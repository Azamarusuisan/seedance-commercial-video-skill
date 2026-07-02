from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from studio.core.approvals import ApprovalLog
from studio.core.budget import check_budget
from studio.core.contract_validator import validate_contract
from studio.core.jobs import JobQueue, GenerationBlocked, run_generation_from_contract
from studio.core.permission import Permission
from studio.core.registry import AssetRegistry, sha256_file
from studio.providers.base import Estimate, Generation


class CountingProvider:
    provider = "counting"
    model = "counting_mock"

    def __init__(self, cost: float = 0.4):
        self.cost = cost
        self.calls = 0

    def estimate(self, *, prompt: str, duration_sec: float = 0, kind: str = "video") -> Estimate:
        return Estimate(self.provider, self.model, self.cost)

    def generate(self, *, prompt: str, output_dir: Path, duration_sec: float = 1, kind: str = "video") -> Generation:
        self.calls += 1
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / f"counting-{self.calls}.mp4"
        out.write_text(prompt, encoding="utf-8")
        return Generation(self.provider, self.model, f"counting_{self.calls}", out)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _contract() -> dict:
    return {
        "shot_id": "shot_001",
        "narrative_function": "show product",
        "duration_sec": 4,
        "camera": "slow dolly",
        "action": "product opens",
        "audio": {},
        "references": [],
        "acceptance_criteria": ["clear product"],
        "state": "approved",
    }


def _generation_root(root: Path, *, cap_usd: float = 20, daily_cap_usd: float = 10, permission_cap: float = 20) -> Path:
    _write_json(
        root / "project.json",
        {
            "id": "p",
            "type": "short_ad",
            "status": "preproduction",
            "brief": {"product": "p", "target": "t", "platform": ["tiktok"], "duration_sec": 4, "aspect": "9:16", "language": "ja"},
            "budget": {"cap_usd": cap_usd, "daily_cap_usd": daily_cap_usd, "spent_usd": 0, "today_spent_usd": 0, "generations": 0},
            "bible_ref": "bible.json",
            "shots": ["shot_001"],
            "created_at": "now",
            "updated_at": "now",
        },
    )
    _write_json(root / "bible.json", {"project": "Demo", "characters": [], "locations": [], "props": [], "style": {}, "brand": {}})
    _write_json(root / "permission.json", {"execute": {"seedance_generate": True}, "budget": {"cap_usd": permission_cap}})
    (root / "assets" / "registry.jsonl").parent.mkdir(parents=True, exist_ok=True)
    (root / "assets" / "registry.jsonl").touch()
    (root / "approvals.jsonl").touch()
    contract_path = root / "contract.json"
    _write_json(contract_path, _contract())
    return contract_path


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

    def test_generate_requires_storyboard_approval_even_with_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract_path = _generation_root(root)
            with self.assertRaisesRegex(GenerationBlocked, "絵コンテが承認待ちです"):
                run_generation_from_contract(root=root, contract_path=contract_path, provider=CountingProvider())

    def test_generate_blocks_stale_contract_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract_path = _generation_root(root)
            ApprovalLog(root / "approvals.jsonl").append(
                gate="G_storyboard",
                project="p",
                target="shot_001",
                target_sha256=sha256_file(contract_path),
                verdict="approved",
            )
            data = json.loads(contract_path.read_text(encoding="utf-8"))
            data["action"] = "changed product opens"
            _write_json(contract_path, data)
            provider = CountingProvider()
            with self.assertRaisesRegex(GenerationBlocked, "絵コンテが承認待ちです"):
                run_generation_from_contract(root=root, contract_path=contract_path, provider=provider)
            self.assertEqual(provider.calls, 0)

    def test_generate_blocks_invalid_contract_before_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract_path = _generation_root(root)
            asset = root / "previs.txt"
            asset.write_text("previs", encoding="utf-8")
            AssetRegistry(root / "assets" / "registry.jsonl").register(asset_id="blend", file_path=asset, asset_kind="blender_render", rights_status="ai_generated")
            data = json.loads(contract_path.read_text(encoding="utf-8"))
            data["references"] = [{"slot": "@Image1", "asset_id": "blend", "role": "identity"}]
            _write_json(contract_path, data)
            ApprovalLog(root / "approvals.jsonl").append(gate="G_storyboard", project="p", target="shot_001", target_sha256=sha256_file(contract_path), verdict="approved")
            provider = CountingProvider()
            with self.assertRaisesRegex(GenerationBlocked, "blender_render"):
                run_generation_from_contract(root=root, contract_path=contract_path, provider=provider)
            self.assertEqual(provider.calls, 0)

    def test_generate_updates_budget_and_blocks_cap_and_daily(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract_path = _generation_root(root, cap_usd=0.5, daily_cap_usd=10)
            ApprovalLog(root / "approvals.jsonl").append(gate="G_storyboard", project="p", target="shot_001", target_sha256=sha256_file(contract_path), verdict="approved")
            run_generation_from_contract(root=root, contract_path=contract_path, provider=CountingProvider(), take="take_001")
            project = json.loads((root / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(project["budget"]["spent_usd"], 0.4)
            with self.assertRaisesRegex(GenerationBlocked, "project budget exceeded"):
                run_generation_from_contract(root=root, contract_path=contract_path, provider=CountingProvider(), take="take_002")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract_path = _generation_root(root, cap_usd=20, daily_cap_usd=0.5)
            ApprovalLog(root / "approvals.jsonl").append(gate="G_storyboard", project="p", target="shot_001", target_sha256=sha256_file(contract_path), verdict="approved")
            run_generation_from_contract(root=root, contract_path=contract_path, provider=CountingProvider(), take="take_001")
            with self.assertRaisesRegex(GenerationBlocked, "daily budget exceeded"):
                run_generation_from_contract(root=root, contract_path=contract_path, provider=CountingProvider(), take="take_002")

    def test_generate_idempotency_does_not_rerun_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract_path = _generation_root(root)
            ApprovalLog(root / "approvals.jsonl").append(gate="G_storyboard", project="p", target="shot_001", target_sha256=sha256_file(contract_path), verdict="approved")
            provider = CountingProvider()
            first = run_generation_from_contract(root=root, contract_path=contract_path, provider=provider, take="take_001")
            second = run_generation_from_contract(root=root, contract_path=contract_path, provider=provider, take="take_001")
            self.assertEqual(first["output_path"], second["output_path"])
            self.assertTrue(second["idempotent"])
            self.assertEqual(provider.calls, 1)


if __name__ == "__main__":
    unittest.main()
