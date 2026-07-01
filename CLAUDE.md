# Claude Code Instructions

Follow `AGENTS.md`, `WORKFLOW.md`, and `workspace/agent-guides/cross-agent-runbook.md`.

## Current Critical Context

The active project is:

`workspace/projects/lipstick-cm-30s/`

Before doing any work on it, read these files in full:

- `CODEX.md`
- `references/known-failure-patterns.md`
- `workspace/projects/lipstick-cm-30s/postmortem-20260701-blender-fleshout-mismatch.md`
- `workspace/projects/lipstick-cm-30s/review-20260701-seedance-failed.md`
- `workspace/projects/lipstick-cm-30s/seedance-conditions.md`
- `workspace/briefs/lipstick-cm-30s-script.md`
- `WORKFLOW.md`

## Current Claude Assignment

Do not generate anything yet. The user explicitly stopped generation.

First task is to repair the workflow understanding and implementation gaps before any new paid job:

1. Explain and fix why only one reference image was used.
   - Root cause: `workspace/scripts/seedance-cost.sh` and `workspace/scripts/seedance-generate.sh` currently pass only one `image=` argument.
   - This forced Clip 2 into `workspace/assets/references/lipstick-cm/clip_02_product_plus_rina_lips_clean.png`, a single combined product+lips reference.
   - That is not acceptable for the next attempt. Do not collapse product, Blender structure, and Rina lips into one image unless the downstream tool truly has no multi-reference path.

2. Treat Rina Hayun correctly.
   - Rina Hayun is a fictional AI-generated cast reference.
   - Use only `workspace/assets/cast/generated_20260629/rina_hayun_lips_closeup.png`.
   - Use it only as lips/skin-tone reference for Clip 2.
   - No full face, no hand-held product, no influencer/customer/testimonial framing.

3. Restore the missing storyboard/key-visual step.
   - Blender panels are structure/storyboard references.
   - They are not acceptable final Seedance start frames for high-brand photoreal work.
   - Before Seedance, create photoreal key visuals from the Blender storyboard and show them beside the source Blender panels.
   - The user must approve those key visuals before any Seedance estimate or Seedance generation.

4. Keep audio, subtitles, and Palmier editing blocked until the visual material passes review.
   - The failed MP4s are review/training material only.
   - Do not add BGM, SFX, narration, subtitles, color, upscale, or export to failed clips.
   - After a future visual pass is approved, then prepare BGM/SFX, narration/subtitle policy, and Palmier Pro edit/finish as a separate approval step.

5. Update project docs/UI state only with sanitized information.
   - Do not commit `workspace/logs/`.
   - Do not include tokens, cookies, credentials, raw session files, or private account details.
   - Failed images/videos and sanitized learning notes are allowed when they explain the workflow failure.

## Work Order For Claude

Follow this order exactly:

1. Pull latest and inspect local dirty files. Do not overwrite unrelated user/Codex changes.
2. Confirm the current stop state in project docs and UI state: `generation_blocked`, `keyvisual_review_required`, `no_seedance_before_keyvisual_approval`.
3. Inspect the actual Higgsfield/Seedance media schema if available, without running generation. Determine whether `seedance_2_0` supports `start_image`, `end_image`, repeated `--image`, or other multi-reference inputs.
4. Patch the smallest necessary script/doc gap so future runs do not silently use only one reference image. If the model truly supports only one image, document that limitation and make the one-image fallback explicit.
5. Prepare the key-visual approval package only. Do not execute paid image generation until the user approves the model, source references, output paths, and total estimated credits.
6. After user approval, generate the 4 photoreal key visuals, make a side-by-side board with original Blender panels, and stop again for user review.
7. Only after key-visual approval, prepare Seedance cost/generation conditions.
8. Only after Seedance visual approval, proceed to BGM/SFX, narration/subtitles, and Palmier Pro finishing.

## Non-Negotiable Correction

The previous Seedance run failed because the raw Blender render was passed directly as Seedance `start_image`.

Do not repeat that.

For high-brand photoreal CM work:

