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

The generated Seedance clips are rejected:

- `workspace/outputs/lipstick-cm-30s/clip_01_9x16.mp4`
- `workspace/outputs/lipstick-cm-30s/clip_02_9x16.mp4`

They may exist only on the local machine. Treat them as failed review material, not assets for finishing.

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
- Do not commit heavy failed MP4s unless the user explicitly asks.
- Keep failed-output notes in project markdown files so the next agent does not repeat the same mistake.
