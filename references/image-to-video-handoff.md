# Image-To-Video Handoff

This guide documents the intended path from generated/reference image to Higgsfield Seedance video.

## What Is Already Wired

- `workspace/scripts/gpt-image-reference.sh` can create a reference image from a prompt file and save it to `workspace/assets/reference-image-v1.png`.
- A local Blender previs render can also be used as the reference image when Blender is available and the user explicitly chooses it.
- `workspace/scripts/_common.sh` resolves the reference image in this order:
  1. `IMAGE_FILE`, when explicitly provided.
  2. `workspace/assets/reference-image-v1.png`.
  3. `workspace/assets/reference-keiba-ai-gptimage-v1.png`.
  4. `workspace/assets/reference-keiba-ai-v1.png`.
- `workspace/scripts/seedance-cost.sh` and `workspace/scripts/seedance-generate.sh` include `image=<resolved path>` in the Higgsfield MCP request when that image exists.
- The scripts do not execute a local Higgsfield CLI. They prepare request JSON for the host-provided Higgsfield MCP tool.

## Standard Flow

Optional first step:

- Run `command -v blender`.
- If Blender is available, ask once: "Blenderを使うとこのクオリティが出ます。使用しますか?"
- If yes, create one local Blender previs render using the heavy-path method (`workspace/blender/action_movie_previs.py` as the base, project-specific `bpy`, `blender --background --python`), save it under `workspace/assets/`, and use that file as `IMAGE_FILE`.
- If no, or Blender is not installed, use the existing generated/user-provided reference image route below.
- This does not add a new gate; the render is approved through the existing reference image/assets approval.

```bash
# 1. Generate or update a reference image.
GPT_IMAGE_PROMPT_FILE=workspace/prompts/reference-image-v1.txt \
GPT_IMAGE_OUT=workspace/assets/reference-image-v1.png \
bash workspace/scripts/gpt-image-reference.sh

# 2. Prepare a cost request using the reference image.
IMAGE_FILE=workspace/assets/reference-image-v1.png \
PROMPT_FILE=workspace/prompts/seedance-video-v1.txt \
ASPECT_RATIO=9:16 \
APPROVED=1 \
bash workspace/scripts/seedance-cost.sh

# 3. Prepare a generation request using the same reference image.
IMAGE_FILE=workspace/assets/reference-image-v1.png \
PROMPT_FILE=workspace/prompts/seedance-video-v1.txt \
ASPECT_RATIO=9:16 \
APPROVED=1 \
bash workspace/scripts/seedance-generate.sh
```

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
