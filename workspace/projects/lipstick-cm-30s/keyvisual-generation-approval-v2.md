# Key Visual Generation Approval v2

Current stage: image generation preapproval.

No paid image generation, Seedance generation, audio generation, or publishing has been executed by this package.

## Purpose

Create four photoreal key visuals from the approved composition sources. These images are not final videos. They are the only candidates that may become Seedance primary images after human approval.

The storyboard board is the review surface for the full flow before any paid generation:

- Board JSON: `workspace/projects/lipstick-cm-30s/storyboard/storyboard-board.json`
- Board HTML: `workspace/projects/lipstick-cm-30s/storyboard/storyboard-board.html`
- Rule: approve the board first, then generate/approve the four photoreal key visuals, then prepare Seedance.

## What Will Be Made

- 8-panel photoreal storyboard board.
- 4 primary key visuals for Seedance, after image generation and human approval.
- No Seedance video, audio, subtitle, Palmier edit, upscale, or publish action in this approval step.

## Shared Conditions

- Project: lipstick-cm-30s
- Format: 9:16
- Quality target: high-brand luxury cosmetics commercial
- Blender role: composition only / Seedance input not allowed
- Photoreal key visual role: visual truth / Seedance candidate after approval
- No baked text, no real logos, no third-party brands
- No full-face cast usage
- Rina Hayun reference is lips-only support, not a full-face or endorsement shot
- No audio, subtitle, or Palmier edit step starts until visual approval is done

## Requested Image Set

| key visual | source role | output path | approval |
|---|---|---|---|
| clip_01_start_key | Blender panel 01 composition | workspace/assets/references/lipstick-cm/keyvisuals/clip_01_start_key.png | pending |
| clip_01_end_key | Blender panel 03 composition | workspace/assets/references/lipstick-cm/keyvisuals/clip_01_end_key.png | pending |
| clip_02_lips_key | product world + Rina lips-only support | workspace/assets/references/lipstick-cm/keyvisuals/clip_02_lips_key.png | pending |
| clip_02_final_key | Blender panel 04 composition | workspace/assets/references/lipstick-cm/keyvisuals/clip_02_final_key.png | pending |

## Reference Assets

- Blender panel 01: `workspace/assets/3d/renders/lipstick_cm_panel_01_silhouette.png`
- Blender panel 02: `workspace/assets/3d/renders/lipstick_cm_panel_02_cap_macro.png`
- Blender panel 03: `workspace/assets/3d/renders/lipstick_cm_panel_03_hero_vfx.png`
- Blender panel 04: `workspace/assets/3d/renders/lipstick_cm_panel_04_negative_space_tag.png`
- Rina lips crop: `workspace/assets/cast/generated_20260629/rina_hayun_lips_closeup.png`

## Banned In This Step

- Blender image direct-to-Seedance.
- Product and lips combined into one collage.
- Full face, hand-held product, testimonial framing, influencer/customer framing.
- Real brand logos, third-party packaging, baked-in text, unsupported claims.

## Execution Check

- model: pending live Higgsfield MCP model confirmation
- provider route: Higgsfield MCP image generation, or prepared request JSON only
- output directory: `workspace/assets/references/lipstick-cm/keyvisuals/`
- aspect ratio: `9:16`
- resolution: pending model confirmation
- estimated credits per image: pending live cost check
- total estimated credits: pending live cost check
- execute_image_generation: false
- execute_seedance_generation: false
- user approval: pending

## Approval Question To Human

Approve only after seeing the generated key visuals side by side with their composition sources:

"この4枚の写実キービジュアルでOK。Seedance 2本の条件を提示して。"

After that, the system must show model, clip count, duration, resolution, bitrate, generate_audio flag, reference images, cost estimate, output paths, and permission manifest before final paid generation approval.
