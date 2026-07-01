# Seedance Short Video Workflow

This file keeps the historical `seedance-cm-workflow.md` name for compatibility. The workflow is now generic and can be used for commercials, social posts, product demos, app walkthroughs, explainers, event teasers, portfolio clips, background loops, and story scenes.

## Required Inputs

Capture these before generation:

- Video use case:
  - `commercial`
  - `social-post`
  - `product-demo`
  - `app-walkthrough`
  - `explainer`
  - `event-teaser`
  - `portfolio`
  - `background-loop`
  - `story-scene`
- Project/title/brand/product/service name
- Pronunciation guide, if needed
- One-line objective or viewer takeaway
- Target viewer
- Intended placement: X, TikTok, Instagram, YouTube, note, LP, pitch deck, app page, internal review, etc.
- Target format: `16:9`, `9:16`, `1:1`, or another supported ratio
- Duration and number of variants
- Main reference assets:
  - generated reference image
  - model/person image
  - product images
  - app screenshots
  - logo or brand visuals
  - style frames
- Audio policy:
  - AI voice-over allowed or not
  - AI music allowed or not
  - in-video AI text allowed or not
- Rights and publication status:
  - internal draft only
  - public organic post
  - paid ad/commercial
  - client delivery
  - monetized article/course/product

## Image-To-Video Handoff

Use this route when a still reference image should drive the Seedance video:

1. Check whether Blender can be used before preparing the reference image:
   - Run `command -v blender`.
   - If Blender is available, ask once: "Blenderを使うとこのクオリティが出ます。使用しますか?"
   - YES: use the same local previs method as the heavy path: create a project-specific `bpy` script based on `workspace/blender/action_movie_previs.py`, run `blender --background --python`, render one still, save it under `workspace/assets/`.
     **This render is composition reference only (`role=composition_only`) and must never become `IMAGE_FILE` directly** (`references/known-failure-patterns.md` FP-001; tried for real on the lipstick CM project and failed). It must go through GPT Image / Higgsfield image generation (`workspace/prompts/templates/gpt-image-from-blender-previs.txt`) to produce a photoreal storyboard frame / key visual first.
   - NO, or Blender is not installed: continue with the existing reference-image route.
   - The Blender render itself is reviewed via the existing reference image/assets approval gate; the *generated photoreal key visual* needs a further explicit approval before it can be used as `IMAGE_FILE` (see `references/image-to-video-handoff.md`).
2. Prepare the reference prompt in `workspace/prompts/reference-image-v1.txt` or a project-specific prompt file if a generated reference image is still needed. If Blender was used, this is the GPT-Image-from-Blender-previs prompt instead.
3. Generate or select a reference image and save it under `workspace/assets/`. If Blender was used, this is the photoreal key visual output, not the Blender render.
4. Use that (photoreal, human-approved) image as `IMAGE_FILE` when preparing Seedance cost/generation requests. `seedance-cost.sh`/`seedance-generate.sh` call `workspace/scripts/validate-seedance-input.py` first and will block a raw Blender render.
5. Keep the Seedance prompt explicit about what to inherit from the image:
   - subject
   - mood
   - composition
   - lighting
   - colors
   - product details
   - style
   - safe text areas
6. Do not ask Seedance to infer legal rights from the reference image.
7. If the image has too much text, reduce video text and restate text explicitly in the Seedance prompt.

Example:

