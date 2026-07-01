# Key Visual Generation Conditions

Status: image generation preapproval required.

Primary review surface:

- `workspace/projects/lipstick-cm-30s/storyboard/storyboard-board.html`
- `workspace/projects/lipstick-cm-30s/storyboard/storyboard-board.json`

This board must be reviewed before the four key visual prompts are sent to an image model.

## Required Outputs

| id | source | purpose | Seedance use | output |
|---|---|---|---|---|
| `clip_01_start_key` | Blender panel 01 | dark silhouette hook | Clip 1 start | `workspace/assets/references/lipstick-cm/keyvisuals/clip_01_start_key.png` |
| `clip_01_end_key` | Blender panel 03 | product hero | Clip 1 end | `workspace/assets/references/lipstick-cm/keyvisuals/clip_01_end_key.png` |
| `clip_02_lips_key` | Rina lips crop only | anonymous lips macro | Clip 2 start | `workspace/assets/references/lipstick-cm/keyvisuals/clip_02_lips_key.png` |
| `clip_02_final_key` | Blender panel 04 | final packshot / endcard-safe plate | Clip 2 end | `workspace/assets/references/lipstick-cm/keyvisuals/clip_02_final_key.png` |

## Conditions

- model: pending MCP image model confirmation
- provider route: Higgsfield MCP image generation request preparation only
- aspect ratio: `9:16`
- resolution: pending model confirmation
- estimated credits per image: pending MCP model/cost confirmation
- total estimated credits: pending MCP model/cost confirmation
- execute_image_generation: false
- execute_seedance_generation: false
- human_approval_status: pending
- stop condition: missing explicit image generation approval
- board_approval_status: pending

## Hard Blocks

- Do not pass Blender images to Seedance.
- Do not combine product and lips into one collage.
- Do not show full face, hand-held product, testimonial, influencer framing, or real brand logo.
- Do not bake text into generated images.
