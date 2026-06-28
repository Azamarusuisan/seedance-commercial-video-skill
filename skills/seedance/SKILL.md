---
name: seedance
description: Create short videos with Higgsfield Seedance from a brief, generated reference image, product/reference assets, screenshots, or brand materials. Use when an agent needs to plan image-to-video prompts, generate vertical/horizontal variants, estimate cost, submit Seedance jobs through Higgsfield MCP, track outputs, or package reusable video workflows for commercials, product demos, explainers, social posts, app walkthroughs, event teasers, portfolio clips, or visual loops.
---

# Seedance Video Workflow

## Overview

Use this skill to produce short videos with Higgsfield Seedance while keeping the workflow reusable across video use cases. Treat every project name, brand, person, product, claim, style, and reference asset as user-provided input; do not bake project-specific defaults into the skill.

The skill supports CM/commercial work, but it is not limited to CM. Route the job by `video_use_case` first, then apply the correct prompt structure and safety checks.

## Supported Use Cases

Choose the closest use case before writing prompts:

- `commercial`: ads, CM, product/service promotion, sales-oriented short videos.
- `social-post`: X, TikTok, Instagram, YouTube Shorts, announcement clips, visual hooks.
- `product-demo`: product motion, EC showcase, catalog-style video, before/after usage.
- `app-walkthrough`: SaaS/app screens, dashboard moments, feature walkthroughs.
- `explainer`: educational, tutorial, how-to, workflow explanation.
- `event-teaser`: event, seminar, launch, campaign teaser.
- `portfolio`: case study, creator showcase, project reveal, note/LP embed.
- `background-loop`: atmospheric loop, hero background, ambient visual, motion backdrop.
- `story-scene`: narrative beat, concept scene, mood shot, character/environment clip.

If the user does not specify a use case, infer a conservative default from the brief and state it in the brief. For commercial or public-facing uses, keep rights and claims checks active.

## Image-To-Video Route

Use this route when the user has no footage, wants a generated visual reference, or asks for image-to-video:

1. Lock the video brief:
   - `video_use_case`
   - title/project name
   - pronunciation, if relevant
   - target viewer
   - intended platform or placement
   - aspect ratio, duration, count
   - audio policy
   - text policy
   - budget, max jobs, max retry count
   - rights/commercial-publication status
2. Create or select a reference image:
   - Prefer user-provided assets with clear usage rights.
   - If there are no usable assets, create an abstract or synthetic generated reference image.
   - Keep generated reference text minimal because image text may fail.
   - Save the selected reference image inside `workspace/assets/`.
3. Write one Seedance prompt per output:
   - Do not reuse a 16:9 prompt unchanged for 9:16.
   - Treat the image as a visual anchor, not a source of legal clearance.
   - Mention what should be preserved from the reference image: mood, subject, layout, colors, product, or scene.
4. Prepare MCP requests:
   - `workspace/scripts/seedance-cost.sh` and `workspace/scripts/seedance-generate.sh` include `IMAGE_FILE` when the file exists.
   - Use `IMAGE_FILE=workspace/assets/<reference>.png` to override the default.
   - The generated MCP request stores the prompt plus `image=<path>` for the host Higgsfield MCP tool.
5. Run Higgsfield MCP only after approval, cost check, login/credit check, and rights check.
6. Record sanitized results, result URLs, MP4 paths, and known limitations.

## Workflow

1. Lock the brief:
   - video use case
   - title/project/product/service name
   - required pronunciation, if any
   - target audience or viewer
   - intended placement: feed, note, LP, YouTube, pitch deck, app page, internal review, etc.
   - deliverables: aspect ratio, duration, count
   - maximum budget, maximum jobs, and maximum retry count
   - whether AI voice-over, music, and in-video text are allowed
   - required references: generated image, model/person, products, screenshots, logo, style frames, brand assets
2. Gather references from local/project files first. Use web assets only when explicitly allowed and rights are clear.
3. Write one prompt per output. Do not reuse a 16:9 prompt unchanged for 9:16.
4. Keep Seedance responsible for cinematic/motion video. Keep in-video text short: one phrase per beat.
5. Preflight:
   - Confirm the host agent has Higgsfield MCP connected.
   - Use Higgsfield MCP to check account/login/plan/credits.
   - Use Higgsfield MCP to check `seedance_2_0` availability.
   - Use Higgsfield MCP to estimate generation cost.
