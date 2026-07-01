#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

IMAGE_GEN="${IMAGE_GEN:-${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/image_gen.py}"
PROMPT_FILE="${GPT_IMAGE_PROMPT_FILE:-workspace/prompts/reference-image-v1.txt}"
OUT_FILE="${GPT_IMAGE_OUT:-workspace/assets/reference-image-v1.png}"
MODEL="${GPT_IMAGE_MODEL:-gpt-image-2}"
SIZE="${GPT_IMAGE_SIZE:-1024x1536}"
QUALITY="${GPT_IMAGE_QUALITY:-high}"
SOURCE_IMAGE="${GPT_IMAGE_SOURCE_IMAGE:-${GPT_IMAGE_IMAGE:-}}"
SOURCE_IMAGES="${GPT_IMAGE_SOURCE_IMAGES:-}"
MASK_IMAGE="${GPT_IMAGE_MASK:-}"
INPUT_FIDELITY="${GPT_IMAGE_INPUT_FIDELITY:-high}"
LOG_PATH="$LOG_DIR/gpt-image-cli-status.json"

if [ ! -f "$IMAGE_GEN" ]; then
  write_status_json "$LOG_PATH" "GPT Image reference generation" "blocked" "image_gen.py was not found."
  log_warn "Missing image generation CLI: $IMAGE_GEN"
  exit 1
fi

if [ ! -f "$PROMPT_FILE" ]; then
  write_status_json "$LOG_PATH" "GPT Image reference generation" "blocked" "Prompt file was not found: $PROMPT_FILE"
  log_warn "Missing reference-image prompt file: $PROMPT_FILE"
  exit 1
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  write_status_json "$LOG_PATH" "GPT Image reference generation" "blocked" "OPENAI_API_KEY is not present in the shell environment."
  log_warn "OPENAI_API_KEY is missing. Export it for this shell only, then rerun. Do not write it to .env."
  exit 2
fi

if [ -n "$SOURCE_IMAGE" ] && [ ! -f "$SOURCE_IMAGE" ]; then
  write_status_json "$LOG_PATH" "GPT Image reference generation" "blocked" "Source image was not found: $SOURCE_IMAGE"
  log_warn "Missing source image: $SOURCE_IMAGE"
  exit 1
fi

# Multi-image edit (references/cli.md: "pass repeated --image flags. Their order is
# meaningful, so describe each image by index and role in the prompt."). One path per
# line in GPT_IMAGE_SOURCE_IMAGES; takes priority over the single-image variables above.
image_args=()
if [ -n "$SOURCE_IMAGES" ]; then
  while IFS= read -r img; do
    [ -z "$img" ] && continue
    if [ ! -f "$img" ]; then
      write_status_json "$LOG_PATH" "GPT Image reference generation" "blocked" "Source image was not found: $img"
      log_warn "Missing source image: $img"
      exit 1
    fi
    image_args+=(--image "$img")
  done <<< "$SOURCE_IMAGES"
elif [ -n "$SOURCE_IMAGE" ]; then
  image_args=(--image "$SOURCE_IMAGE")
fi

if [ -n "$MASK_IMAGE" ] && [ ! -f "$MASK_IMAGE" ]; then
  write_status_json "$LOG_PATH" "GPT Image reference generation" "blocked" "Mask image was not found: $MASK_IMAGE"
  log_warn "Missing mask image: $MASK_IMAGE"
  exit 1
fi

force_args=()
if [ "${FORCE:-0}" = "1" ]; then
  force_args=(--force)
fi

if [ "${#image_args[@]}" -gt 0 ]; then
  mask_args=()
  if [ -n "$MASK_IMAGE" ]; then
    mask_args=(--mask "$MASK_IMAGE")
  fi
  python3 "$IMAGE_GEN" edit \
    --model "$MODEL" \
    --prompt-file "$PROMPT_FILE" \
    ${image_args[@]+"${image_args[@]}"} \
    ${mask_args[@]+"${mask_args[@]}"} \
    --input-fidelity "$INPUT_FIDELITY" \
    --size "$SIZE" \
    --quality "$QUALITY" \
    --out "$OUT_FILE" \
    ${force_args[@]+"${force_args[@]}"}
else
  python3 "$IMAGE_GEN" generate \
    --model "$MODEL" \
    --prompt-file "$PROMPT_FILE" \
    --size "$SIZE" \
    --quality "$QUALITY" \
    --out "$OUT_FILE" \
    ${force_args[@]+"${force_args[@]}"}
fi

write_status_json "$LOG_PATH" "GPT Image reference generation" "generated" "Generated $OUT_FILE with $MODEL."
log_info "Generated GPT Image reference: $OUT_FILE"
