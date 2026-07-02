from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from studio.core.registry import AssetRegistry
from studio.memory.seeds import active_items, candidate_items
from studio.schemas.validate import SchemaError, validate_document


@dataclass
class ValidationReport:
    blocked: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.blocked


def validate_contract(contract: dict[str, Any], registry: AssetRegistry) -> ValidationReport:
    report = ValidationReport()
    try:
        active_rules = active_items("prompt_rules")
        candidate_rules = candidate_items("prompt_rules")
    except FileNotFoundError as exc:
        report.blocked.append(f"prompt rule seed missing: {exc}")
        return report
    try:
        validate_document(contract, "shot_contract")
    except SchemaError as exc:
        report.blocked.append(str(exc))
        return report
    if not 4 <= float(contract.get("duration_sec", 0)) <= 15:
        report.blocked.append("duration_sec must be 4-15 seconds")
    refs = contract.get("references", [])
    if len(refs) > 12:
        report.blocked.append("too many references; maximum is 12")
    for ref in refs:
        asset_id = ref["asset_id"]
        role = ref["role"]
        record = registry.get(asset_id)
        if not record:
            report.blocked.append(f"asset not registered: {asset_id}")
            continue
        if not record.get("seedance_upload_allowed"):
            report.blocked.append(f"asset is not allowed for Seedance upload: {asset_id}")
        if record.get("real_face"):
            report.blocked.append(f"real-face asset is forbidden: {asset_id}")
        if record.get("rights_status") == "unknown":
            report.blocked.append(f"unknown-rights asset is forbidden: {asset_id}")
        if record.get("asset_kind") == "blender_render":
            if role not in {"composition", "motion"}:
                report.blocked.append(f"FP-001: blender_render cannot be role={role}: {asset_id}")
            if role == "composition" and ref.get("experimental") is not True:
                report.blocked.append(f"FP-001: blender composition reference requires experimental=true: {asset_id}")
        path = str(record.get("path", "")).lower()
        for rule in active_rules:
            if rule.get("severity") != "block":
                continue
            if any(term.lower() in path for term in rule.get("trigger_terms", [])):
                report.blocked.append(f"{rule.get('fp_id', rule['id'])}: {rule.get('message', 'blocked')}")
    text = f"{contract.get('camera', '')} {contract.get('action', '')}".lower()
    for rule in active_rules:
        terms = [term.lower() for term in rule.get("trigger_terms", [])]
        if not terms or not any(term in text for term in terms):
            continue
        context_terms = [term.lower() for term in rule.get("context_terms", [])]
        if context_terms and not any(term in text for term in context_terms):
            continue
        label = rule.get("fp_id", rule["id"])
        message = rule.get("message", "確認してください。")
        if rule.get("severity") == "block":
            report.blocked.append(f"{label}: {message}")
        elif rule.get("severity") == "warn":
            report.warnings.append(f"{label}: {message}")
    for rule in candidate_rules:
        terms = [term.lower() for term in rule.get("trigger_terms", [])]
        if terms and any(term in text for term in terms):
            report.warnings.append(f"candidate:{rule['id']}: {rule.get('message', '未承認候補です')}")
    return report