6. Generate:
   - Use `seedance_2_0` by default unless the user chooses another model.
   - Prefer `1080p` for the first approved draft unless the user prioritizes quality and credits allow higher settings.
   - Use `generate_audio=true` only when narration/music is wanted and approved.
7. Track every artifact:
   - prompt file
   - reference image or asset list
   - model and parameters
   - cost estimate
   - job JSON
   - result URL
   - downloaded MP4 path
8. Verify before final:
   - output opens and has expected duration/aspect
   - important names and pronunciation are correct in the prompt
   - text is short enough to be plausible
   - reference person/object/product is not badly distorted
   - visual does not imply unsupported claims
   - usage limitations are documented

## Rights Gate

For public-facing, commercial, client, brand, or monetized uses, confirm material rights before generation and before final delivery. AI cannot complete legal clearance by itself.

- Prefer user-provided images, videos, logos, people, product materials, screenshots, or brand assets.
- Do not use web images or third-party materials in final public/commercial outputs unless the user confirms rights.
- Person photos, store photos, product photos, logos, and UI screenshots require a clear usage basis.
- If rights are unclear, label the output as an internal draft and keep it separate from final deliverables.
- Do not imitate celebrities, existing brands, third-party ads, films, anime, games, or protected characters without permission.
- When trademark, copyright, likeness, or publicity-right risk exists, use alternate materials, abstract visuals, generic models, fictional brands, or non-commercial drafts.
- Final publication rights checks must be performed by the user/client or responsible human reviewer.

## Budget Lock

Video generation can consume credits quickly. Lock budget and iteration limits before any paid generation.

- Confirm maximum budget, maximum job count, and maximum retry count before generation.
- If budget is unknown, use a minimal setup: one short draft, one aspect ratio, no audio, no extra variants.
- Do not exceed budget or run unlimited regenerations.
- If the estimate is too high, reduce count, duration, resolution, audio, or variants.
- Regeneration is normally limited to 2 attempts. For a third attempt, ask the user to confirm budget, revise references, simplify the prompt, or switch to manual editing.
- When cost estimation is available, run it through Higgsfield MCP before generation and record the result.

## Use-Case Prompt Guidance

### Commercial

- Structure: hook, value proposition, use/result, brand/CTA.
- Safety: unsupported sales, profit, hit-rate, No.1, official partnership, medical/financial/legal claims require evidence.
- Text: short tagline plus brand/service name.

### Social Post

- Structure: instant visual hook, motion surprise, one memorable phrase, shareable ending.
- Safety: avoid fake platform UI, fake endorsements, and third-party logos unless rights are confirmed.
- Text: one phrase per beat.

### Product Demo

- Structure: product reveal, use motion, material/detail shot, final product frame.
- Safety: do not imply exact product condition, fit, specifications, or availability unless provided.
- Text: feature label plus product name.

### App Walkthrough

- Structure: app context, feature action, dashboard/result moment, final screen.
- Safety: avoid fake metrics, fake customers, real private data, and copied third-party UI.
- Text: feature name plus short outcome.

### Explainer

- Structure: concept/problem, visual metaphor, step-by-step transformation, final takeaway.
- Safety: keep factual claims cautious and label generated diagrams as explanatory when needed.
- Text: short labels only.

### Event Teaser

- Structure: atmosphere, date/theme reveal, highlight moment, event title/CTA.
- Safety: do not show unapproved venues, speakers, sponsors, or logos.
- Text: event title, date, CTA.

### Portfolio

- Structure: project title, process/visual reveal, outcome frame, creator/client credit.
- Safety: avoid unapproved client logos, private work, or unlicensed assets.
- Text: project title plus credit.

### Background Loop

- Structure: seamless ambience, slow motion, no hard narrative dependency.
- Safety: avoid readable claims or logos unless provided.
- Text: usually none.

## MCP Pattern

