#!/usr/bin/env python3
"""Append sanitized review learning to the repo learning files.

Default mode writes candidates only. `--apply` may append a known-failure stub.
"""

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / "workspace/learning"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()

    review_path = Path(args.review)
    review = load_json(review_path)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    run_id = review.get("run_id") or review.get("job_id") or f"review-{now}"
    project_id = review.get("project_id", "unknown")
    shot_id = review.get("shot_id", "")
    visual_issue = review.get("visual_issue") or review.get("rejection_reason") or "unspecified"

    memory = {
        "recorded_at": now,
        "run_id": run_id,
        "project_id": project_id,
        "shot_id": shot_id,
        "source_image_kind": review.get("source_image_kind", ""),
        "blender_look_leaked": bool(review.get("blender_look_leaked")),
        "composition_preserved": review.get("composition_preserved", ""),
        "winning_hook": review.get("winning_hook", ""),
        "losing_hook": review.get("losing_hook", ""),
        "prompt_phrase_helped": review.get("prompt_phrase_helped", ""),
        "prompt_phrase_harmed": review.get("prompt_phrase_harmed", ""),
        "visual_issue": visual_issue,
        "motion_issue": review.get("motion_issue", ""),
        "rights_compliance_issue": review.get("rights_compliance_issue", ""),
        "next_instruction": review.get("next_instruction", "update storyboard/key visual before retry"),
    }

    candidate = (
        f"\n## Candidate from {run_id}\n\n"
        f"- project_id: {project_id}\n"
        f"- shot_id: {shot_id}\n"
        f"- visual_issue: {visual_issue}\n"
        f"- next_instruction: {memory['next_instruction']}\n"
    )

    if args.dry_run:
        print(json.dumps(memory, ensure_ascii=False, indent=2))
        print("\n# Failure Candidate Proposal")
        print(candidate)
        return

    (LEARNING / "pattern-memory.jsonl").open("a", encoding="utf-8").write(json.dumps(memory, ensure_ascii=False) + "\n")
    with (LEARNING / "iteration-log.csv").open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            run_id,
            project_id,
            shot_id,
            review.get("status", "reviewed"),
            review.get("source_image_kind", ""),
            bool(review.get("blender_look_leaked")),
            review.get("composition_preserved", ""),
            visual_issue,
            review.get("motion_issue", ""),
            memory["next_instruction"],
        ])

    (LEARNING / "failure-candidates.md").open("a", encoding="utf-8").write(candidate)

    if args.apply:
        (ROOT / "references/known-failure-patterns.md").open("a", encoding="utf-8").write(
            "\n\n## FP-TBD: Review-derived candidate\n" + candidate
        )


if __name__ == "__main__":
    main()
