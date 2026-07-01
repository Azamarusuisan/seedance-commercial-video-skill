#!/usr/bin/env python3
"""Create a generic Blender-previs -> photoreal-storyboard handoff.

This writes files only. It never runs image or video generation.
"""

import argparse
import datetime
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = REPO_ROOT / "workspace/prompts/templates/gpt-image-from-blender-previs.txt"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--route", default="light", choices=["light", "heavy"])
    parser.add_argument("--blend-path", default="")
    parser.add_argument("--render-path", default="")
    parser.add_argument("--asset-kind", default="blender_previs")
    parser.add_argument("--aspect-ratio", default="9:16")
    parser.add_argument("--platform", default="internal_review")
    parser.add_argument("--visual-style", default="photoreal commercial storyboard")
    parser.add_argument("--lighting", default="premium photographic lighting")
    parser.add_argument("--materials", default="photoreal materials with realistic reflections")
    parser.add_argument("--mood", default="cinematic commercial mood")
    parser.add_argument("--camera-notes", default="")
    parser.add_argument("--lens-feel", default="")
    parser.add_argument("--framing", default="")
    parser.add_argument("--placement-notes", default="")
    parser.add_argument("--scale-notes", default="")
    parser.add_argument("--motion-intent", default="")
    args = parser.parse_args()

    shot_dir = REPO_ROOT / "workspace/projects" / args.project_id / "shots" / args.shot_id
    shot_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = shot_dir / "gpt-image-storyboard-prompt.txt"
    template = TEMPLATE_PATH.read_text(encoding="utf-8") if TEMPLATE_PATH.is_file() else ""
    composition_truth = {
        "camera_angle": args.camera_notes,
        "lens_feel": args.lens_feel,
        "framing": args.framing,
        "subject_positions": [args.placement_notes] if args.placement_notes else [],
        "spatial_relationships": [args.scale_notes] if args.scale_notes else [],
        "motion_intent": args.motion_intent,
    }
    prompt = template
    prompt = prompt.replace("{blender_render_path(s)}", args.render_path or "(describe Blender composition in text)")
    prompt = prompt.replace("{project_specific_avoid_list}", "project-specific unsafe claims, private data, unsupported logos, and unapproved text")
    prompt += (
        "\n\nProject:\n"
        f"{args.project_id}\n\n"
        "Shot:\n"
        f"{args.shot_id}\n\n"
        "Composition truth to preserve:\n"
        f"{json.dumps(composition_truth, ensure_ascii=False, indent=2)}\n\n"
        "Visual style:\n"
        f"{args.visual_style}\n\n"
        "Lighting:\n"
        f"{args.lighting}\n\n"
        "Material / product realism:\n"
        f"{args.materials}\n"
    )
    prompt_path.write_text(prompt, encoding="utf-8")

    handoff = {
        "schema_version": "visual_handoff.v1",
        "project_id": args.project_id,
        "shot_id": args.shot_id,
        "route": args.route,
        "source": {
            "asset_path": args.render_path,
            "asset_kind": args.asset_kind,
            "role": "composition_only",
            "seedance_input_allowed": False,
        },
        "composition_truth": composition_truth,
        "do_preserve_from_blender": [
            "composition",
            "camera angle",
            "object placement",
            "scale relationship",
            "shot continuity",
            "negative space",
        ],
        "do_not_preserve_from_blender": [
            "low-poly look",
            "viewport lighting",
            "temporary materials",
            "flat shader",
            "gray background",
            "cheap CG preview look",
            "drawn rings",
            "floating dots",
            "graphic line overlays",
        ],
        "storyboard_goal": {
            "visual_style": args.visual_style,
            "lighting": args.lighting,
            "materials": args.materials,
            "mood": args.mood,
            "platform": args.platform,
            "aspect_ratio": args.aspect_ratio,
        },
        "output": {
            "prompt_path": str(prompt_path.relative_to(REPO_ROOT)),
            "storyboard_image_path": str((shot_dir / "storyboard.png").relative_to(REPO_ROOT)),
            "asset_kind": "photoreal_key_visual",
            "role": "visual_truth",
            "approval_status": "pending",
            "seedance_input_allowed": False,
        },
        # Backward-compatible keys used by prepare-storyboard-image-request.sh and UI.
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
