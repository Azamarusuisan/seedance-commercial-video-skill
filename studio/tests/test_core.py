from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from studio.core.approvals import ApprovalLog
from studio.core.budget import check_budget
from studio.core.contract_validator import validate_contract
from studio.core.jobs import JobQueue
from studio.core.permission import Permission
from studio.core.registry import AssetRegistry, sha256_file


class CoreTests(unittest.TestCase):
    def test_registry_blocks_unknown_rights_and_real_faces(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "asset.txt"
            asset.write_text("x", encoding="utf-8")
            reg = AssetRegistry(Path(tmp) / "registry.jsonl")
            unknown = reg.register(asset_id="a1", file_path=asset, asset_kind="product_photo", rights_status="unknown")
            face = reg.register(asset_id="a2", file_path=asset, asset_kind="generated_charsheet", rights_status="ai_generated", real_face=True)
            self.assertFalse(unknown["seedance_upload_allowed"])
            self.assertFalse(face["seedance_upload_allowed"])
            self.assertTrue(reg.verify_sha("a1"))
            asset.write_text("changed", encoding="utf-8")
            self.assertFalse(reg.verify_sha("a1"))

    def test_approvals_are_append_only_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = ApprovalLog(Path(tmp) / "approvals.jsonl")
            log.append(gate="G_storyboard", project="p", target="shot_1", target_sha256="abc", verdict="approved")
            self.assertTrue(log.is_approved(gate="G_storyboard", target="shot_1", target_sha256="abc"))
            log.append(gate="G_storyboard", project="p", target="shot_1", target_sha256="abc", verdict="revoked")
            self.assertFalse(log.is_approved(gate="G_storyboard", target="shot_1", target_sha256="abc"))

    def test_permission_fails_closed(self):
        self.assertFalse(Permission({}).can_execute("seedance_generate").allowed)
        self.assertFalse(Permission({"execute": {"seedance_generate": False}, "budget": {"cap_usd": 1}}).can_execute("seedance_generate").allowed)
        allowed = Permission({"execute": {"seedance_generate": True}, "budget": {"cap_usd": 2}}).can_execute("seedance_generate", estimated_cost=1)
        self.assertTrue(allowed.allowed)

    def test_contract_validator_blocks_blender_identity_and_warns_effect_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "previs.png"
            asset.write_text("fake", encoding="utf-8")
            reg = AssetRegistry(Path(tmp) / "registry.jsonl")
            reg.register(asset_id="blend", file_path=asset, asset_kind="blender_render", rights_status="ai_generated")
            contract = {
                "shot_id": "shot_001",
                "narrative_function": "hook",
                "duration_sec": 8,
                "camera": "wide electric arcs",
                "action": "product opens",
                "audio": {},
                "references": [{"slot": "@Image1", "asset_id": "blend", "role": "identity"}],
                "acceptance_criteria": ["clear product"],
                "state": "approved",
            }
            report = validate_contract(contract, reg)
            self.assertFalse(report.ok)
            self.assertTrue(any("blender_render" in item for item in report.blocked))
            self.assertTrue(report.warnings)
            contract["references"][0] = {"slot": "@Image1", "asset_id": "blend", "role": "composition", "experimental": True}
            self.assertTrue(validate_contract(contract, reg).ok)

    def test_budget_and_idempotency(self):
        self.assertFalse(check_budget(cap_usd=1, daily_cap_usd=10, spent_usd=0.8, today_spent_usd=0, estimate_usd=0.3).allowed)
        q = JobQueue()
        calls = {"n": 0}

        def work():
            calls["n"] += 1
            return "ok"

        self.assertEqual(q.run_once("same", work).value, "ok")
        self.assertEqual(q.run_once("same", work).value, "ok")
        self.assertEqual(calls["n"], 1)
        self.assertTrue(q.record_failure("face_drift"))
        self.assertFalse(q.record_failure("face_drift"))


if __name__ == "__main__":
    unittest.main()
