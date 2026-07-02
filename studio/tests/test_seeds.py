from __future__ import annotations

from pathlib import Path
import unittest

from studio.memory.seeds import SEED_DIR, active_items, load_seed
from studio.schemas.validate import validate_document


class SeedTests(unittest.TestCase):
    def test_all_seed_files_have_source_and_status(self):
        for path in sorted(SEED_DIR.glob("*.json")):
            data = load_seed(path.stem)
            validate_document(data, "seed")
            self.assertTrue(data["items"], path.name)
            for item in data["items"]:
                self.assertIn(item["status"], {"active", "candidate"})
                self.assertTrue(item["source"])

    def test_failure_patterns_001_to_008_are_seeded(self):
        ids = {item.get("fp_id") for item in active_items("prompt_rules")}
        self.assertTrue({f"FP-{i:03d}" for i in range(1, 9)} <= ids)

    def test_candidate_entries_are_distinct(self):
        luxury = load_seed("look_luxury")["items"]
        self.assertTrue(any(item["status"] == "candidate" for item in luxury))
        for item in luxury:
            if item["status"] == "candidate":
                self.assertEqual(item.get("origin"), "claude_generated_candidate")

    def test_seed_source_paths_exist(self):
        root = Path.cwd()
        for path in sorted(SEED_DIR.glob("*.json")):
            data = load_seed(path.stem)
            for item in data["items"]:
                for source in str(item["source"]).split(";"):
                    source_path = source.strip().split("#", 1)[0].strip()
                    if "/" not in source_path and not source_path.endswith((".md", ".json")):
                        continue
                    self.assertTrue((root / source_path).exists(), f"{path.name}:{item['id']} source missing: {source_path}")


if __name__ == "__main__":
    unittest.main()
