from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from studio.agents.compiler import compile_prompt
from studio.assembly.ffmpeg import assemble_videos, probe
from studio.core.approvals import ApprovalLog
from studio.core.gates import evaluate_shot
from studio.core.permission import Permission
from studio.core.registry import AssetRegistry, sha256_file
from studio.providers.mock import MockProvider


class E2ETests(unittest.TestCase):
    def test_mock_project_through_assembly_and_permission_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "product.txt"
            asset.write_text("product", encoding="utf-8")
            reg = AssetRegistry(root / "assets" / "registry.jsonl")
            reg.register(asset_id="product", file_path=asset, asset_kind="product_photo", rights_status="ai_generated")
            contract = {
                "shot_id": "shot_001",
                "narrative_function": "show product",
                "duration_sec": 4,
                "camera": "slow dolly",
                "action": "product opens",
                "audio": {"dialogue": []},
                "references": [{"slot": "@Image1", "asset_id": "product", "role": "product"}],
                "acceptance_criteria": ["clear product"],
                "state": "approved",
            }
            contract_path = root / "contract.json"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            approvals = ApprovalLog(root / "approvals.jsonl")
            approvals.append(gate="G_storyboard", project="p", target="shot_001", target_sha256=sha256_file(contract_path), verdict="approved")
            blocked_permission = Permission({"execute": {"seedance_generate": False}, "budget": {"cap_usd": 20}})
            self.assertEqual(evaluate_shot(contract, reg, approvals, blocked_permission, contract_sha256=sha256_file(contract_path), estimated_cost=1)[-1].status, "manual_required")
            permission = Permission({"execute": {"seedance_generate": True}, "budget": {"cap_usd": 20}})
            self.assertEqual(evaluate_shot(contract, reg, approvals, permission, contract_sha256=sha256_file(contract_path), estimated_cost=1)[-1].status, "pass")
            prompt = compile_prompt(contract, {"project": "Demo"}, reg)
            provider = MockProvider()
            estimate = provider.estimate(prompt=prompt, duration_sec=4)
            self.assertGreater(estimate.cost_usd, 0)
            gen = provider.generate(prompt=prompt, output_dir=root / "takes", duration_sec=4)
            final = assemble_videos([gen.output_path], root / "final.mp4")
            self.assertTrue(final.is_file())
            meta = probe(final)
            self.assertTrue(meta["streams"])


if __name__ == "__main__":
    unittest.main()
