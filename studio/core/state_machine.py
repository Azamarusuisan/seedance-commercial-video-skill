from __future__ import annotations


PROJECT_TRANSITIONS = {
    "briefing": {"scripting"},
    "scripting": {"preproduction"},
    "preproduction": {"production"},
    "production": {"assembly"},
    "assembly": {"qc"},
    "qc": {"review"},
    "review": {"published", "archived"},
    "published": {"archived"},
    "archived": set(),
}

SHOT_TRANSITIONS = {
    "draft": {"validated"},
    "validated": {"approved"},
    "approved": {"estimating"},
    "estimating": {"authorized"},
    "authorized": {"generating"},
    "generating": {"evaluating"},
    "evaluating": {"needs_retry", "accepted", "rejected"},
    "needs_retry": {"authorized", "rejected"},
    "accepted": set(),
    "rejected": set(),
}


def transition(current: str, new: str, table: dict[str, set[str]]) -> str:
    if new not in table.get(current, set()):
        raise ValueError(f"invalid transition: {current} -> {new}")
    return new


def transition_project(project: dict, new_status: str) -> dict:
    project = dict(project)
    project["status"] = transition(project["status"], new_status, PROJECT_TRANSITIONS)
    return project


def transition_shot(contract: dict, new_state: str) -> dict:
    contract = dict(contract)
    contract["state"] = transition(contract["state"], new_state, SHOT_TRANSITIONS)
    return contract
