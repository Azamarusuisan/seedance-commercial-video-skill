# Learning Materials — Failed Lipstick CM Seedance Run

Date: 2026-07-01

This file is safe to commit. It intentionally excludes tokens, cookies, account data, result URLs, and raw service logs.

## Included Visual Failure Examples

These files are committed as learning material because the user explicitly requested that the failed outputs be included.

| File | Purpose | SHA-256 |
|---|---|---|
| `workspace/outputs/lipstick-cm-30s/clip_01_9x16.mp4` | Failed Clip 1 video | `cbcf9ec30d9d099f77a6be2c043319719178129e25c09788242ac01b05d4cd52` |
| `workspace/outputs/lipstick-cm-30s/clip_02_9x16.mp4` | Failed Clip 2 video | `d7915b1e0ca46d057f5a8da60225a43d35edf772e5c393b9694dfa7c48c6a20e` |
| `workspace/outputs/lipstick-cm-30s/review_frames/clip_01_contact.jpg` | Failed Clip 1 contact sheet | `6cdcdcd756b319063f7a156c293e501ed0791bce3aca6655195e9b88201633ee` |
| `workspace/outputs/lipstick-cm-30s/review_frames/clip_02_contact.jpg` | Failed Clip 2 contact sheet | `98bc904eec621266560776c96b29f22a78e644dcd6ad158c49dde2db85b1b6ac` |

## Video Metadata

- Clip 1: 1080 x 1920, 24 fps, 15.041667 seconds
- Clip 2: 1080 x 1920, 24 fps, 15.041667 seconds
- Seedance audio: disabled
- Intended quality: high-brand luxury lipstick CM
- Actual review result: rejected

## Why Logs Are Not Committed

`workspace/logs/` is intentionally not committed.

Even if the current logs do not contain obvious secrets, service logs may contain:

- account identifiers
- cloud result URLs
- internal job IDs
- future auth/session fields
- provider-specific metadata that should not be treated as training material

For learning, use this sanitized file plus:

- `workspace/projects/lipstick-cm-30s/postmortem-20260701-blender-fleshout-mismatch.md`
- `workspace/projects/lipstick-cm-30s/review-20260701-seedance-failed.md`
- the committed MP4s and contact sheets listed above

## Failure Summary

The failed examples show what not to do:

- Do not pass raw Blender blockout renders directly as Seedance `start_image`.
- Do not expect prompt wording alone to transform low-poly previs into high-brand product photography.
- Do not combine product reference and lips reference into one literal collage image.
- Do not proceed to sound, subtitles, color, or Palmier Pro finishing after a visual review rejection.

Correct next step:

Create photoreal key visuals from the Blender storyboard first, show them to the user, and only then request any new paid video-generation approval.
