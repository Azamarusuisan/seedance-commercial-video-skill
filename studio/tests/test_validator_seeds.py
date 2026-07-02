from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio.core.contract_validator import validate_contract
from studio.core.registry import AssetRegistry
from studio.memory.seeds import SEED_DIR


def _contract() -> dict:
    return {
        "shot_id": "shot_001",
        "narrative_function": "hook",
        "duration_sec": 4,
        "camera": "wide electric arcs",
        "action": "product opens",
        "audio": {},
        "references": [{"slot": "@Image1", "asset_id": "product", "role": "product"}],
        "acceptance_criteria": ["clear product"],
        "state": "approved",
    }


class ValidatorSeedTests(unittest.TestCase):
    def test_active_rule_warns_with_fp_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "asset.txt"
            asset.write_text("x", encoding="utf-8")
            reg = AssetRegistry(Path(tmp) / "assets" / "registry.jsonl")
            reg.register(asset_id="product", file_path=asset, asset_kind="product_photo", rights_status="ai_generated")
            report = validate_contract(_contract(), reg)
            self.assertTrue(any("FP-003" in item for item in report.warnings))

    def test_candidate_warns_only_and_active_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            seed_dir = Path(tmp) / "seeds"
            shutil.copytree(SEED_DIR, seed_dir)
            rules = json.loads((seed_dir / "prompt_rules.json").read_text(encoding="utf-8"))
            rules["items"].append({"id": "candidate_bad", "status": "candidate", "source": "test", "severity": "block", "trigger_terms": ["product opens"], "message": "candidate"})
            (seed_dir / "prompt_rules.json").write_text(json.dumps(rules), encoding="utf-8")
            asset = Path(tmp) / "asset.txt"
            asset.write_text("x", encoding="utf-8")
            reg = AssetRegistry(Path(tmp) / "assets" / "registry.jsonl")
            reg.register(asset_id="product", file_path=asset, asset_kind="product_photo", rights_status="ai_generated")
            with patch.dict(os.environ, {"STUDIO_SEED_DIR": str(seed_dir)}):
                report = validate_contract(_contract(), reg)
            self.assertTrue(report.ok)
            self.assertTrue(any("candidate:candidate_bad" in item for item in report.warnings))
            rules["items"][-1]["status"] = "active"
            (seed_dir / "prompt_rules.json").write_text(json.dumps(rules), encoding="utf-8")
            with patch.dict(os.environ, {"STUDIO_SEED_DIR": str(seed_dir)}):
                report = validate_contract(_contract(), reg)
            self.assertFalse(report.ok)
            self.assertTrue(any("candidate_bad" in item for item in report.blocked))

    def test_missing_seed_blocks_validator(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "asset.txt"
            asset.write_text("x", encoding="utf-8")
            reg = AssetRegistry(Path(tmp) / "assets" / "registry.jsonl")
            reg.register(asset_id="product", file_path=asset, asset_kind="product_photo", rights_status="ai_generated")
            with patch.dict(os.environ, {"STUDIO_SEED_DIR": str(Path(tmp) / "missing")}):
                report = validate_contract(_contract(), reg)
            self.assertFalse(report.ok)
            self.assertIn("seed missing", report.blocked[0])


if __name__ == "__main__":
    unittest.main()
