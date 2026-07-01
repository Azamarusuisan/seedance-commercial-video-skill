#!/usr/bin/env python3
"""Write a learning preflight report before Seedance request preparation.

This is intentionally conservative: missing approved photoreal key visuals block.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-id", required=True)
    p.add_argument("--shot-id", required=True)
    p.add_argument("--visual-handoff", default="")
    p.add_argument("--prompt-file", default="")
    p.add_argument("--asset-manifest", default="")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    shot_dir = ROOT / "workspace/projects" / args.project_id / "shots" / args.shot_id
    shot_dir.mkdir(parents=True, exist_ok=True)

    handoff_path = Path(args.visual_handoff) if args.visual_handoff else shot_dir / "visual-handoff.json"
    manifest_path = Path(args.asset_manifest) if args.asset_manifest else shot_dir / "asset-manifest.json"
    prompt_path = Path(args.prompt_file) if args.prompt_file else shot_dir / "seedance_prompt.txt"
    project_brief_path = ROOT / "workspace/projects" / args.project_id / "brief.md"
    project_state_path = ROOT / "workspace/projects" / args.project_id / "project-state.json"
    fallback_brief_path = ROOT / "workspace/briefs" / f"{args.project_id}-script.md"

    handoff = json.loads(read(handoff_path) or "{}")
    manifest = json.loads(read(manifest_path) or "{}")
    project_state = json.loads(read(project_state_path) or "{}")
    prompt = read(prompt_path)

    known = read(ROOT / "references/known-failure-patterns.md")
    rules = read(ROOT / "workspace/learning/prompt-rules.md")
    memory = read(ROOT / "workspace/learning/pattern-memory.jsonl")
    demand = read(ROOT / "references/public-demand-short-video-patterns.md")
    brief = read(project_brief_path) or read(fallback_brief_path)

    risks = []
    if "FP-001" in known:
        risks.append("FP-001: Blender blockout direct-to-Seedance risk")
    if "FP-002" in known:
        risks.append("FP-002: product/person collage risk")
    if "FP-003" in known:
        risks.append("FP-003: graphic light nouns risk")

    reasons = []
    if manifest.get("asset_kind") not in {"photoreal_key_visual", "approved_storyboard_frame", "rights_confirmed_user_asset", "approved_product_reference"}:
        reasons.append("missing approved photoreal key visual")
    if manifest.get("role") != "visual_truth":
        reasons.append("primary image role is not visual_truth")
    if manifest.get("approval_status") != "approved":
        reasons.append("primary image is not approved")
    if manifest.get("seedance_input_allowed") is not True:
        reasons.append("seedance_input_allowed is not true")
    if manifest.get("rights_status") == "unknown" or not manifest.get("rights_status"):
        reasons.append("rights_status is missing or unknown")
    if handoff.get("source", {}).get("role") == "composition_only" and not handoff.get("output", {}).get("storyboard_image_path"):
        reasons.append("visual handoff still points only to Blender composition source")
    if any(word in prompt.lower() for word in [" ring", " rings", "particle", "particles", "line overlay", "dots"]):
        reasons.append("prompt may contain graphic light nouns; use photographic language")
    script = project_state.get("script", {}) if isinstance(project_state, dict) else {}
    beats = script.get("beats", []) if isinstance(script, dict) else []
    cast_policy = project_state.get("cast_policy", {}) if isinstance(project_state, dict) else {}
    audio_post = project_state.get("audio_post", {}) if isinstance(project_state, dict) else {}
    if project_state:
        storyboard = project_state.get("storyboard", {}) if isinstance(project_state.get("storyboard"), dict) else {}
        requires_storyboard = storyboard.get("required") is not False
        has_generated_storyboard = bool(storyboard.get("generated_contact_sheet") or storyboard.get("approved_storyboard_frame"))
        if requires_storyboard and not has_generated_storyboard:
            reasons.append("generated storyboard/contact sheet is missing")
        if storyboard.get("status") in {"blocked_missing_generated_storyboard", "reference_board_only"}:
            reasons.append("storyboard status blocks Seedance preparation")
        if not beats:
            reasons.append("script beat sheet / storyboard timing is missing")
        if beats and any(not beat.get("visual") for beat in beats if isinstance(beat, dict)):
            reasons.append("one or more script beats are missing visual direction")
        if not script.get("dialogue_policy"):
            reasons.append("dialogue/no-dialogue policy is missing")
        if not script.get("telop_plan") and not any((beat.get("telop") or beat.get("caption")) for beat in beats if isinstance(beat, dict)):
            reasons.append("Japanese subtitle/telop plan is missing")
        if not cast_policy.get("decision") and not cast_policy.get("selected_cast"):
            reasons.append("cast/no-cast decision is missing")
        if not audio_post.get("status"):
            reasons.append("audio/BGM/SFX policy is missing")

    can_prepare = not reasons
    report = [
        f"# Learning Preflight — {args.project_id} / {args.shot_id}",
        "",
        f"can_prepare_seedance_request: {'true' if can_prepare else 'false'}",
        f"dry_run: {'true' if args.dry_run else 'false'}",
        "",
        "## Applicable Known Failure Patterns",
        *[f"- {item}" for item in risks],
        "",
        "## Blocked Risks",
        *([f"- {item}" for item in reasons] or ["- none"]),
        "",
        "## Prompt Changes Required",
        "- Use Blender only as composition/camera guide.",
        "- Use photoreal material and photographic light language.",
        "- Keep exact text, subtitles, CTA, and claims for post-production.",
        "",
        "## Demand Pattern To Reuse",
        "- Build storyboard panels or a 15s beat sheet before generation.",
        "",
        "## Preserve",
        "- composition, camera angle, object placement, scale, shot continuity",
        "",
        "## Avoid",
        "- Blender cheap-CG look, collage references, drawn rings/lines/dots, unapproved text",
        "",
        "## Sources Read",
        f"- known_failure_patterns: {bool(known)}",
        f"- prompt_rules: {bool(rules)}",
        f"- pattern_memory: {bool(memory)}",
        f"- demand_patterns: {bool(demand)}",
        f"- project_brief: {bool(brief)}",
        f"- project_state: {rel(project_state_path) if project_state_path.exists() else 'missing'}",
        f"- seedance_prompt: {rel(prompt_path) if prompt_path.exists() else 'missing'}",
        f"- visual_handoff: {rel(handoff_path) if handoff_path.exists() else 'missing'}",
        f"- asset_manifest: {rel(manifest_path) if manifest_path.exists() else 'missing'}",
    ]
    out = shot_dir / "learning-preflight.md"
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(out.relative_to(ROOT))
    if not can_prepare:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
