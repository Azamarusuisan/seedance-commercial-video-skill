from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from studio.core.approvals import ApprovalLog
from studio.core.permission import Permission
from studio.core.registry import AssetRegistry


@dataclass(frozen=True)
class GateResult:
    gate: str
    status: str
    reason: str


def _blocked(gate: str, reason: str) -> GateResult:
    return GateResult(gate, "blocked", reason)


def _passed(gate: str, reason: str = "passed") -> GateResult:
    return GateResult(gate, "pass", reason)


def _manual(gate: str, reason: str) -> GateResult:
    return GateResult(gate, "manual_required", reason)


def evaluate_project(project: dict[str, Any], approvals: ApprovalLog | None = None) -> list[GateResult]:
    results: list[GateResult] = []
    brief = project.get("brief", {})
    if not all(brief.get(key) for key in ["product", "target", "platform", "duration_sec", "aspect", "language"]):
        return [_blocked("G_brief", "ブリーフが未確定です")]
    results.append(_passed("G_brief"))
    if approvals and not approvals.is_approved(gate="G_final", target=project.get("id", "")):
        results.append(_manual("G_final", "最終確認が未実施です"))
    results.append(_manual("G_publish", "公開は本システムの外で人間が行います"))
    return results


def evaluate_shot(
    contract: dict[str, Any],
    registry: AssetRegistry,
    approvals: ApprovalLog,
    permission: Permission,
    *,
    contract_sha256: str,
    estimated_cost: float = 0.0,
    spent_usd: float = 0.0,
) -> list[GateResult]:
    results: list[GateResult] = []
    for ref in contract.get("references", []):
        record = registry.get(ref.get("asset_id", ""))
        if not record:
            return [_blocked("G_assets", "未登録の参照素材があります")]
        if not registry.verify_sha(record["asset_id"]):
            return [_blocked("G_assets", f"素材のsha256が一致しません: {record['asset_id']}")]
        if record.get("rights_status") == "unknown" or record.get("real_face"):
            return [_blocked("G_rights", f"権利不明/実在顔の素材は使えません: {record['asset_id']}")]
    results.extend([_passed("G_assets"), _passed("G_rights")])
    if not approvals.is_approved(gate="G_storyboard", target=contract.get("shot_id", ""), target_sha256=contract_sha256):
        results.append(_manual("G_storyboard", "絵コンテが承認待ちです"))
        return results
    results.append(_passed("G_storyboard"))
    if estimated_cost <= 0:
        results.append(_blocked("G_estimate", "見積未実施/予算超過"))
        return results
    results.append(_passed("G_estimate"))
    allowed = permission.can_execute("seedance_generate", estimated_cost=estimated_cost, spent_usd=spent_usd)
    if not allowed.allowed:
        results.append(_manual("G_authorize", f"最終生成許可がありません: {allowed.reason}"))
        return results
    results.append(_passed("G_authorize"))
    return results
