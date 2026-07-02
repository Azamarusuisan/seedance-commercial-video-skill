from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from studio.agents.compiler import compile_prompt, draft_short_ad_contract, normalize_camera_action
from studio.core.registry import AssetRegistry


class CompilerSeedTests(unittest.TestCase):
    def test_draft_short_ad_has_hook_beat(self):
        draft = draft_short_ad_contract()
        self.assertIn("0-2s hook", draft["narrative_function"])
        for name in ("problem", "demo", "afterglow", "cta"):
            self.assertIn(name, draft["narrative_function"])
        self.assertTrue(any(item.startswith("0-2s") for item in draft["acceptance_criteria"]))

    def test_draft_short_ad_uses_platform_structure(self):
        draft = draft_short_ad_contract(platform="ugc")
        self.assertIn("ugc_15s", draft["narrative_function"])

    def test_camera_is_normalized_to_playbook_phrase(self):
        camera, action = normalize_camera_action("dolly toward product", "open lid")
        self.assertEqual(camera, "slow dolly-in")
        self.assertEqual(action, "open lid")

    def test_compiler_includes_active_seed_rules_and_not_candidate_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "product.txt"
            asset.write_text("x", encoding="utf-8")
            reg = AssetRegistry(root / "assets" / "registry.jsonl")
            reg.register(asset_id="product", file_path=asset, asset_kind="product_photo", rights_status="ai_generated")
            contract = draft_short_ad_contract(duration_sec=4)
            contract.update(
                {
                    "state": "approved",
                    "references": [{"slot": "@Image1", "asset_id": "product", "role": "product"}],
                    "camera": "slow dolly-in",
                    "action": "product opens",
                }
            )
            prompt = compile_prompt(contract, {"project": "Demo"}, reg)
            self.assertIn("first two seconds", prompt)
            self.assertIn("macro push-in", prompt)
            self.assertIn("No watermark", prompt)
            self.assertIn("Candidate vocabulary not used: teal_orange_check", prompt)
            self.assertNotIn("restrained color contrast", prompt)


if __name__ == "__main__":
    unittest.main()
