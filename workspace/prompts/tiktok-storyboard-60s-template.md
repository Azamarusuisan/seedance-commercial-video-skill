# 60s TikTok Storyboard Script Template

Status: planning template. Do not run paid generation until the storyboard, rights notes, budget, voice route, and subtitle route are approved.

Project:
`{project_name}`

Platform / format:
`9:16`, `{duration_seconds}s`, `{target_platform}`

Story premise:
`{one_sentence_story}`

Cast manifest:
`workspace/assets/cast/cast-manifest.json`

Voice route:
`External TTS / Higgsfield ElevenLabs / exact Japanese narration`

Subtitle route:
`Post-production Japanese telop/subtitles. Do not ask Seedance to render readable subtitles.`

Seedance audio:
`generate_audio=false`

Rights status:
`{internal_draft_only | user_confirmed_publication_rights | licensed_assets | mixed_pending_confirmation}`

## Panels

| # | Time | Clip Group | Cast | Location | Primary Reference | Camera | Visible Action | Japanese Narration | Planned Subtitle/Telop | Next-Scene Reason |
|---|---:|---|---|---|---|---|---|---|---|---|
| 1 | 0-5s | 1 | `{cast_id}` | `{location}` | `{asset_path}` | handheld push-in | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{why_next}` |
| 2 | 5-10s | 1 | `{cast_id}` | `{location}` | `{asset_path}` | `{camera}` | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{why_next}` |
| 3 | 10-15s | 1 | `{cast_id}` | `{location}` | `{asset_path}` | `{camera}` | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{why_next}` |
| 4 | 15-22s | 2 | `{cast_id}` | `{location}` | `{asset_path}` | `{camera}` | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{why_next}` |
| 5 | 22-30s | 2 | `{cast_id}` | `{location}` | `{asset_path}` | `{camera}` | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{why_next}` |
| 6 | 30-38s | 3 | `{cast_id}` | `{location}` | `{asset_path}` | `{camera}` | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{why_next}` |
| 7 | 38-45s | 3 | `{cast_id}` | `{location}` | `{asset_path}` | `{camera}` | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{why_next}` |
| 8 | 45-52s | 4 | `{cast_id}` | `{location}` | `{asset_path}` | `{camera}` | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{why_next}` |
| 9 | 52-58s | 4 | `{cast_id}` | `{location}` | `{asset_path}` | `{camera}` | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{why_next}` |
| 10 | 58-60s | 4 | `{cast_id}` | `{location}` | `{asset_path}` | close handheld loop | `{visual_action}` | `{spoken_line}` | `{short_telop}` | `{next_episode_hook}` |

## Collapse To Seedance Clips

After approval, convert the panels into four visual-only prompts:

1. `0-15s`: panels 1-3
2. `15-30s`: panels 4-5
3. `30-45s`: panels 6-7
4. `45-60s`: panels 8-10

Each Seedance prompt should include:

- one primary start image
- selected cast ID and role
- visual action only
- camera movement
- previous beat and next beat
- `No readable generated text`
- `Seedance visual-only; narration and subtitles will be added in editing`
