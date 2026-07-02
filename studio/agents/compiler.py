from __future__ import annotations

from studio.core.contract_validator import validate_contract
from studio.core.registry import AssetRegistry
from studio.memory.seeds import active_items, candidate_items


def _negative_defaults() -> str:
    for rule in active_items("prompt_rules"):
        if rule.get("id") == "negative_defaults":
            return rule["negative"]
    raise FileNotFoundError("negative_defaults missing from prompt_rules seed")


def draft_short_ad_contract(*, shot_id: str = "shot_001", duration_sec: float = 15.0) -> dict:
    template = next(item for item in active_items("cm_structure") if item["id"] == "product_ad_15s")
    return {
        "shot_id": shot_id,
        "narrative_function": " / ".join(f"{beat['time']} {beat['name']}" for beat in template["beats"]),
        "duration_sec": duration_sec,
        "camera": template["beats"][0]["camera_default"],
        "action": "show product transformation and final hero memory",
        "audio": {},
        "references": [],
        "acceptance_criteria": [f"{beat['time']}: {beat['purpose']}" for beat in template["beats"]],
        "state": "draft",
    }


def compile_prompt(contract: dict, bible: dict, registry: AssetRegistry) -> str:
    report = validate_contract(contract, registry)
    if not report.ok:
        raise ValueError("; ".join(report.blocked))
    camera_terms = ", ".join(item["phrase"] for item in active_items("camera_playbook")[:5])
    look_terms = ", ".join(token for item in active_items("look_luxury") for token in item.get("tokens", [])[:2])
    candidates = ", ".join(item["id"] for item in candidate_items("look_luxury")) or "none"
    lines = [
        f"Project: {bible.get('project', 'Studio video')}",
        f"Shot: {contract['shot_id']}",
        f"Function: {contract['narrative_function']}",
        f"Duration: {contract['duration_sec']} seconds",
        f"CM structure: first two seconds must contain a silent visual hook.",
        f"Camera vocabulary: {camera_terms}",
        f"Look vocabulary: {look_terms}",
        f"Candidate vocabulary not used: {candidates}",
        f"Camera: {contract['camera']}",
        f"Action: {contract['action']}",
        "References:",
    ]
    for ref in contract.get("references", [])[:12]:
        record = registry.get(ref["asset_id"]) or {}
        lines.append(f"- {ref['slot']} role={ref['role']} asset={record.get('path', ref['asset_id'])}")
    lines.extend(["Acceptance criteria:"])
    lines.extend(f"- {item}" for item in contract.get("acceptance_criteria", []))
    lines.append(f"Negative: {_negative_defaults()}")
    return "\n".join(lines)
