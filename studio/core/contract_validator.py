from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from studio.core.registry import AssetRegistry
from studio.schemas.validate import SchemaError, validate_document


LIGHT_SHAPES = ("arc", "arcs", "bolt", "bolts", "spark", "sparks", "beam", "beams", "ray", "rays", "streak", "orb")
LIGHT_CONTEXT = ("electric", "light", "glow", "neon", "laser", "energy")


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
                report.blocked.append(f"blender_render cannot be role={role}: {asset_id}")
            if role == "composition" and ref.get("experimental") is not True:
                report.blocked.append(f"blender composition reference requires experimental=true: {asset_id}")
    text = f"{contract.get('camera', '')} {contract.get('action', '')}".lower()
    if any(shape in text for shape in LIGHT_SHAPES) and any(ctx in text for ctx in LIGHT_CONTEXT):
        report.warnings.append("図形的エフェクト語が含まれます。撮影語彙に置換できないか確認してください。")
    if any(word in text for word in ("subtitle", "caption", "readable text", "exact text", "テロップ", "字幕")):
        report.warnings.append("正確な文字表示はポスプロで焼く前提にしてください。")
    return report
