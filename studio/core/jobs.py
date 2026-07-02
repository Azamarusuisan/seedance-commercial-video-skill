from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
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
    output = Path(data.get("output_path", ""))
    return data if output.is_file() else None


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
    estimate = provider.estimate(prompt=prompt, duration_sec=duration)
    budget = project.get("budget", {})
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

    budget["spent_usd"] = round(spent_usd + estimate.cost_usd, 6)
    budget["today_spent_usd"] = round(today_spent_usd + estimate.cost_usd, 6)
    budget["generations"] = int(budget.get("generations", 0)) + 1
    project["budget"] = budget
    project["updated_at"] = datetime.now(UTC).isoformat()
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
