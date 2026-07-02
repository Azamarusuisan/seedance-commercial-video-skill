from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PermissionResult:
    allowed: bool
    reason: str


class Permission:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    @classmethod
    def load(cls, path: str | Path) -> "Permission":
        p = Path(path)
        if not p.is_file():
            return cls({})
        return cls(json.loads(p.read_text(encoding="utf-8")))

    def can_execute(self, action: str, *, estimated_cost: float = 0.0, spent_usd: float = 0.0) -> PermissionResult:
        execute = self.data.get("execute")
        if not isinstance(execute, dict):
            return PermissionResult(False, "permission.execute is missing")
        if execute.get(action) is not True:
            return PermissionResult(False, f"permission.execute.{action} is not true")
        budget = self.data.get("budget")
        if not isinstance(budget, dict):
            return PermissionResult(False, "permission.budget is missing")
        cap = budget.get("cap_usd")
        if not isinstance(cap, (int, float)):
            return PermissionResult(False, "permission.budget.cap_usd is missing")
        if spent_usd + estimated_cost > cap:
            return PermissionResult(False, f"budget cap exceeded: {spent_usd + estimated_cost} > {cap}")
        return PermissionResult(True, "allowed")
