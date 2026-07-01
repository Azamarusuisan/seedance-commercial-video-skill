#!/usr/bin/env python3
"""Creates the visual-handoff record + storyboard prompt scaffold for a shot, from Blender
previs. Never runs generation. See workspace/schemas/visual-handoff.schema.json and
references/known-failure-patterns.md FP-001."""

import argparse
import datetime
import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = REPO_ROOT / "workspace/prompts/templates/gpt-image-from-blender-previs.txt"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--blend-path", default="")
    parser.add_argument("--render-path", default="")
    parser.add_argument("--camera-notes", default="")
    parser.add_argument("--placement-notes", default="")
    parser.add_argument("--scale-notes", default="")
    parser.add_argument("--motion-intent", default="")
    args = parser.parse_args()

    shot_dir = REPO_ROOT / "workspace/projects" / args.project_id / "shots" / args.shot_id
    shot_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = shot_dir / "gpt-image-storyboard-prompt.txt"
    if TEMPLATE_PATH.is_file():
        shutil.copyfile(TEMPLATE_PATH, prompt_path)
    else:
        prompt_path.write_text("Status: proposal.\n", encoding="utf-8")

    handoff = {
        "project_id": args.project_id,
        "shot_id": args.shot_id,
        "blender_role": "composition_only",
        "blender_source": {
            "blend_path": args.blend_path,
            "render_path": args.render_path,
            "camera_notes": args.camera_notes,
            "placement_notes": args.placement_notes,
            "scale_notes": args.scale_notes,
            "motion_intent": args.motion_intent,
        },
        "storyboard_prompt_path": str(prompt_path.relative_to(REPO_ROOT)),
        "storyboard_status": "prompt_prepared",
        "storyboard_image_path": "",
        "seedance_primary_image_allowed": False,
        "block_reason": "写実キービジュアル未生成・未承認のため、Seedanceの主参照にはまだ使えません。",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    handoff_path = shot_dir / "visual-handoff.json"
    handoff_path.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {handoff_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {prompt_path.relative_to(REPO_ROOT)}")
    print("No paid generation was executed. Blender role is fixed to composition_only.")


if __name__ == "__main__":
    main()