```bash
GPT_IMAGE_PROMPT_FILE=workspace/prompts/reference-image-v1.txt \
GPT_IMAGE_OUT=workspace/assets/reference-image-v1.png \
bash workspace/scripts/gpt-image-reference.sh

IMAGE_FILE=workspace/assets/reference-image-v1.png \
ASSET_MANIFEST=workspace/projects/<project_id>/shots/<shot_id>/asset-manifest.json \
PERMISSION_MANIFEST=workspace/run/<run_id>/permission.json \
PROMPT_FILE=workspace/prompts/seedance-video-v1.txt \
ASPECT_RATIO=9:16 \
APPROVED={{SET_TO_1_ONLY_AFTER_GATE_CHECK}} \
bash workspace/scripts/seedance-cost.sh

IMAGE_FILE=workspace/assets/reference-image-v1.png \
ASSET_MANIFEST=workspace/projects/<project_id>/shots/<shot_id>/asset-manifest.json \
PERMISSION_MANIFEST=workspace/run/<run_id>/permission.json \
PROMPT_FILE=workspace/prompts/seedance-video-v1.txt \
ASPECT_RATIO=9:16 \
APPROVED={{SET_TO_1_ONLY_AFTER_GATE_CHECK}} \
bash workspace/scripts/seedance-generate.sh
```

The scripts prepare MCP request JSON only. The actual cost/generation call must be run through the host-provided Higgsfield MCP tool.

## 15-Second Structure

Use this as the default short-video structure. Adjust by use case.

### 16:9

1. 0-3s: Establish the subject, scene, or core idea.
2. 3-7s: Show the transformation, action, feature, or concept shift.
3. 7-12s: Show the main visual result, explanation, or emotional payoff.
4. 12-15s: End with title, brand, CTA, takeaway, or seamless loop point.

### 9:16

1. 0-2s: Immediate visual hook.
2. 2-6s: Fast motion, transformation, or key step.
3. 6-11s: Main result, centered and readable.
4. 11-15s: Final title/CTA/takeaway or loop point.

## 30-Second Structure

For two 15-second clips that will be joined later:

- Clip A: hook, context, setup, transformation trigger.
- Clip B: result, explanation/use cases, final title/CTA/takeaway.

Keep each clip self-contained enough to work alone.

## Generic Prompt Template

```text
Create a {DURATION}-second {ASPECT} short video with Higgsfield Seedance.

Video use case:
{VIDEO_USE_CASE}

Project/title/name:
{PROJECT_NAME}
Pronunciation guide:
{PRONUNCIATION_OR_NONE}

Target viewer and placement:
{TARGET_VIEWER}
{PLACEMENT}

Objective:
{ONE_LINE_OBJECTIVE}

Reference image/assets:
- Use the provided reference image as the primary visual anchor.
- Preserve: {WHAT_TO_PRESERVE_FROM_REFERENCE}
- Do not copy or invent third-party logos, private data, unsupported claims, or exact UI unless provided and approved.

Visual direction:
{STYLE_DIRECTION}

Timing:
0-3s: {BEAT_1}
3-7s: {BEAT_2}
7-12s: {BEAT_3}
12-15s: {BEAT_4}

In-video text:
Use only short, clean text:
1. "{TEXT_1}"
2. "{TEXT_2}"
3. "{FINAL_TEXT}"

Voice-over:
{VOICEOVER_POLICY_AND_EXACT_NARRATION_IF_ANY}

Audio:
{MUSIC_OR_SFX_DIRECTION}

Quality and safety:
Clear subject, stable motion, readable short text, no clutter, no unsupported claims, no unauthorized third-party brands, no private data, no unsafe framing.
```

## Use-Case Defaults

### Commercial

- Style: premium product/service visual, clear value proposition, strong final CTA.
- Text: tagline + project/brand name.
- Warning: do not imply sales, profit, hit rate, ranking, official partnership, medical/legal/financial outcomes, or customer acquisition unless substantiated.

### Social Post

- Style: immediate visual hook, kinetic motion, shareable surprise.
- Text: one short phrase per beat.
- Warning: avoid fake platform UI, fake endorsements, third-party logos, and engagement guarantees.

### Product Demo

- Style: clean studio, catalog-quality lighting, product detail, usage motion.
- Text: product name + short feature label.
- Warning: do not imply exact specs, fit, condition, availability, or performance unless verified.

### App Walkthrough

