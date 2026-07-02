from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Callable, Generic, TypeVar

from studio.agents.compiler import compile_prompt
from studio.core.approvals import ApprovalLog
from studio.core.budget import check_budget
from studio.core.gates import evaluate_shot
from studio.core.permission import Permission
from studio.core.registry import AssetRegistry, sha256_file
from studio.memory.seeds import active_items
from studio.providers.base import Generation, Provider
from studio.providers.seedance import execution_token

T = TypeVar("T")


@dataclass
class JobResult(Generic[T]):
    idempotency_key: str
    value: T


class JobQueue:
    def __init__(self, *, max_retries_per_failure: int = 2):
        self._results: dict[str, JobResult] = {}
        self._failure_counts: dict[str, int] = {}
        self.max_retries_per_failure = max_retries_per_failure

    def run_once(self, idempotency_key: str, fn: Callable[[], T]) -> JobResult[T]:
        if idempotency_key in self._results:
            return self._results[idempotency_key]
        result = JobResult(idempotency_key, fn())
        self._results[idempotency_key] = result
        return result

    def record_failure(self, tag: str) -> bool:
        count = self._failure_counts.get(tag, 0) + 1
        self._failure_counts[tag] = count
        return count < self.max_retries_per_failure

    def retry_plan(self, tag: str) -> tuple[bool, str]:
        recipe = next((item["recipe"] for item in active_items("retry_playbook") if item["id"] == tag), "")
        if not recipe:
            return False, f"failure_tag '{tag}' has no retry playbook"
        if not self.record_failure(tag):
            return False, f"failure_tag '{tag}' repeated; stop for human review"
        return True, recipe

    def retry_prompt(self, prompt: str, tag: str) -> tuple[bool, str, str]:
        should_retry, recipe = self.retry_plan(tag)
        if not should_retry:
            return False, prompt, recipe
        diff = f"Retry adjustment for {tag}: {recipe}"
        return True, f"{prompt}\n{diff}", diff


class GenerationBlocked(RuntimeError):
    pass


