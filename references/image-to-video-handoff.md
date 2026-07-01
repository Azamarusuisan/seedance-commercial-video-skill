# Image-To-Video Handoff

This guide documents the intended path from generated/reference image to Higgsfield Seedance video.

## What Is Already Wired

- `workspace/scripts/gpt-image-reference.sh` can create a reference image from a prompt file and save it to `workspace/assets/reference-image-v1.png`.
- `workspace/scripts/_common.sh` resolves the reference image in this order:
  1. `IMAGE_FILE`, when explicitly provided.
  2. `workspace/assets/reference-image-v1.png`.
  3. `workspace/assets/reference-keiba-ai-gptimage-v1.png`.
  4. `workspace/assets/reference-keiba-ai-v1.png`.
- `workspace/scripts/seedance-cost.sh` and `workspace/scripts/seedance-generate.sh` include `image=<resolved path>` in the Higgsfield MCP request when that image exists, and now call `workspace/scripts/validate-seedance-input.py` first (see "Blender Is Never A Direct Reference" below).
- The scripts do not execute a local Higgsfield CLI. They prepare request JSON for the host-provided Higgsfield MCP tool.

## Blender Is Never A Direct Reference (`references/known-failure-patterns.md` FP-001)

**A raw Blender previs render must never become `IMAGE_FILE` / Seedance `start_image`/`end_image` directly.** This was tried for real (lipstick CM, 2026-07-01) and failed: the low-poly/blockout look, viewport lighting, and placeholder materials all carried through into the final video instead of being replaced with photoreal quality.

- Blender's role is `composition_only`: camera angle, framing, object placement, scale relationships, shot continuity, rough motion intent. It is a design/structure reference, not a visual/image reference.
- Optional first step if the user wants Blender-derived composition: run `command -v blender`, ask once "Blenderを使うとこのクオリティが出ます。使用しますか?", and if yes, create a local Blender previs render (`workspace/blender/action_movie_previs.py` as the base) under `workspace/assets/` or `workspace/projects/<id>/shots/<id>/`.
- **That render is not usable as `IMAGE_FILE` by itself.** It must go through GPT Image / Higgsfield image generation (`workspace/prompts/templates/gpt-image-from-blender-previs.txt`) to produce a photoreal storyboard frame / key visual first. Only the generated, human-approved photoreal image may become `IMAGE_FILE`.
- `workspace/scripts/seedance-cost.sh` / `seedance-generate.sh` call `workspace/scripts/validate-seedance-input.py` before building any request. It blocks `asset_kind=blender_previs` (see `workspace/schemas/asset-manifest.schema.json`), and also blocks images whose path looks like a Blender render/blend file even without an explicit manifest. Set `ASSET_MANIFEST=<path>` alongside `IMAGE_FILE` to declare an asset's kind explicitly once you have one.
- Allowed `IMAGE_FILE` asset kinds once approved: `approved_storyboard_frame`, `photoreal_key_visual`, `rights_confirmed_user_asset`, `approved_product_reference`.

```bash
# 1. Generate or update a reference image (or a photoreal key visual derived from Blender
#    composition, per "Blender Is Never A Direct Reference" above).
GPT_IMAGE_PROMPT_FILE=workspace/prompts/reference-image-v1.txt \
GPT_IMAGE_OUT=workspace/assets/reference-image-v1.png \
bash workspace/scripts/gpt-image-reference.sh

# 2. Prepare a cost request using the reference image. APPROVED=1 is not a formality — only set
#    it after the brief, prompt, reference image/assets, rights, and budget are actually approved.
IMAGE_FILE=workspace/assets/reference-image-v1.png \
ASSET_MANIFEST=workspace/schemas/asset-manifest.schema.json \
PROMPT_FILE=workspace/prompts/seedance-video-v1.txt \
ASPECT_RATIO=9:16 \
APPROVED={{SET_TO_1_ONLY_AFTER_GATE_CHECK}} \
bash workspace/scripts/seedance-cost.sh

# 3. Prepare a generation request using the same reference image. Same rule: APPROVED=1 only
#    after the gate check, never by default or by habit.
IMAGE_FILE=workspace/assets/reference-image-v1.png \
ASSET_MANIFEST=workspace/schemas/asset-manifest.schema.json \
PROMPT_FILE=workspace/prompts/seedance-video-v1.txt \
ASPECT_RATIO=9:16 \
APPROVED={{SET_TO_1_ONLY_AFTER_GATE_CHECK}} \
bash workspace/scripts/seedance-generate.sh
```

(`ASSET_MANIFEST` above is illustrative — point it at a real per-image manifest following `workspace/schemas/asset-manifest.schema.json`, not the schema file itself.)

## Approval Gates

Do not prepare cost or generation with `APPROVED=1` until:

- The brief is final.
- The reference image/assets are approved.
- Rights status is clear for the intended use.
- The prompt no longer contains `pending`, `proposal`, or `do not run` markers.
- Higgsfield login, paid/credit state, and model availability are checked through MCP.
- Budget and retry count are approved.

## Notes

- If `OPENAI_API_KEY` is missing, `gpt-image-reference.sh` blocks safely. Do not store the key in this repo.
- If a generated reference image is only a draft, label it as such in delivery notes.
- For multi-reference jobs, verify the current Higgsfield MCP media schema first. If uncertain, use one strong visual reference plus explicit text description in the prompt.
