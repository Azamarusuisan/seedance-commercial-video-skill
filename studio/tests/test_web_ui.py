from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from studio.ui.web.server import api_approve, api_create_project, api_generate, api_register_asset, api_review, api_status


class WebUiTests(unittest.TestCase):
    def test_web_api_flow_uses_core_ledgers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            api_create_project({"root": str(root), "project": "web", "product": "PC", "target": "creators", "platform": "tiktok"})
            self.assertTrue((root / "permission.json.example").is_file())
            photo = root / "photo.txt"
            photo.write_text("photo", encoding="utf-8")
            registered = api_register_asset({"root": str(root), "asset_id": "photo_001", "path": str(photo), "asset_kind": "product_photo", "rights_status": "ai_generated"})
            self.assertEqual(registered["asset"]["asset_id"], "photo_001")
            contract = root / "contract.json"
            contract.write_text(
                json.dumps(
                    {
                        "shot_id": "shot_001",
                        "narrative_function": "show product",
                        "duration_sec": 4,
                        "camera": "slow dolly",
                        "action": "product opens",
                        "audio": {},
                        "references": [{"slot": "@Image1", "asset_id": "photo_001", "role": "product"}],
                        "acceptance_criteria": ["clear product"],
                        "state": "approved",
                    }
                ),
                encoding="utf-8",
            )
            blocked = api_generate({"root": str(root), "contract": str(contract)})
            self.assertIn("blocked", blocked)
            permission = json.loads((root / "permission.json.example").read_text(encoding="utf-8"))
            permission["execute"]["seedance_generate"] = True
            (root / "permission.json").write_text(json.dumps(permission), encoding="utf-8")
            still_blocked = api_generate({"root": str(root), "contract": str(contract)})
            self.assertIn("絵コンテが承認待ちです", still_blocked["blocked"])
            event = api_approve({"root": str(root), "project": "web", "target_file": str(contract), "target_name": "shot_001"})["event"]
            self.assertEqual(event["verdict"], "approved")
            generated = api_generate({"root": str(root), "contract": str(contract)})
            self.assertTrue(Path(generated["output_path"]).is_file())
            api_review({"root": str(root), "project": "web", "take": "take_001", "file": generated["output_path"], "verdict": "approved"})
            status = api_status(root)
            self.assertEqual(status["memory"]["generations"], 1)
            self.assertTrue(status["approvals"])
            self.assertEqual(status["assets"][0]["asset_id"], "photo_001")

    def test_web_ui_does_not_directly_dump_state(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in Path("studio/ui/web").glob("*.py"))
        self.assertNotIn("json.dump", text)
        self.assertNotIn("state.write", text)

    def test_web_create_project_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            api_create_project({"root": str(root), "project": "web", "product": "PC", "target": "creators", "platform": "tiktok"})
            result = api_create_project({"root": str(root), "project": "web", "product": "PC", "target": "creators", "platform": "tiktok"})
            self.assertIn("blocked", result)


if __name__ == "__main__":
    unittest.main()