Use the host-provided Higgsfield MCP tool for account checks, model checks, cost estimates, and generation. Do not use the unrelated PyPI `higgsfield` package or assume a local CLI is available.

For cross-agent handoff, prepare request JSON with:

```bash
bash workspace/scripts/higgsfield-status.sh
APPROVED=1 bash workspace/scripts/seedance-cost.sh
APPROVED=1 bash workspace/scripts/seedance-generate.sh
```

For image-to-video, explicitly pass the reference image when needed:

```bash
IMAGE_FILE=workspace/assets/reference-image-v1.png \
APPROVED=1 \
bash workspace/scripts/seedance-generate.sh
```

The generated files under `workspace/mcp-requests/` describe the intended Higgsfield MCP calls. After running MCP, record sanitized responses with:

```bash
bash workspace/scripts/record-mcp-json.sh account <mcp-account-response.json>
bash workspace/scripts/record-mcp-json.sh model <mcp-model-response.json>
bash workspace/scripts/record-mcp-json.sh cost <mcp-cost-response.json>
bash workspace/scripts/record-mcp-json.sh job <mcp-job-response.json>
```

When passing multiple media references, first verify the Higgsfield MCP media schema with a low-cost test or current model documentation. If a multi-reference path fails, fall back to one strong visual reference plus explicit description in the prompt.

## Prompt Rules

- Always include required pronunciation when a name has a non-obvious reading.
- State `video_use_case`, target viewer, platform/placement, aspect ratio, duration, and output count.
- Use concise in-video text. Prefer 1-8 characters for logos/names and 5-14 Japanese characters for caption cards.
- For voice-over, write exact narration and specify language, tone, and pronunciation.
- Separate wide and mobile composition:
  - 16:9: wider layout, panels, environment, clearer explanation.
  - 9:16: centered subject, faster hook, fewer words, strong final moment.
- Do not claim exact fit, exact product condition, medical/legal/financial outcomes, sales/profit/customer acquisition, or official partnership unless the user provided that basis.
- For people: preserve broad identity, expression, and natural face quality without promising perfect likeness.
- For products: preserve color/material/shape as a goal, but label generated footage as reference if used commercially.
- For generated references: specify what Seedance should inherit, such as mood, composition, lighting, subject, style, or color.

## Acceptance Criteria

- Specified aspect ratio, duration, and count match the brief.
- Required names, labels, and pronunciation notes are correct.
- In-video text is short, readable, and draft-appropriate.
- Reference person/object/product/UI is not badly distorted.
- Output does not include unsupported claims or unauthorized third-party elements.
- Final MP4 opens successfully.
- Output file path, generation settings, job information, result URL, and limitations are recorded.
- For public/commercial/client use, rights and claims notes are present.

## Delivery Package

For each project, organize deliverables and production information in the same folder or delivery memo.

- final MP4 files
- prompt files
- reference asset list
- generation settings
- cost estimate, when available
- job JSON
- result URLs
- revision notes
- usage notes
- known limitations

`known limitations` should mention, when applicable:

- AI-generated video may not guarantee tiny text, exact logos, exact face identity, exact product geometry, exact UI, or legal/factual accuracy.
- Important legal, medical, financial, pricing, campaign, product, or rights statements require human review.
- Final publication requires user/client review of content, rights, claims, and platform rules.
- If any source material rights are unclear, the output is an internal draft, not a final public asset.

## Reference

Read `references/seedance-cm-workflow.md` before writing final prompts or generating multi-variant jobs. The filename is kept for backward compatibility; the content now covers general short-video workflows, not only CM.

## Final Checklist

- [ ] Brief confirmed
- [ ] Use case confirmed
- [ ] Rights confirmed
- [ ] Budget confirmed
- [ ] Aspect ratio confirmed
- [ ] Duration confirmed
- [ ] Reference image/assets confirmed
- [ ] Names and pronunciation checked
- [ ] Voiceover policy checked
- [ ] On-screen text readable
- [ ] Claims and rights are safe for intended use
- [ ] Final MP4 opened successfully
- [ ] Output paths recorded
- [ ] Delivery package created
- [ ] Known limitations documented
