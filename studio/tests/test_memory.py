from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from studio.memory.import_v1 import import_project
from studio.memory.production_memory import ProductionMemory


class MemoryTests(unittest.TestCase):
    def test_memory_import_is_idempotent_and_loads_fp_001_to_008(self):
        with tempfile.TemporaryDirectory() as tmp:
            mem = ProductionMemory(Path(tmp) / "memory.sqlite")
            before = Path("references/known-failure-patterns.md").read_bytes()
            import_project("workspace/projects/lipstick-cm-30s", mem)
            import_project("workspace/projects/lipstick-cm-30s", mem)
            self.assertEqual(before, Path("references/known-failure-patterns.md").read_bytes())
            self.assertTrue({f"FP-{i:03d}" for i in range(1, 9)} <= mem.failure_ids())
            self.assertGreaterEqual(mem.counts()["playbooks"], 5)
            self.assertGreater(mem.counts()["generations"], 0)

    def test_review_can_record_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            mem = ProductionMemory(Path(tmp) / "memory.sqlite")
            mem.record_generation(project="p", take="t1", verdict="rejected", failure_tag="cheap_vfx", cost_usd=1.5)
            mem.record_generation(project="p", take="t1", verdict="approved", failure_tag="", cost_usd=1.5)
            self.assertEqual(mem.counts()["generations"], 1)


if __name__ == "__main__":
    unittest.main()
