# Lipstick CM Seedance Review — Failed Take

Date: 2026-07-01

## Result

The 2 generated Seedance clips are rejected.

They are technically valid outputs, but they do not meet the creative requirement.

- Model: `seedance_2_0`
- Resolution: `1080p`
- Bitrate: `high`
- Duration: 15s x 2
- Seedance audio: `generate_audio=false`
- Cost used: 270 credits total

## Files

- Clip 1 MP4: `workspace/outputs/lipstick-cm-30s/clip_01_9x16.mp4`
- Clip 2 MP4: `workspace/outputs/lipstick-cm-30s/clip_02_9x16.mp4`
- Clip 1 contact sheet: `workspace/outputs/lipstick-cm-30s/review_frames/clip_01_contact.jpg`
- Clip 2 contact sheet: `workspace/outputs/lipstick-cm-30s/review_frames/clip_02_contact.jpg`
- Clip 1 job JSON: `workspace/logs/lipstick-cm-clip_01.json`
- Clip 2 job JSON: `workspace/logs/lipstick-cm-clip_02.json`

## What Failed

- The Blender blockout look remained too visible.
- The background planes, simple geometry, rings, and particles stayed close to the raw previs.
- Clip 1 only gained some macro polish in the first seconds; the hero shot regressed to Blender-like CG.
- Clip 2 became a collage-like sequence: Blender product, realistic lips, Blender product.
- The lips reference appeared as a separate material insertion, not as an integrated luxury cosmetics scene.

## Root Cause

The workflow treated the Blender render as the direct Seedance `start_image`.

That is wrong for high-brand, photoreal cosmetics work. The Blender render is a storyboard/control image, not the final visual start frame. Passing a low-poly/blockout render directly causes Seedance to preserve the blockout instead of replacing it with luxury product photography.

The combined Clip 2 reference also overloaded one image with two unrelated visual targets: product blockout and lips crop. Seedance followed both literally, so the cut felt pasted together.

## Corrected Rule

Blender is the design source:

- product shape
- camera framing
- composition
- timing beats
- motion intent

Seedance input must be a beauty keyframe:

- photoreal luxury lipstick product shot
- black lacquer and champagne-gold material already polished
- realistic studio background, not visible blockout planes
- lips shot integrated as a planned shot, not pasted beside the product

Do not run another paid Seedance job until these keyframes are generated and approved.

## Next Fix

1. Create realistic key visuals from the Blender storyboard.
2. Show key visuals beside the original Blender panels.
3. Approve the key visuals.
4. Generate Seedance using the realistic key visuals as `start_image` and, where needed, `end_image`.
5. Keep Blender only as the structural reference, not the literal visual frame.
