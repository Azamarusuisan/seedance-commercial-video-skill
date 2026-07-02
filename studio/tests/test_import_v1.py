from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from studio.core.registry import sha256_file
from studio.memory.import_v1 import import_project
from studio.memory.production_memory import ProductionMemory


class ImportV1Tests(unittest.TestCase):
    def test_import_v1_fixture_copy_is_idempotent_and_read_only(self):
        source = Path("workspace/projects/lipstick-cm-30s")
        known = Path("references/known-failure-patterns.md")
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "lipstick-cm-30s"
            shutil.copytree(source, fixture)
            before_project = {str(path.relative_to(fixture)): sha256_file(path) for path in fixture.rglob("*") if path.is_file()}
            before_known = sha256_file(known)
            mem = ProductionMemory(Path(tmp) / "memory.sqlite")
            first = import_project(fixture, mem)
            second = import_project(fixture, mem)
            after_project = {str(path.relative_to(fixture)): sha256_file(path) for path in fixture.rglob("*") if path.is_file()}
            self.assertEqual(before_project, after_project)
            self.assertEqual(before_known, sha256_file(known))
            self.assertEqual(first["project_files"], second["project_files"])
            self.assertTrue({f"FP-{i:03d}" for i in range(1, 9)} <= mem.failure_ids())
            self.assertGreater(mem.counts()["generations"], 0)


if __name__ == "__main__":
    unittest.main()
