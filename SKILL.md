---
name: seedance
description: Create short videos with Higgsfield Seedance from a brief, generated reference image, product/reference assets, screenshots, or brand materials. Use when an agent needs to plan image-to-video prompts, generate vertical/horizontal variants, estimate cost, submit Seedance jobs through Higgsfield MCP, track outputs, or package reusable video workflows for commercials, product demos, explainers, social posts, app walkthroughs, event teasers, portfolio clips, or visual loops.
---

# Seedance Video Workflow

## Overview

Use this skill to produce short videos with Higgsfield Seedance while keeping the workflow reusable across video use cases. Treat every project name, brand, person, product, claim, style, and reference asset as user-provided input; do not bake project-specific defaults into the skill.

The skill supports CM/commercial work, but it is not limited to CM. Route the job by `video_use_case` first, then apply the correct prompt structure and safety checks.

For TikTok-style story videos with recurring guides, theater-like cast libraries, user-supplied character sources, external narration, storyboard panels, or edited Japanese captions, also read `references/tiktok-story-cast-workflow.md` before writing prompts or preparing jobs.

When the user asks to learn from external Higgsfield/Seedance examples, X posts, or demo repositories, read `references/higgsfield-mcp-demo-patterns.md` and use it only as a production-pattern reference unless rights are confirmed.

When the user asks for viral, popular, market-demand, autonomous learning, trend optimization, UGC, or "what people want," read `references/public-demand-short-video-patterns.md` before choosing the concept, hook, storyboard, or generation route.

When the user asks for TikTok Ads, Spark Ads, Non-Spark Ads, ad review, Pixel, Events API, CV-focused TikTok creatives, A/B tests, post-launch ad learning, LP consistency, Japanese ad compliance, or paid TikTok deployment checks, read `references/tiktok-ad-ops-workflow.md` before writing scripts or prompts.

When the user asks Hermes to run autonomously, keep iterating, run many variants, manage paid generation loops, or operate ad/launch tasks with permission, read `references/hermes-autonomous-loop.md` before executing. Autonomous execution requires a run-permission manifest with scope, caps, allowed actions, stop conditions, and logging.

When the user asks to use Blender, GLB/OBJ/3D assets, local 3D previews, 3D factory floors, camera paths, lighting/material checks, or Blender-rendered plates before Seedance/Higgsfield generation, read `references/blender-3d-preview-workflow.md`. Blender work is local-only and must not trigger paid generation or external publishing.

When the user asks for a natural-language-only movie/short-film/multi-shot commercial pipeline (Blender previs → GPT Image storyboard → Palmier Pro audio → Seedance → Palmier Pro finishing), or when a project needs the same character/product/scene to stay consistent across multiple shots with real narrative progression, read `references/end-to-end-movie-pipeline.md` before planning. Route single-shot or asset-swap-only requests through the existing Image-To-Video Route instead; do not apply the heavier pipeline where it is not needed.

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

## TikTok Story / Cast Library Route

Use this route when the user wants a TikTok/Shorts-style narrative, a recurring "cast" of guide characters, or user-supplied source characters/assets:

1. Treat the deliverable as `video_use_case=social-post` or `story-scene`.
2. Build or update a local cast library:
   - guide/model references
   - user-supplied source characters
   - creature/prop/background references
   - scene-specific reference frames
   - rights notes and publication status
3. Keep the story continuous across clips:
   - one 60s story can be planned as 4 x 15s clips
   - each clip should end by motivating the next clip
   - the same guide/cast should appear or be clearly implied throughout
4. Create a storyboard script before generation:
   - for a 60s story, write 8-12 panels before writing Seedance prompts
   - each panel must include time range, cast, location, camera motion, action, narration, planned subtitle/telop, primary reference, and next-scene motivation
   - do not generate until the storyboard shows a continuous cause-and-effect chain
