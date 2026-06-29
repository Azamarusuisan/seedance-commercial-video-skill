# TikTok Story Cast Workflow

Use this reference for TikTok, Instagram Reels, YouTube Shorts, and Vlog-style story videos that rely on recurring guides, a theater-like cast library, user-supplied source characters, external narration, and edited captions.

## Goal

Make the project feel like a small troupe:

- recurring male/female guides
- user-supplied source characters
- creatures, vehicles, props, and location frames
- a continuous story line across multiple Seedance clips
- external narration and post-edited subtitles when timing matters

The cast library is a production aid, not a rights clearance system. Rights-sensitive source assets must still be cleared by the user or client before public/commercial use.

## Recommended Folder Pattern

Inside a project workspace:

```text
workspace/assets/cast/
  guides/
    female_traveler/
    male_traveler/
  source_refs/
    user_supplied/
  props/
  creatures/
  locations/
  cast-manifest.json
```

Keep raw images out of git unless they are intentionally licensed sample assets. Commit the manifest schema, README, prompts, and notes; keep project-specific person/source images local or in a private asset store.

## Cast Manifest

Create `workspace/assets/cast/cast-manifest.json` from the example template.

Required fields per cast item:

- `id`: stable short ID, e.g. `female_guide_01`
- `role`: guide, source_character, creature, prop, location, vehicle
- `asset_path`: local path to the image/video reference
- `rights_status`: `user_supplied_confirmed`, `licensed`, `generated`, `internal_draft_only`, or `unknown`
- `use_scope`: internal draft, organic social, paid ad, client delivery, etc.
- `prompt_identity`: concise visual identity to reuse in prompts
- `notes`: generation or editing constraints

## One Start Image Rule

Some Higgsfield/Seedance routes accept only one `start_image`.

Default policy:

1. Pick one primary reference image per clip.
2. Put other cast members, props, and style notes in the prompt.
3. If multiple references are required, split the scene into multiple clips or run separate generations.
4. Do not keep retrying a multi-image request after the endpoint returns a one-start-image error.

## 60s TikTok Story Shape

For a 60s story, first make a storyboard script, then use four visual-only Seedance clips:

1. `0-15s`: hook and threshold
2. `15-30s`: discovery and chase
3. `30-45s`: arrival, invitation, or danger
4. `45-60s`: payoff and proof

Each clip should carry one story cause into the next:

```text
ordinary place -> hidden entrance -> source character clue -> guide follows -> vehicle/portal/meeting -> final proof
```

Avoid four unrelated "cool shots." The audience should understand why the next scene happens.

## Storyboard Script First

Before writing Seedance prompts, create 8-12 storyboard panels for a 60s story. This is the default because recurring character videos fail when the visual prompt is polished but the story chain is vague.

Each panel should include:

- `time_range`: exact seconds
- `clip_group`: 1-4, matching the four Seedance clips
- `cast`: chosen cast IDs from the manifest
- `location`: where the beat happens
- `primary_reference`: one main image/video reference for this panel or clip
- `camera`: handheld, push-in, pan, tracking, low angle, overhead, etc.
- `action`: visible movement only
- `narration`: exact spoken Japanese line when voice-led
- `subtitle_telop`: planned edited caption, not generated inside Seedance
- `transition_reason`: why the next panel happens

Recommended 60s rhythm:

```text
0-5s hook
5-10s guide notices clue
10-15s threshold/entrance
15-22s chase or travel
22-30s first reveal
30-38s character/creature encounter
38-45s invitation, danger, or bargain
45-52s payoff action
52-58s final proof
58-60s loop/next-episode hook
```

Only after this is approved, collapse the panels into 4 x 15s Seedance prompts. The prompts should describe motion and scene continuity; narration, ElevenLabs voice, and Japanese subtitles stay in post-production.

## Voice And Subtitle Handoff

For story content, especially Japanese Vlog narration:

- Keep Seedance visual-only: `generate_audio=false`.
- Write exact narration first.
- Generate voice-over with the approved TTS provider, e.g. Higgsfield ElevenLabs when available.
- Add subtitles/telop during editing, after the audio timing is known.
- Do not ask Seedance to render readable subtitles inside the video.

Subtitle style should match the platform:

- TikTok/Shorts: short Japanese punch phrases, bold white text with dark stroke, not long paragraphs.
- Narrative Vlog: show key phrases, not every spoken word.
- Explainer: use more complete captions, but still split into short groups.

## Prompt Pattern

```text
Vertical 9:16 handheld smartphone Vlog, TikTok story style.
Primary cast reference: {CAST_ID}, {PROMPT_IDENTITY}.
Scene continues from the previous clip: {PREVIOUS_BEAT}.
Action: {GUIDE_ACTION}, {CAMERA_ACTION}, {ENVIRONMENT_ACTION}.
Story beat: {CAUSE_AND_REVEAL}.
Keep the same guide/cast identity as much as possible.
No readable generated text, no logos, no unauthorized third-party brands.
Seedance visual-only; narration and subtitles will be added in editing.
```

## Rights Notes

Use these labels in the manifest:

- `generated`: AI-generated or synthetic asset created for the project.
- `user_supplied_confirmed`: user confirmed rights for the intended use.
- `licensed`: licensed stock/client asset; record license notes.
- `internal_draft_only`: can be used for private tests but not public/commercial delivery.
- `unknown`: do not use for final generation until clarified.

When source assets look like real performers, celebrities, existing characters, film/anime/game characters, logos, or branded campaign stills, treat them as rights-sensitive even if they were supplied by the user. The agent should not identify the person or character; it should record the asset as user-supplied source material and ask the user/client to confirm publication rights before final use.

## Acceptance Checks

- Cast manifest exists and includes rights notes.
- Storyboard panels exist before generation for narrative/TikTok story work.
- One primary reference image is chosen per Seedance request.
- The story chain is continuous across clips.
- Seedance audio policy is explicit.
- Voice-over language is explicit.
- Subtitles/telop are planned as post-production overlays.
- Output is marked internal draft if source rights are not confirmed.