- Blender is a structure/design reference only.
- Blender defines composition, camera, product proportions, timing, and motion intent.
- Blender blockout renders must not be used directly as final Seedance start frames.
- Create realistic key visuals first, show them to the user, and get approval before any paid video generation.

## Current Stop State

The generated Seedance clips are rejected and committed for review because the user explicitly asked to keep them in Git as learning material:

- `workspace/outputs/lipstick-cm-30s/clip_01_9x16.mp4`
- `workspace/outputs/lipstick-cm-30s/clip_02_9x16.mp4`

Treat them as failed review material, not assets for finishing.

Do not send them to Palmier Pro.
Do not add music, SFX, subtitles, color, or export.
Do not run another paid Seedance job.

## Required Next Work

Next work is not video generation and not image generation until the user approves the image generation conditions.

Next work is to prepare the approval package for photoreal key visuals derived from the Blender storyboard:

- Clip 1 start key: luxury lipstick macro, dark premium studio, no visible blockout planes.
- Clip 1 end key: photoreal product hero shot, black lacquer tube, champagne-gold metal, deep red bullet.
- Clip 2 lips key: anonymous luxury lips close-up, integrated beauty campaign lighting, no full face, no pasted collage look.
- Clip 2 final key: product/lips world resolves into a premium final brand frame.

Once generated with explicit approval, show the key visuals beside the original Blender panels. The user must approve them before any new Seedance estimate or generation.

### Status (Claude Code, this session — revised)

Looked directly at the failed contact sheets (`workspace/outputs/lipstick-cm-30s/review_frames/clip_0{1,2}_contact.jpg`) and found a **second failure mode the postmortem had not caught**: the "orbit light rings / floating particles" prompt language rendered as literal white line/dot graphic overlays (a motion-graphics-template look), not photographic light. Logged as `FP-003` in the new **`references/known-failure-patterns.md`** — a durable, cross-project failure-pattern registry (the practical, non-ML-retraining version of a "feedback loop": accumulate root causes here, and every future Seedance generation must check this file first). FP-001 (raw Blender as start_image) and FP-002 (product+lips composite) are also logged there from the existing postmortem.

Rewrote all 4 key-visual prompts to fix FP-003 (photographic light vocabulary only — bokeh/glints/haze — no "ring/particle/line/dot" as drawn shapes) and to explicitly route through `workspace/scripts/gpt-image-reference.sh` in edit mode (`GPT_IMAGE_SOURCE_IMAGE=<blender render>`), per user direction:

- `workspace/prompts/lipstick-cm/keyvisuals/clip_01_start_key.txt`
- `workspace/prompts/lipstick-cm/keyvisuals/clip_01_end_key.txt`
- `workspace/prompts/lipstick-cm/keyvisuals/clip_02_lips_key.txt`
- `workspace/prompts/lipstick-cm/keyvisuals/clip_02_final_key.txt`

Each still carries a `Status: proposal` pending marker. **Not executed yet.** Do not use `OPENAI_API_KEY` as a default route for this project. Prefer the Higgsfield-authenticated GPT Image 2 / image workflow when available, but only after explicit user approval. Show the generated results beside the original Blender panels, and get user approval before any new Seedance cost estimate or generation. `WORKFLOW.md` §7-8 now requires checking `references/known-failure-patterns.md` before every future Seedance generation, not just this project's.

## Safety / Cost Gate

Paid generation is blocked until the user explicitly approves:

- model
- count
- duration
- resolution
- bitrate
- references
- output paths
- total credits

Do not treat cost approval as generation approval.
Do not run paid jobs because a previous generation was already approved; the failed review reset the gate.

## Git / Asset Policy

- Commit and push useful documentation, prompts, and approved reference images.
- Do not commit credentials, cookies, tokens, or session files.
- Heavy failed MP4s are normally not committed. This lipstick CM exception is intentional because the user explicitly asked to include them for Claude review/training context.
- Do not commit `workspace/logs/` as training material. Use the sanitized learning manifest instead: `workspace/projects/lipstick-cm-30s/learning-materials-20260701.md`.
- Keep failed-output notes in project markdown files so the next agent does not repeat the same mistake.
