# Seedance CM Workflow

## Required Inputs

Capture these before generation:

- Brand/service/product name
- Pronunciation guide, if needed
- One-line value proposition
- Target format: `16:9`, `9:16`, `1:1`, or another supported ratio
- Duration and number of variants
- Main reference assets:
  - model/person image
  - product images
  - app screenshots
  - logo or brand visuals
- Audio policy:
  - AI voice-over allowed or not
  - AI music allowed or not
  - in-video AI text allowed or not

## 15-Second Structure

Use this as the default short CM structure.

### 16:9

1. 0-3s: Establish the product/service and main subject.
2. 3-7s: Show the problem or transformation trigger.
3. 7-12s: Show the product/service result with visual proof.
4. 12-15s: End with brand/service name and one clear CTA or claim.

### 9:16

1. 0-2s: Immediate hook.
2. 2-6s: Fast transformation or benefit demonstration.
3. 6-11s: Main result, centered and readable.
4. 11-15s: Final brand/service moment.

## 30-Second Structure

For two 15-second clips that will be joined later:

- Clip A: hook, problem, transformation setup.
- Clip B: result, social proof or use cases, final brand/service moment.

Keep each clip self-contained enough to work alone.

## Prompt Template

```text
{ASPECT} commercial video for {BRAND_OR_SERVICE_NAME}.
Pronounce the name as "{PRONUNCIATION}".

Goal:
{ONE_LINE_VALUE_PROPOSITION}

References:
- Use the provided main reference as the primary subject or product anchor.
- Use additional references only as visual/product/app references.
- Do not imply unsupported official partnerships or guarantees.

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
3. "{BRAND_OR_SERVICE_NAME}"

Voice-over:
Include a {LANGUAGE} voice-over with this exact narration:
"{NARRATION}"

Audio:
{MUSIC_DIRECTION}

Quality and safety:
Realistic commercial footage. Clear subject. Stable face/object. No distorted anatomy, no unreadable long text, no unsupported claims, no unsafe or sexualized framing, no clutter.
```

## Variant Defaults

### Product / EC

- Style: clean studio, catalog-quality lighting, product cards, before/after usage.
- Text: short benefit + product/service name.
- Warning: do not imply exact product condition or guaranteed fit unless verified.

### App / SaaS

- Style: app panels, workflow transitions, dashboard moments, user outcome.
- Text: feature name + result.
- Warning: avoid fake metrics unless provided.

### Brand / Lifestyle

- Style: cinematic hero, environment, brand emotion.
- Text: tagline + brand name.
- Warning: keep claims soft unless substantiated.

## Quality Checklist

Before final response, verify:

- Job completed and result URL is saved.
- MP4 was downloaded when practical.
- Duration is close to requested duration.
- Aspect ratio matches target.
- Generated text is acceptable for a draft.
- Voice-over pronunciation was explicitly specified.
- No brand/project-specific defaults leaked into the prompt.
- If quality is weak, recommend a second pass with stronger references or fewer on-screen text requirements.
