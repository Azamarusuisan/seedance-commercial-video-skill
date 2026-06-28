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

force_args=()
if [ "${FORCE:-0}" = "1" ]; then
  force_args=(--force)
fi

python3 "$IMAGE_GEN" generate \
  --model "$MODEL" \
  --prompt-file "$PROMPT_FILE" \
  --size "$SIZE" \
  --quality "$QUALITY" \
  --out "$OUT_FILE" \
  "${force_args[@]}"

write_status_json "$LOG_PATH" "GPT Image reference generation" "generated" "Generated $OUT_FILE with $MODEL."
log_info "Generated GPT Image reference: $OUT_FILE"
