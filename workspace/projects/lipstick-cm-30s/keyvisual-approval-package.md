# Key Visual Approval Package — Lipstick CM Retry

Status: awaiting user approval. Do not run any image generation until the user explicitly approves
model, source references, output paths, and total estimated cost below.

## What will be generated (4 images)

| # | File (prompt) | Tool (primary) | Source image(s) | Output |
|---|---|---|---|---|
| 1 | `clip_01_start_key.txt` | `higgsfield-image.sh` | `lipstick_cm_panel_01_silhouette.png` (1 image) | `workspace/assets/references/lipstick-cm/clip_01_start_key.png` |
| 2 | `clip_01_end_key.txt` | `higgsfield-image.sh` | `lipstick_cm_panel_03_hero_vfx.png` (1 image) | `workspace/assets/references/lipstick-cm/clip_01_end_key.png` |
| 3 | `clip_02_lips_key.txt` | `higgsfield-image.sh` | `clip_01_end_key.png` (output of #2) + `rina_hayun_lips_closeup.png` (2 images, roles specified) | `workspace/assets/references/lipstick-cm/clip_02_lips_key.png` |
| 4 | `clip_02_final_key.txt` | `higgsfield-image.sh` | `lipstick_cm_panel_04_negative_space_tag.png` (1 image) | `workspace/assets/references/lipstick-cm/clip_02_final_key.png` |

**Order matters: #2 must complete before #3** (its output is one of #3's two input images).

## Model / route

- Primary: Higgsfield MCP image generation (`workspace/scripts/higgsfield-image.sh`, model placeholder `image2`). Per CLAUDE.md, this is preferred over a raw `OPENAI_API_KEY` route.
- Fallback (only if Higgsfield MCP image generation is unavailable, and only with explicit user go-ahead): `workspace/scripts/gpt-image-reference.sh` (`gpt-image-2`, requires `OPENAI_API_KEY` in the shell).
- **Unverified**: the real Higgsfield MCP model name/id behind `image2`, and whether it truly supports multi-image input the way this package assumes for #3. Confirm via a `higgsfield-status.sh`-style `model_get` request before running #3, per `references/known-failure-patterns.md` (FP-004).

## Cost

**Unknown from this session** — no Higgsfield MCP connection here to run a real cost check, and no confirmed per-image credit cost for Higgsfield's image model. Before running any of the 4:

1. Run `bash workspace/scripts/higgsfield-status.sh` (or equivalent model_get for the image model) to learn the actual credit cost per image.
2. Report the real number back to the user for explicit approval.
3. If Higgsfield's image cost is unknown or too high, ask the user whether to approve the `gpt-image-reference.sh` fallback instead (different cost profile, requires `OPENAI_API_KEY`).

**Do not treat this package's approval as generation approval.** Cost must be confirmed separately, per CLAUDE.md's Safety/Cost Gate.

## What happens after these 4 are generated

1. Show all 4 alongside the original Blender panels (`lipstick_cm_panel_01..04*.png`, `lipstick_cm_previs.png`) for side-by-side comparison.
2. User approves or requests changes. No Seedance cost estimate or generation happens before this approval.
3. Once approved, the 4 key visuals become the `start_image`/`end_image` inputs for the Clip 1 / Clip 2 Seedance regeneration — never the raw Blender renders.

## Known-failure-patterns checked against this package

- FP-001 (raw Blender as start_image): avoided — Blender renders are inputs to image generation only, never directly to Seedance.
- FP-002 (product+lips composite): avoided — #3 uses two separate images with explicit roles, not a pre-flattened composite.
- FP-003 (graphic-noun light language): avoided — all 4 prompts use photographic vocabulary only.
- FP-004 (single-image scripts hiding real multi-image support): addressed — `higgsfield-image.sh` and `gpt-image-reference.sh` now both support multiple source images; #3 uses this directly instead of a manual composite.