- Style: app panels, screen transitions, dashboard/feature moment, workflow clarity.
- Text: feature name + short result.
- Warning: avoid fake metrics, private data, copied third-party UI, or unsupported outcomes.

### Explainer

- Style: simple visual metaphor, step-by-step transformation, clean labels.
- Text: short labels, no dense paragraphs.
- Warning: keep factual claims cautious and require human review for domain-specific claims.

### Event Teaser

- Style: atmosphere, reveal, date/title moment, anticipation.
- Text: event title, date, CTA.
- Warning: do not show unapproved speakers, sponsors, venues, logos, or ticket details.

### Portfolio

- Style: process reveal, before/after, final showcase frame, creator credit.
- Text: project name + credit.
- Warning: do not reveal private client work or unapproved assets.

### Background Loop

- Style: seamless ambience, slow motion, subtle parallax, no hard narrative.
- Text: usually none.
- Warning: avoid claims, logos, and obvious start/end discontinuities.

### Story Scene

- Style: cinematic beat, character/object/environment motion, mood continuity.
- Text: optional title only.
- Warning: avoid copyrighted characters, celebrity likeness, and unsafe depictions.

## Variant Defaults

### 9:16 Mobile

- Center the subject.
- Use fast hook and fewer words.
- Avoid small UI/detail text.
- Keep important text away from top/bottom crop areas.

### 16:9 Wide

- Use left-to-right depth, panels, environment, and negative space.
- Make the final frame useful as a cover, note embed, LP preview, or portfolio thumbnail.
- Do not merely stretch a 9:16 concept.

### 1:1 Square

- Use central composition.
- Keep text minimal and larger.
- Avoid wide-only camera movement.

## Retry Strategy

If AI video quality is weak, do not rerun the same complex prompt blindly. Reduce complexity first.

1. Reduce in-video text.
   - Remove long captions, multi-line subtitles, and small notes.
   - Keep only project name, short title, or one phrase.
2. Simplify camera movement.
   - Avoid aggressive rotations, fast zooms, complex tracking, and multi-step motion.
   - Use locked camera, slow dolly, simple pan, or controlled parallax.
3. Reduce elements in one clip.
   - Do not combine product, UI, person, logo, text, background change, and transformation all at once.
   - Keep the most important 1-2 elements.
4. Split longer clips.
   - If 15 seconds fails, create 5-8 second clips and join later.
5. Strengthen references.
   - Use clearer front/detail/product/UI/style references when the subject breaks.
6. If face, product, logo, or UI breaks twice, do not rely only on generation.
   - Propose manual edit, alternate structure, stronger reference, still-to-motion treatment, or post-production.
7. Limit retries.
   - Regeneration is normally 2 attempts. More attempts require user approval and budget confirmation.

## Delivery Package

For each project, prepare:

- `final/`
  - final MP4 files
  - filenames with aspect ratio and duration
- `prompts/`
  - final prompt files
  - variant differences
- `references/`
  - reference asset list
  - source, rights status, and intended usage
- `jobs/`
  - generation settings
  - job JSON
  - result URLs
  - cost estimate, when available
- `notes/`
  - revision notes
  - usage notes
  - known limitations

`known limitations` should mention:

- AI-generated video can fail on tiny text, exact logos, exact faces, exact product geometry, exact UI, and complex motion.
- Important legal, medical, financial, pricing, campaign, product, factual, or rights statements require human review.
- Final publication requires content, rights, claims, and platform review by a human.
- If source rights are unclear, the output is an internal draft, not a final public asset.

## Quality Checklist

Before final response, verify:

- Job completed and result URL is saved.
- MP4 was downloaded when practical.
- Duration is close to requested duration.
- Aspect ratio matches target.
- Generated text is acceptable for a draft.
- Voice-over pronunciation was explicitly specified when relevant.
- No project-specific defaults leaked into reusable templates.
- If quality is weak, recommend a second pass with stronger references or fewer requirements.
- Delivery package or delivery notes are prepared.
- Rights, budget, and limitations are recorded.
