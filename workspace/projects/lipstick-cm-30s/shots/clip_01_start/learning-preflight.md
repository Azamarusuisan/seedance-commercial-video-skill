# Learning Preflight — lipstick-cm-30s / clip_01_start

can_prepare_seedance_request: false
dry_run: true

## Applicable Known Failure Patterns
- FP-001: Blender blockout direct-to-Seedance risk
- FP-002: product/person collage risk
- FP-003: graphic light nouns risk

## Blocked Risks
- primary image is not approved
- seedance_input_allowed is not true

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
- seedance_prompt: missing
- visual_handoff: workspace/projects/lipstick-cm-30s/shots/clip_01_start/visual-handoff.json
- asset_manifest: workspace/projects/lipstick-cm-30s/shots/clip_01_start/asset-manifest.json