5. If the generation endpoint accepts only one start image, choose one primary reference per clip. Do not force multiple start images into one request.
6. For voice-led edits, keep Seedance visual-only and generate narration separately:
   - set Seedance audio generation to false unless explicitly approved
   - write exact narration in the target language
   - generate voice-over with the approved TTS route
   - add subtitles/telop in editing after audio timing is known
7. For existing characters, celebrities, or third-party IP-like material, use user-supplied source assets only when the user confirms rights. If rights are unclear, mark the output as internal draft only.

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
   - cast/source asset manifest when using recurring characters or user-supplied source materials
   - storyboard/script panel count when making a narrative or TikTok story
   - demand target when optimizing for public/social performance: views, comments, saves, paid ad CTR, product recall, or story retention
   - TikTok ad operations context when relevant: Spark/Non-Spark, KPI, LP URL, tracking status, high-risk category, approval owner
   - autonomous run permission manifest when Hermes or any agent is expected to execute beyond planning
2. Gather references from local/project files first. Use web assets only when explicitly allowed and rights are clear.
3. Write one prompt per output. Do not reuse a 16:9 prompt unchanged for 9:16.
4. Keep Seedance responsible for cinematic/motion video. Keep in-video text short: one phrase per beat. For subtitle-heavy workflows, generate no in-video text and add captions in post.
5. Preflight:
   - Confirm the host agent has Higgsfield MCP connected.
   - Use Higgsfield MCP to check account/login/plan/credits.
   - Use Higgsfield MCP to check `seedance_2_0` availability.
   - Use Higgsfield MCP to estimate generation cost.
6. Generate:
   - Use `seedance_2_0` by default unless the user chooses another model.
   - Prefer `1080p` for the first approved draft unless the user prioritizes quality and credits allow higher settings.
   - Use `generate_audio=true` only when narration/music is wanted and approved. For workflows with external TTS, keep `generate_audio=false`.
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
9. For social-demand work, score the draft concept or finished output against the demand pattern checklist before spending more generation credits.
10. For autonomous or paid operations, execute only actions explicitly allowed in the run-permission manifest. Without that manifest, stop at planning/checklists and request approval.

## Rights Gate

For public-facing, commercial, client, brand, or monetized uses, confirm material rights before generation and before final delivery. AI cannot complete legal clearance by itself.

- Prefer user-provided images, videos, logos, people, product materials, screenshots, or brand assets.
- Do not use web images or third-party materials in final public/commercial outputs unless the user confirms rights.
- Person photos, store photos, product photos, logos, and UI screenshots require a clear usage basis.
- If rights are unclear, label the output as an internal draft and keep it separate from final deliverables.
- Do not imitate celebrities, existing brands, third-party ads, films, anime, games, or protected characters without permission.
- User-supplied source images of public figures, performers, actors, fictional characters, or recognizable IP must be treated as rights-sensitive source assets. They can be cataloged for internal drafting, but public/commercial output requires the user's rights confirmation.
- When trademark, copyright, likeness, or publicity-right risk exists, use alternate materials, abstract visuals, generic models, fictional brands, or non-commercial drafts.
- Final publication rights checks must be performed by the user/client or responsible human reviewer.
- For the end-to-end pipeline (Blender + Palmier Pro audio), read the extended rights checks in `references/end-to-end-movie-pipeline.md`, including voice-clone consent for real-person narration.

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
- For TikTok paid ads, connect the creative to LP, KPI, tracking, Spark/Non-Spark choice, review risk, and post-launch learning.

### Social Post

- Structure: instant visual hook, motion surprise, one memorable phrase, shareable ending.
- Safety: avoid fake platform UI, fake endorsements, and third-party logos unless rights are confirmed.
- Text: one phrase per beat.
- For TikTok story posts, use a cast manifest, fast handheld motion, short Japanese telop when relevant, and a continuous story chain instead of unrelated shots.
- For demand-driven posts, design the first 2 seconds to work silently: face, product motion, conflict, curiosity, or a before/after visual must be visible immediately.

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

### Story Scene

