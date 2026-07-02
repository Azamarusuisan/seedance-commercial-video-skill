from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BudgetDecision:
    allowed: bool
    level: str
    reason: str


def check_budget(*, cap_usd: float, daily_cap_usd: float, spent_usd: float, today_spent_usd: float, estimate_usd: float) -> BudgetDecision:
    projected = spent_usd + estimate_usd
    today_projected = today_spent_usd + estimate_usd
    if projected > cap_usd:
        return BudgetDecision(False, "blocked", f"project budget exceeded: {projected} > {cap_usd}")
    if today_projected > daily_cap_usd:
        return BudgetDecision(False, "blocked", f"daily budget exceeded: {today_projected} > {daily_cap_usd}")
    if cap_usd and projected >= cap_usd * 0.8:
        return BudgetDecision(True, "warn", "project budget is above 80%")
    return BudgetDecision(True, "ok", "budget available")
