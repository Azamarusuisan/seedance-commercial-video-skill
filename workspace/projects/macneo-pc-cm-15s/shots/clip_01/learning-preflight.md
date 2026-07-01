# Learning Preflight — macneo-pc-cm-15s / clip_01

can_prepare_seedance_request: false
dry_run: true

## Applicable Known Failure Patterns
- FP-001: Blender blockout direct-to-Seedance risk
- FP-002: product/person collage risk
- FP-003: graphic light nouns risk

## Blocked Risks
- missing approved photoreal key visual
- primary image role is not visual_truth
- primary image is not approved
- seedance_input_allowed is not true
- rights_status is missing or unknown
- generated storyboard/contact sheet is missing

## Prompt Changes Required
- Use Blender only as composition/camera guide.
- Use photoreal material and photographic light language.
- Keep exact text, subtitles, CTA, and claims for post-production.

## Demand Pattern To Reuse
- Build storyboard panels or a 15s beat sheet before generation.

## Preserve
- composition, camera angle, object placement, scale, shot continuity

## Avoid
- Blender cheap-CG look, collage references, drawn rings/lines/dots, unapproved text

## Sources Read
- known_failure_patterns: True
- prompt_rules: True
- pattern_memory: True
- demand_patterns: True
- project_brief: True
- project_state: workspace/projects/macneo-pc-cm-15s/project-state.json
- seedance_prompt: missing
- visual_handoff: missing
- asset_manifest: missing