def _read_json(path: Path) -> dict:
    if not path.is_file():
        raise GenerationBlocked(f"missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _existing_take(meta_path: Path) -> dict | None:
    if not meta_path.is_file():
        return None
    data = _read_json(meta_path)
    if data.get("status") == "prepared" and Path(data.get("request_path", "")).is_file():
        return data
    output = Path(data.get("output_path", ""))
    return data if output.is_file() else None


def _today() -> str:
    return date.today().isoformat()


def _budget_for_today(project: dict) -> dict:
    budget = dict(project.get("budget", {}))
    today = _today()
    if budget.get("today_date") != today:
        budget["today_date"] = today
        budget["today_spent_usd"] = 0
    project["budget"] = budget
    return budget


def _charge_budget(project: dict, cost: float) -> None:
    budget = _budget_for_today(project)
    budget["spent_usd"] = round(float(budget.get("spent_usd", 0)) + cost, 6)
    budget["today_spent_usd"] = round(float(budget.get("today_spent_usd", 0)) + cost, 6)
    budget["generations"] = int(budget.get("generations", 0)) + 1
    project["budget"] = budget
    project["updated_at"] = datetime.now(UTC).isoformat()


def _contract_references(contract: dict, registry: AssetRegistry) -> list[dict]:
    resolved = []
    for ref in contract.get("references", []):
        record = registry.get(ref["asset_id"]) or {}
        resolved.append(
            {
                "slot": ref["slot"],
                "role": ref["role"],
                "path": record.get("path", ref["asset_id"]),
                "sha256": record.get("sha256", ""),
            }
        )
    return resolved


def run_generation_from_contract(*, root: Path, contract_path: Path, provider: Provider, take: str = "take_001") -> dict:
    root = root.resolve()
    contract_path = contract_path.resolve()
    project_path = root / "project.json"
    project = _read_json(project_path)
    bible = _read_json(root / project.get("bible_ref", "bible.json"))
    contract = _read_json(contract_path)
    registry = AssetRegistry(root / "assets" / "registry.jsonl")
    approvals = ApprovalLog(root / "approvals.jsonl")
    permission = Permission.load(root / "permission.json")
    contract_sha = sha256_file(contract_path)

    try:
        prompt = compile_prompt(contract, bible, registry)
    except ValueError as exc:
        raise GenerationBlocked(str(exc)) from exc

    duration = float(contract.get("duration_sec", 0))
    try:
        estimate = provider.estimate(prompt=prompt, duration_sec=duration)
    except RuntimeError as exc:
        raise GenerationBlocked(str(exc)) from exc
    budget = _budget_for_today(project)
    spent_usd = float(budget.get("spent_usd", 0))
    today_spent_usd = float(budget.get("today_spent_usd", 0))

    gates = evaluate_shot(
        contract,
        registry,
        approvals,
        permission,
        contract_sha256=contract_sha,
        estimated_cost=estimate.cost_usd,
        spent_usd=spent_usd,
    )
    failed = [gate for gate in gates if gate.status != "pass"]
    if failed:
        raise GenerationBlocked("; ".join(gate.reason for gate in failed))

    budget_decision = check_budget(
        cap_usd=float(budget.get("cap_usd", 0)),
        daily_cap_usd=float(budget.get("daily_cap_usd", 0)),
        spent_usd=spent_usd,
        today_spent_usd=today_spent_usd,
        estimate_usd=estimate.cost_usd,
    )
    if not budget_decision.allowed:
        raise GenerationBlocked(budget_decision.reason)

    shot_id = contract["shot_id"]
    prompt_sha = _hash_text(prompt)
    idempotency_key = f"{project['id']}:{shot_id}:{contract_sha}:{take}"
    meta_path = root / "takes" / f"{shot_id}-{contract_sha[:12]}-{take}.json"
    existing = _existing_take(meta_path)
    if existing:
        existing["idempotent"] = True
        return existing

    if getattr(provider, "mode", "") == "prepare":
        request_path = provider.prepare(
            prompt=prompt,
            contract=contract,
            output_dir=root / "requests",
            meta={
                "project": project["id"],
                "shot_id": shot_id,
                "take": take,
                "contract_sha256": contract_sha,
                "prompt_sha256": prompt_sha,
                "estimate_cost": estimate.cost_usd,
                "aspect": project.get("brief", {}).get("aspect", "9:16"),
                "references": _contract_references(contract, registry),
            },
        )
        record = {
            "status": "prepared",
            "project": project["id"],
            "shot_id": shot_id,
            "take": take,
            "request_path": str(request_path),
            "execution_token": _read_json(request_path)["execution_token"],
            "contract_sha256": contract_sha,
            "prompt_sha256": prompt_sha,
            "cost_usd": estimate.cost_usd,
            "idempotency_key": idempotency_key,
            "created_at": datetime.now(UTC).isoformat(),
        }
        _write_json(meta_path, record)
        with (root / "takes" / "takes.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        _write_json(project_path, project)
        return record

    queue = JobQueue()
    result = queue.run_once(idempotency_key, lambda: provider.generate(prompt=prompt, output_dir=root / "takes", duration_sec=duration)).value
    record = _take_record(
        project=project["id"],
        shot_id=shot_id,
        take=take,
        contract_sha=contract_sha,
        prompt_sha=prompt_sha,
        estimate_cost=estimate.cost_usd,
        idempotency_key=idempotency_key,
        generation=result,
    )
    _write_json(meta_path, record)
    with (root / "takes" / "takes.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    _charge_budget(project, estimate.cost_usd)
    _write_json(project_path, project)
    return record


def record_generation_result(*, root: Path, request_path: Path, output_path: Path, cost_usd: float | None = None, response_path: Path | None = None) -> dict:
    root = root.resolve()
    request_path = request_path.resolve()
    output_path = output_path.resolve()
    request = _read_json(request_path)
    take = request["take"]
    contract_sha = request["contract_sha256"]
    shot_id = request["shot_id"]
    meta_path = root / "takes" / f"{shot_id}-{contract_sha[:12]}-{take}.json"
    existing = _existing_take(meta_path)
    if existing and existing.get("status") == "recorded":
        existing["idempotent"] = True
        return existing
    expected = request.get("execution_token")
    if not expected or execution_token(request) != expected:
        raise GenerationBlocked("request改竄またはtoken無し。MCP実行はtoken付きrequestのみ")
    if not output_path.is_file():
        raise GenerationBlocked(f"missing output: {output_path}")

    project_path = root / "project.json"
    project = _read_json(project_path)
    actual_cost = float(cost_usd if cost_usd is not None else request.get("estimate", {}).get("cost_usd", 0))
    permission = Permission.load(root / "permission.json")
    unauthorized = permission.data.get("execute", {}).get("seedance_generate") is not True
    response_copy = ""
    if response_path:
        response_dir = root / "responses"
        response_dir.mkdir(parents=True, exist_ok=True)
        response_copy = str(response_dir / response_path.name)
        Path(response_copy).write_bytes(response_path.read_bytes())

    record = {
        "status": "recorded",
        "project": request["project"],
        "shot_id": shot_id,
        "take": take,
        "request_path": str(request_path),
        "execution_token": expected,
        "contract_sha256": contract_sha,
        "prompt_sha256": request["prompt_sha256"],
        "cost_usd": actual_cost,
        "actual_cost_usd": actual_cost,
        "output_path": str(output_path),
        "output_sha256": sha256_file(output_path),
        "provider": request.get("estimate", {}).get("provider", ""),
        "model": request.get("estimate", {}).get("model", ""),
        "executed_by": "human_mcp",
        "unauthorized": unauthorized,
        "response_path": response_copy,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _write_json(meta_path, record)
    with (root / "takes" / "takes.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    request["status"] = "recorded"
    request["recorded_at"] = datetime.now(UTC).isoformat()
    _write_json(request_path, request)
    _charge_budget(project, actual_cost)
    _write_json(project_path, project)
    return record


def _take_record(
    *,
    project: str,
    shot_id: str,
    take: str,
    contract_sha: str,
    prompt_sha: str,
    estimate_cost: float,
    idempotency_key: str,
    generation: Generation,
) -> dict:
    return {
        "project": project,
        "shot_id": shot_id,
        "take": take,
        "contract_sha256": contract_sha,
        "prompt_sha256": prompt_sha,
        "cost_usd": estimate_cost,
        "idempotency_key": idempotency_key,
        "provider": generation.provider,
        "model": generation.model,
        "provider_job_id": generation.job_id,
        "output_path": str(generation.output_path),
        "created_at": datetime.now(UTC).isoformat(),
    }
