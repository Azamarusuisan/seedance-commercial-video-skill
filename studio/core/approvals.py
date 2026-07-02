from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ApprovalLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def append(
        self,
        *,
        gate: str,
        project: str,
        target: str,
        target_sha256: str,
        verdict: str,
        by: str = "human",
        note: str = "",
    ) -> dict[str, Any]:
        if verdict not in {"approved", "rejected", "revoked"}:
            raise ValueError(f"invalid verdict: {verdict}")
        event = {
            "at": datetime.now(UTC).isoformat(),
            "gate": gate,
            "project": project,
            "target": target,
            "target_sha256": target_sha256,
            "verdict": verdict,
            "by": by,
            "note": note,
            "event_id": f"apv_{uuid.uuid4().hex[:12]}",
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        return event

    def events(self) -> list[dict[str, Any]]:
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def latest(self, *, gate: str, target: str) -> dict[str, Any] | None:
        for event in reversed(self.events()):
            if event.get("gate") == gate and event.get("target") == target:
                return event
        return None

    def is_approved(self, *, gate: str, target: str, target_sha256: str | None = None) -> bool:
        event = self.latest(gate=gate, target=target)
        if not event or event.get("verdict") != "approved":
            return False
        return target_sha256 is None or event.get("target_sha256") == target_sha256
