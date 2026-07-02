from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "studio", *args], check=check, capture_output=True, text=True)


class CLITests(unittest.TestCase):
    def test_cli_mock_flow_and_permission_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            run_cli("new", "--root", str(root), "--project", "prj_cli", "--product", "PC")
            run_cli("status", "--root", str(root))
            run_cli("validate", "project", str(root / "project.json"))
            self.assertTrue((root / "permission.json.example").is_file())
            self.assertFalse((root / "permission.json").exists())
            prompt = root / "prompt.txt"
            prompt.write_text("simple mock commercial", encoding="utf-8")
            run_cli("estimate", "--prompt", str(prompt), "--duration", "4")
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
                        "references": [],
                        "acceptance_criteria": ["clear product"],
                        "state": "approved",
                    }
                ),
                encoding="utf-8",
            )
            permission = json.loads((root / "permission.json.example").read_text(encoding="utf-8"))
            (root / "permission.json").write_text(json.dumps(permission), encoding="utf-8")
            run_cli("approve", "--root", str(root), "--project", "prj_cli", "--gate", "G_storyboard", "--target", str(contract), "--name", "shot_001")
            blocked = run_cli("generate", "--root", str(root), "--contract", str(contract), check=False)
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("permission.execute.seedance_generate is not true", blocked.stderr)
            permission["execute"]["seedance_generate"] = True
            (root / "permission.json").write_text(json.dumps(permission), encoding="utf-8")
            generated = run_cli("generate", "--root", str(root), "--contract", str(contract)).stdout.strip()
            self.assertTrue(Path(generated).is_file())
            final = root / "final.mp4"
            run_cli("assemble", "--output", str(final), generated)
            self.assertTrue(final.is_file())
            run_cli("review", "--root", str(root), "--project", "prj_cli", "--take", "take_001", "--file", str(final))

    def test_cli_new_refuses_existing_root_without_touching_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            permission = root / "permission.json"
            permission.write_text("human permission", encoding="utf-8")
            before = permission.read_bytes()
            result = run_cli("new", "--root", str(root), "--project", "prj_cli", "--product", "PC", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(permission.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
