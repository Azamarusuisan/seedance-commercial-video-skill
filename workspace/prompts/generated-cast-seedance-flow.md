# Generated Cast Seedance Flow

This flow turns the generated cast library into repeatable TikTok/Shorts videos.

## Inputs

- Cast manifest: `workspace/assets/cast/generated_20260629/cast-manifest.json`
- Source reference manifest: `workspace/assets/cast/source_refs_20260629/source-manifest.json`
- Contact sheet: `workspace/assets/cast/generated_20260629/contact_sheet.jpg`
- Story script: `workspace/briefs/tiktok-theater-cast-60s-script.md`
- Voice route: Higgsfield ElevenLabs or approved external TTS
- Subtitle route: post-production editing

## Flow

1. Pick the story type.
   - Mystery Vlog
   - Beauty/travel Vlog
   - Product discovery
   - Testimonial-style, but never fake customer claims
   - Theater ensemble story

2. Assign roles before prompts.
   - Lead: one visually strong cast member
   - Co-lead: one contrast cast member
   - Witnesses: 2-4 ordinary cast members
   - Trust figures: older or professional cast members
   - Crowd/cameos: remaining cast members

3. Write storyboard first.
   - 8-12 panels for 60s
   - Each panel includes time, cast IDs, location, action, narration, telop, and next beat
   - If the story does not cause the next beat, rewrite before generation

4. Split video generation.
   - 60s = 4 x 15s Seedance clips
   - 30s = 2 x 15s Seedance clips
   - 15s = 1 clip with 1-3 cast members
   - Use one primary image per clip

5. Generate visual-only.
   - `generate_audio=false`
   - No generated subtitles
   - No long in-video text
   - No logos or third-party brands unless rights are confirmed

6. Generate voice separately.
   - Japanese script first
   - Higgsfield ElevenLabs voice after script approval
   - Keep exact narration in a text file
   - Do not rely on Seedance for exact spoken lines

7. Add subtitles in editing.
   - Short Japanese telop
   - Bold white text with dark stroke
   - 1 phrase per beat
   - Match timing to voice, not to raw Seedance output

8. Package outputs.
   - final MP4
   - prompt files
   - reference image list
   - voice script
   - subtitle/telop file
   - job JSON
   - result URLs
   - cost log
   - usage notes

## Anti-AI-Look Prompt Rules

Use these when generating additional cast:

- Prefer "ordinary smartphone photo" over "beautiful model portrait".
- Include slight facial asymmetry, real ambient light, natural pores, ordinary background.
- Avoid `perfect`, `idol`, `model`, `polished`, `airbrushed`, `high-end editorial`, and `small face`.
- For paid ads, keep cast realistic and avoid fake testimonial wording.

## Safety

- Generated cast can be reused as fictional actors.
- The first blond male guide is removed from active use and must not be selected as a default reference.
- Do not claim they are real customers or real influencers.
- Do not imitate celebrities or named public figures.
- Public or paid use requires platform, AIGC, rights, and claims review.
