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
            prompt = root / "prompt.txt"
            prompt.write_text("simple mock commercial", encoding="utf-8")
            run_cli("estimate", "--prompt", str(prompt), "--duration", "4")
            blocked = run_cli("generate", "--root", str(root), "--prompt", str(prompt), "--duration", "4", check=False)
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("blocked:", blocked.stderr)
            permission = json.loads((root / "permission.json").read_text(encoding="utf-8"))
            permission["execute"]["seedance_generate"] = True
            (root / "permission.json").write_text(json.dumps(permission), encoding="utf-8")
            generated = run_cli("generate", "--root", str(root), "--prompt", str(prompt), "--duration", "4").stdout.strip()
            self.assertTrue(Path(generated).is_file())
            final = root / "final.mp4"
            run_cli("assemble", "--output", str(final), generated)
            self.assertTrue(final.is_file())
            run_cli("review", "--root", str(root), "--project", "prj_cli", "--take", "take_001", "--file", str(final))


if __name__ == "__main__":
    unittest.main()
