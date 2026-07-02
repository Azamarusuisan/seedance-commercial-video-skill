from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from studio.core.approvals import ApprovalLog
from studio.core.jobs import GenerationBlocked
from studio.core.permission import Permission
from studio.core.registry import sha256_file
from studio.providers.seedance import execution_token


def _read_json(path: Path) -> dict:
    if not path.is_file():
        raise GenerationBlocked(f"missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_palmier_request(*, root: Path, inputs: list[Path], instruction: str = "") -> dict:
    root = root.resolve()
    project = _read_json(root / "project.json")
    permission = Permission.load(root / "permission.json")
    allowed = permission.can_execute("palmier_edit")
    if not allowed.allowed:
        raise GenerationBlocked(allowed.reason)
    approvals = ApprovalLog(root / "approvals.jsonl")
    rows = []
    for item in inputs:
        path = item.resolve()
        digest = sha256_file(path)
        target = path.stem
        if not approvals.is_approved(gate="G_take", target=target, target_sha256=digest):
            raise GenerationBlocked(f"take is not approved for Palmier edit: {target}")
        rows.append({"path": str(path), "sha256": digest, "target": target})
    seed = hashlib.sha256(json.dumps(rows, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    request = {
        "schema_version": "mcp_request.v1",
        "kind": "palmier_edit",
        "project": project["id"],
        "inputs": rows,
        "instruction": instruction,
        "created_at": datetime.now(UTC).isoformat(),
        "status": "prepared",
        "mcp_hint": {"tool": "palmier", "note": "人間がPalmierで編集/書き出しし、export-recordへ"},
    }
    request["execution_token"] = execution_token(request)
    path = root / "requests" / f"palmier-{seed}.request.json"
    if not path.exists():
        _write_json(path, request)
    return {"request_path": str(path), "execution_token": request["execution_token"]}


def record_palmier_export(*, root: Path, request_path: Path, output_path: Path) -> dict:
    root = root.resolve()
    request = _read_json(request_path.resolve())
    expected = request.get("execution_token")
    if request.get("kind") != "palmier_edit" or not expected or execution_token(request) != expected:
        raise GenerationBlocked("Palmier request改竄またはtoken無し")
    output = output_path.resolve()
    if not output.is_file():
        raise GenerationBlocked(f"missing output: {output}")
    permission = Permission.load(root / "permission.json")
    unauthorized = permission.data.get("execute", {}).get("palmier_export") is not True
    record = {
        "kind": "palmier_export",
        "project": request["project"],
        "request_path": str(request_path),
        "execution_token": expected,
        "output_path": str(output),
        "output_sha256": sha256_file(output),
        "unauthorized": unauthorized,
        "created_at": datetime.now(UTC).isoformat(),
    }
    out = root / "exports" / f"{output.stem}.json"
    _write_json(out, record)
    return record
