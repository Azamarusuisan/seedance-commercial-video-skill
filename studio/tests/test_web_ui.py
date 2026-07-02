from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from studio.ui.web.server import api_approve, api_create_project, api_generate, api_register_asset, api_review, api_status


class WebUiTests(unittest.TestCase):
    def test_web_api_flow_uses_core_ledgers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            api_create_project({"root": str(root), "project": "web", "product": "PC", "target": "creators", "platform": "tiktok"})
            photo = root / "photo.txt"
            photo.write_text("photo", encoding="utf-8")
            registered = api_register_asset({"root": str(root), "asset_id": "photo_001", "path": str(photo), "asset_kind": "product_photo", "rights_status": "ai_generated"})
            self.assertEqual(registered["asset"]["asset_id"], "photo_001")
            target = root / "storyboard.txt"
            target.write_text("storyboard", encoding="utf-8")
            event = api_approve({"root": str(root), "project": "web", "target_file": str(target), "target_name": "shot_001"})["event"]
            self.assertEqual(event["verdict"], "approved")
            blocked = api_generate({"root": str(root), "prompt": "mock"})
            self.assertIn("blocked", blocked)
            permission = json.loads((root / "permission.json").read_text(encoding="utf-8"))
            permission["execute"]["seedance_generate"] = True
            (root / "permission.json").write_text(json.dumps(permission), encoding="utf-8")
            generated = api_generate({"root": str(root), "prompt": "mock", "duration": 4})
            self.assertTrue(Path(generated["output_path"]).is_file())
            api_review({"root": str(root), "project": "web", "take": "take_001", "file": generated["output_path"], "verdict": "approved"})
            status = api_status(root)
            self.assertEqual(status["memory"]["generations"], 1)
            self.assertTrue(status["approvals"])
            self.assertEqual(status["assets"][0]["asset_id"], "photo_001")

    def test_web_ui_does_not_directly_dump_state(self):
        result = subprocess.run(["rg", "state.*write|json.dump", "studio/ui/web/"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
