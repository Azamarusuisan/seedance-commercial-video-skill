# Lipstick CM Seedance Conditions

Status:
- Reference image and camera storyboard approved by user.
- Cost estimate completed on 2026-07-01.
- Paid Seedance generation is not approved yet.

## Video Generation

- Model: `seedance_2_0`
- Mode: image-to-video
- Count: 2 clips
- Duration: 15 seconds each, 30 seconds total
- Primary format: `9:16`
- Resolution target: recommended `1080p`; optional `720p` if user wants the lowest draft cost; `4k` is available but expensive
- Bitrate mode: `high`
- Seedance audio: `generate_audio=false`
- Visual quality target: high-brand luxury cosmetics commercial, not casual SNS beauty content

## Non-Negotiable Flesh-Out Rule

Seedance must flesh out the approved Blender storyboard. It must not invent a different lipstick ad.

Preserve:
- same product silhouette
- same black lacquer tube and gold rings
- same deep red bullet
- same vertical 9:16 packshot framing
- same dark stage geometry
- same orbit light rings, floating particles, and anamorphic light blades
- same camera-cut logic from the Blender panels

Add on top:
- Hollywood-level CG polish
- premium macro reflections
- volumetric light and champagne glow
- shallow depth of field
- controlled lens bloom
- high-brand cosmetics pacing
- refined motion and cut timing

## Clip 1

- Time: 0-15s
- Prompt: `workspace/prompts/lipstick-cm/final/clip_01_0-15s_9x16_seedance_final.txt`
- Primary reference: `workspace/assets/3d/renders/lipstick_cm_previs.png`
- Camera storyboard:
  - `workspace/assets/3d/renders/lipstick_cm_panel_01_silhouette.png`
  - `workspace/assets/3d/renders/lipstick_cm_panel_02_cap_macro.png`
  - `workspace/assets/3d/renders/lipstick_cm_panel_03_hero_vfx.png`
- Output path: `workspace/outputs/lipstick-cm-30s/clip_01_9x16.mp4`
- Log path: `workspace/logs/lipstick-cm-clip_01.json`

## Clip 2

- Time: 15-30s
- Prompt: `workspace/prompts/lipstick-cm/final/clip_02_15-30s_9x16_seedance_final.txt`
- Primary reference: `workspace/assets/references/lipstick-cm/clip_02_product_plus_rina_lips_clean.png`
- Lips reference only: `workspace/assets/cast/generated_20260629/rina_hayun_lips_closeup.png`
- Camera storyboard:
  - `workspace/assets/3d/renders/lipstick_cm_panel_03_hero_vfx.png`
  - `workspace/assets/3d/renders/lipstick_cm_panel_04_negative_space_tag.png`
- Output path: `workspace/outputs/lipstick-cm-30s/clip_02_9x16.mp4`
- Log path: `workspace/logs/lipstick-cm-clip_02.json`

## Audio / BGM / SFX

Seedance video generation remains silent. High-brand sound is handled after the videos are approved.

- Narration: none by default
- Optional whisper line, only if approved later: `ROUGE NOIR。静けさの中に、色気を。`
- BGM: minimal luxury score, 30 seconds, slow pulse, airy pad, sparse piano or glass-like tone, no pop beat, no loud melody
- SFX: soft cap lift, metal shimmer, gloss sweep, subtle particle sparkle, low cinematic tail at the final hero frame
- Tooling: Palmier Pro `generate_audio` for BGM/SFX only, after model specs and cost impact are shown to the user

## Cost Estimate

Credits before generation: `996.8`

| Option | Clip 1 | Clip 2 | Total | Remaining | Recommendation |
|---|---:|---:|---:|---:|---|
| `4k/high` | 330 | 330 | 660 | 336.8 | Best quality, high cost |
| `1080p/high` | 135 | 135 | 270 | 726.8 | Recommended lower-cost production option |
| `720p/high` | 67 | 67 | 134 | 862.8 | Cheapest review draft, lower finish quality |

Use `1080p/high` unless the user explicitly chooses `720p/high` or `4k/high`.

Generation command must still wait for final human permission. Cost approval is not the same as generation approval.

## Rights / Safety

- `ROUGE NOIR` is a placeholder fictional brand.
- Do not copy Dior logos, packaging, type, trade dress, or product names.
- Rina Hayun is a fictional AI-generated adult cast reference.
- Use Rina Hayun only for lips/skin-tone reference in Clip 2.
- Do not show full face, selfie background, hand-held product, customer testimonial, influencer endorsement, celebrity framing, or medical/beauty-effect claims.

## Next Approval

Next step is final paid-generation permission, not automatic generation.

Ask:
`1080p/high、合計270 creditsでSeedance 2本を生成して`

Alternative:
`720p/high、合計134 creditsでSeedance 2本を生成して`
