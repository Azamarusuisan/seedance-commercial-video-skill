from __future__ import annotations

import unittest

from studio.schemas.validate import SchemaError, validate_document


class SchemaTests(unittest.TestCase):
    def test_project_schema_accepts_plan_example_shape(self):
        validate_document(
            {
                "id": "prj_1",
                "type": "short_ad",
                "status": "briefing",
                "brief": {"product": "PC", "target": "creator", "platform": ["tiktok"], "duration_sec": 15, "aspect": "9:16", "language": "ja"},
                "budget": {"cap_usd": 20, "daily_cap_usd": 10, "spent_usd": 0, "generations": 0},
                "audio_policy": {},
                "bible_ref": "bible.json",
                "shots": ["shot_001"],
                "timeline": "timeline.json",
                "created_at": "now",
                "updated_at": "now",
            },
            "project",
        )

    def test_missing_required_key_fails(self):
        with self.assertRaises(SchemaError):
            validate_document({"id": "bad"}, "project")

    def test_invalid_state_fails(self):
        with self.assertRaises(SchemaError):
            validate_document(
                {
                    "shot_id": "shot_001",
                    "narrative_function": "hook",
                    "duration_sec": 8,
                    "camera": "wide",
                    "action": "run",
                    "audio": {},
                    "references": [],
                    "acceptance_criteria": [],
                    "state": "paid_generation_now",
                },
                "shot_contract",
            )


if __name__ == "__main__":
    unittest.main()
