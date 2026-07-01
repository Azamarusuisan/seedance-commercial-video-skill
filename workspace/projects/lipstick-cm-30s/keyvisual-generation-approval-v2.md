# Key Visual Generation Approval v2

Current stage: image generation preapproval.

No paid image generation, Seedance generation, audio generation, or publishing has been executed by this package.

## Purpose

Create four photoreal key visuals from the approved composition sources. These images are not final videos. They are the only candidates that may become Seedance primary images after human approval.

The storyboard board is the review surface for the full flow before any paid generation:

- Board JSON: `workspace/projects/lipstick-cm-30s/storyboard/storyboard-board.json`
- Board HTML: `workspace/projects/lipstick-cm-30s/storyboard/storyboard-board.html`
- Rule: approve the board first, then generate/approve the four photoreal key visuals, then prepare Seedance.

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

## Approval Question To Human

Approve only after seeing the generated key visuals side by side with their composition sources:

"この4枚の写実キービジュアルでOK。Seedance 2本の条件を提示して。"

After that, the system must show model, clip count, duration, resolution, bitrate, generate_audio flag, reference images, cost estimate, output paths, and permission manifest before final paid generation approval.
