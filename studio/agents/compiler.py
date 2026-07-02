from __future__ import annotations

from studio.core.contract_validator import validate_contract
from studio.core.registry import AssetRegistry


NEGATIVE_DEFAULTS = "No watermark, no subtitles, no captions, no unreadable text, no unsafe claims."


def compile_prompt(contract: dict, bible: dict, registry: AssetRegistry) -> str:
    report = validate_contract(contract, registry)
    if not report.ok:
        raise ValueError("; ".join(report.blocked))
    lines = [
        f"Project: {bible.get('project', 'Studio video')}",
        f"Shot: {contract['shot_id']}",
        f"Function: {contract['narrative_function']}",
        f"Duration: {contract['duration_sec']} seconds",
        f"Camera: {contract['camera']}",
        f"Action: {contract['action']}",
        "References:",
    ]
    for ref in contract.get("references", [])[:12]:
        record = registry.get(ref["asset_id"]) or {}
        lines.append(f"- {ref['slot']} role={ref['role']} asset={record.get('path', ref['asset_id'])}")
    lines.extend(["Acceptance criteria:"])
    lines.extend(f"- {item}" for item in contract.get("acceptance_criteria", []))
    lines.append(f"Negative: {NEGATIVE_DEFAULTS}")
    return "\n".join(lines)
