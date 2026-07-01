# Claude Code Instructions

Follow `AGENTS.md`, `WORKFLOW.md`, and `workspace/agent-guides/cross-agent-runbook.md`.

## Current Critical Context

The active project is:

`workspace/projects/lipstick-cm-30s/`

Before doing any work on it, read these files in full:

- `workspace/projects/lipstick-cm-30s/postmortem-20260701-blender-fleshout-mismatch.md`
- `workspace/projects/lipstick-cm-30s/review-20260701-seedance-failed.md`
- `workspace/projects/lipstick-cm-30s/seedance-conditions.md`
- `workspace/briefs/lipstick-cm-30s-script.md`
- `WORKFLOW.md`

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

Next work is not video generation.

Next work is to create photoreal key visuals derived from the Blender storyboard:

- Clip 1 start key: luxury lipstick macro, dark premium studio, no visible blockout planes.
- Clip 1 end key: photoreal product hero shot, black lacquer tube, champagne-gold metal, deep red bullet.
- Clip 2 lips key: anonymous luxury lips close-up, integrated beauty campaign lighting, no full face, no pasted collage look.
- Clip 2 final key: product/lips world resolves into a premium final brand frame.

Show the key visuals beside the original Blender panels. The user must approve them before any new Seedance estimate or generation.

### Status (Claude Code, this session — revised)

Looked directly at the failed contact sheets (`workspace/outputs/lipstick-cm-30s/review_frames/clip_0{1,2}_contact.jpg`) and found a **second failure mode the postmortem had not caught**: the "orbit light rings / floating particles" prompt language rendered as literal white line/dot graphic overlays (a motion-graphics-template look), not photographic light. Logged as `FP-003` in the new **`references/known-failure-patterns.md`** — a durable, cross-project failure-pattern registry (the practical, non-ML-retraining version of a "feedback loop": accumulate root causes here, and every future Seedance generation must check this file first). FP-001 (raw Blender as start_image) and FP-002 (product+lips composite) are also logged there from the existing postmortem.

Rewrote all 4 key-visual prompts to fix FP-003 (photographic light vocabulary only — bokeh/glints/haze — no "ring/particle/line/dot" as drawn shapes) and to explicitly route through `workspace/scripts/gpt-image-reference.sh` in edit mode (`GPT_IMAGE_SOURCE_IMAGE=<blender render>`), per user direction:

- `workspace/prompts/lipstick-cm/keyvisuals/clip_01_start_key.txt`
- `workspace/prompts/lipstick-cm/keyvisuals/clip_01_end_key.txt`
- `workspace/prompts/lipstick-cm/keyvisuals/clip_02_lips_key.txt`
- `workspace/prompts/lipstick-cm/keyvisuals/clip_02_final_key.txt`

Each still carries a `Status: proposal` pending marker. **Not executed yet** — this session has neither `OPENAI_API_KEY` nor a connected Higgsfield MCP tool. Whichever agent/session has `OPENAI_API_KEY` should run these 4 prompts through `gpt-image-reference.sh` (source images already referenced inside each file), show the results beside the original Blender panels, and get user approval before any new Seedance cost estimate or generation. `WORKFLOW.md` §7-8 now requires checking `references/known-failure-patterns.md` before every future Seedance generation, not just this project's.

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