- Style: cinematic beat, character/object/environment motion, mood continuity.
- Text: optional title or post-edited subtitles only.
- Warning: avoid copyrighted characters, celebrity likeness, and unsafe depictions unless user-supplied rights are confirmed.
- For recurring characters, define a cast role and one primary reference image per clip. Keep exact likeness expectations modest and document AI limitations.

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
- For demand-led content, state the chosen hook type and why the viewer keeps watching.
- Use concise in-video text. Prefer 1-8 characters for logos/names and 5-14 Japanese characters for caption cards.
- For voice-over, write exact narration and specify language, tone, and pronunciation.
- For external narration workflows, state `Seedance visual-only, generate_audio=false`; generate voice-over through the approved TTS provider and add subtitles/telop in editing.
- Separate wide and mobile composition:
  - 16:9: wider layout, panels, environment, clearer explanation.
  - 9:16: centered subject, faster hook, fewer words, strong final moment.
- Do not claim exact fit, exact product condition, medical/legal/financial outcomes, sales/profit/customer acquisition, or official partnership unless the user provided that basis.
- For people: preserve broad identity, expression, and natural face quality without promising perfect likeness.
- For products: preserve color/material/shape as a goal, but label generated footage as reference if used commercially.
- For generated references: specify what Seedance should inherit, such as mood, composition, lighting, subject, style, or color.
- For cast libraries: specify the chosen cast member, their role, the selected primary reference image, and which traits must carry through the clip.
- For storyboard-driven stories: convert each approved panel into a Seedance prompt. Keep the prompt focused on visual action; keep narration and subtitles in the external edit plan.

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

Read `references/tiktok-story-cast-workflow.md` for TikTok/Shorts story videos, theater-like cast libraries, user-supplied character references, visual-only Seedance workflows, external narration, and post-edited subtitles.

Read `references/higgsfield-mcp-demo-patterns.md` when reusing production patterns from X/Higgsfield demo references, such as start-image prompts, post-edited audio/text, review packaging, contact sheets, and raw/final artifact tracking.

Read `references/public-demand-short-video-patterns.md` when optimizing for viral/social demand, UGC ads, trend learning, 2-second hooks, public reference scanning, Marketing Studio/Virality Predictor loops, or reusable audience-fit playbooks.

Read `references/tiktok-ad-ops-workflow.md` when making Seedance/Higgsfield creatives for TikTok Ads, CV campaigns, Spark/Non-Spark decisions, Pixel/Events API checks, Top Ads analysis, compliance review, A/B tests, or post-launch learning loops.

Read `references/hermes-autonomous-loop.md` when Hermes or another agent should run iterative research, prompt generation, paid media generation, ad account operations, budget/bid changes, Spark usage, external posting, or destructive actions under explicit permission.

Read `references/end-to-end-movie-pipeline.md` for the Blender previs → GPT Image storyboard → Palmier Pro audio → Seedance → Palmier Pro finishing pipeline, including light-path vs. heavy-path routing, consistency rules across shots, the dialogue/lip-sync check, and extra approval gates.

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
- [ ] External TTS/subtitle handoff checked when `generate_audio=false`
- [ ] Cast/source asset manifest checked when using recurring characters
- [ ] Storyboard panels approved when making a narrative/TikTok story
- [ ] Demand hook and retention pattern checked for viral/social work
- [ ] TikTok ad ops checks completed when used for paid TikTok: Spark/Non-Spark, LP, tracking, review risk, A/B plan, human approval
- [ ] Autonomous run-permission manifest checked before any self-running, paid, ad-account, external-posting, or destructive operation
- [ ] For the end-to-end pipeline (heavy path): storyboard approval gate, narration lock, and final-export approval gate all passed
- [ ] On-screen text readable
- [ ] Claims and rights are safe for intended use
- [ ] Final MP4 opened successfully
- [ ] Output paths recorded
- [ ] Delivery package created
- [ ] Known limitations documented
