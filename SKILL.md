---
name: seedance-commercial-video
description: Create short commercial videos with Higgsfield Seedance from a service/product brief, model reference, product references, screenshots, or brand assets. Use when Codex needs to plan prompts, generate PC/mobile variants, estimate cost, submit Seedance jobs, track outputs, or package reusable CM-generation workflow for fashion, EC, app, SaaS, product, or brand promotion videos.
---

# Seedance Commercial Video

## Overview

Use this skill to produce short CM-style videos with Higgsfield Seedance while keeping the workflow reusable across brands and projects. Treat every brand name, pronunciation, product name, person, and claim as user-provided input; do not bake project-specific defaults into the skill.

## Workflow

1. Lock the brief:
   - service/product name
   - required pronunciation, if any
   - target audience
   - deliverables: aspect ratio, duration, count
   - whether AI voice-over and AI in-video text are allowed
   - required references: model, products, screenshots, brand assets
2. Gather references from local/project files first. Use web assets only when explicitly allowed.
3. Write one prompt per output. Do not reuse a 16:9 prompt unchanged for 9:16.
4. Keep Seedance responsible for cinematic video. Keep in-video text short: one phrase per beat.
5. Preflight:
   - `higgsfield account status --json`
   - `higgsfield model get seedance_2_0 --json`
   - `higgsfield generate cost seedance_2_0 ... --json`
6. Generate:
   - Use `seedance_2_0` by default unless the user chooses another model.
   - Prefer `--resolution 4k` and `--bitrate_mode high` when the user prioritizes quality and credits allow.
   - Use `--generate_audio true` only when AI narration/music is wanted.
7. Track every artifact:
   - prompt file
   - reference file list
   - model and parameters
   - job JSON
   - result URL
   - downloaded MP4 path
8. Verify before final:
   - output opens and has expected duration/aspect
   - brand/service pronunciation is correct in prompt
   - text is short enough to be plausible
   - reference person/object is not badly distorted
   - visual does not imply unsupported claims

## CLI Pattern

```bash
higgsfield generate cost seedance_2_0 \
  --prompt "$(cat prompts/variant.txt)" \
  --image ./assets/reference.png \
  --aspect_ratio 16:9 \
  --duration 15 \
  --resolution 4k \
  --bitrate_mode high \
  --generate_audio true \
  --mode std \
  --json
```

```bash
higgsfield generate create seedance_2_0 \
  --prompt "$(cat prompts/variant.txt)" \
  --image ./assets/reference.png \
  --aspect_ratio 16:9 \
  --duration 15 \
  --resolution 4k \
  --bitrate_mode high \
  --generate_audio true \
  --mode std \
  --json \
  --wait \
  --wait-timeout 60m \
  --wait-interval 10s
```

When passing multiple media references, first verify the CLI/media schema with a low-cost test or current model documentation. If a multi-reference path fails, fall back to one strong visual reference plus explicit product/service description in the prompt.

## Prompt Rules

- Always include the required pronunciation when the service/product name has a non-obvious reading.
- Use concise in-video text. Prefer 1-8 characters for logos and 5-14 Japanese characters for caption cards.
- For voice-over, write exact narration and specify language, tone, and pronunciation.
- Separate PC and mobile composition:
  - PC/16:9: wider layout, product/app panels, clearer service explanation.
  - Mobile/9:16: centered subject, faster hook, fewer words, stronger final brand moment.
- Do not claim exact fit, exact product condition, medical/legal/financial outcomes, or official partnership unless the user provided that basis.
- For people: preserve broad identity, expression, and natural face quality without promising perfect likeness.
- For products: preserve color/material/shape as a goal, but label generated footage as reference if used commercially.

## Reference

Read `references/seedance-cm-workflow.md` before writing final prompts or generating multi-variant CM jobs.
