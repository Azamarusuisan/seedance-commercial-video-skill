#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

MODEL="${HIGGSFIELD_IMAGE_MODEL:-image2}"
PROMPT_FILE="${PROMPT_FILE:-workspace/prompts/reference-image-v1.txt}"
SOURCE_IMAGE="${IMAGE_FILE:-${HIGGSFIELD_IMAGE_SOURCE_IMAGE:-}}"
SOURCE_IMAGES="${HIGGSFIELD_IMAGE_SOURCE_IMAGES:-}"
OUT_FILE="${IMAGE_OUT:-workspace/assets/reference-image-v1.png}"
ASPECT_RATIO="${ASPECT_RATIO:-9:16}"
LOG_PATH="${IMAGE_LOG:-$LOG_DIR/image-result.json}"
REQ_PATH="${REQ_PATH:-$MCP_REQUEST_DIR/higgsfield-image.request.json}"

if [ ! -f "$PROMPT_FILE" ]; then
  write_status_json "$LOG_PATH" "Higgsfield MCP image generation $MODEL" "blocked" "Prompt file was not found: $PROMPT_FILE"
  log_warn "Missing image prompt file: $PROMPT_FILE"
  exit 1
fi

approval_gate "$PROMPT_FILE" "$LOG_PATH" "Higgsfield MCP image generation $MODEL"

# Multi-image input (references/known-failure-patterns.md FP-004). One "path:role" pair
# per line in HIGGSFIELD_IMAGE_SOURCE_IMAGES, e.g. "workspace/assets/x.png:product hero
# reference". Higgsfield MCP's real multi-reference schema is unverified (unlike GPT
# Image's documented repeated --image flags), so this is expressed as indexed
# image_N / image_N_role request fields for a human/host to map onto the real API.
image_pairs=()
if [ -n "$SOURCE_IMAGES" ]; then
  index=0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    index=$((index + 1))
    img="${line%%:*}"
    role="${line#*:}"
    if [ "$role" = "$line" ]; then
      role=""
    fi
    if [ ! -f "$img" ]; then
      write_status_json "$LOG_PATH" "Higgsfield MCP image generation $MODEL" "blocked" "Source image was not found: $img"
      log_warn "Missing source image: $img"
      exit 1
    fi
    image_pairs+=("image_${index}=$img")
    if [ -n "$role" ]; then
      image_pairs+=("image_${index}_role=$role")
    fi
  done <<< "$SOURCE_IMAGES"
elif [ -n "$SOURCE_IMAGE" ]; then
  if [ ! -f "$SOURCE_IMAGE" ]; then
    write_status_json "$LOG_PATH" "Higgsfield MCP image generation $MODEL" "blocked" "Source image was not found: $SOURCE_IMAGE"
    log_warn "Missing source image: $SOURCE_IMAGE"
    exit 1
  fi
  image_pairs=("image=$SOURCE_IMAGE")
fi

mkdir -p "$REPO_ROOT/$(dirname "$OUT_FILE")"

write_mcp_request_with_prompt \
  "$REQ_PATH" \
  "higgsfield_mcp.image_generate" \
  "Higgsfield MCP: generate storyboard/reference image" \
  "$LOG_PATH" \
  "$PROMPT_FILE" \
  "model=$MODEL" \
  "aspect_ratio=$ASPECT_RATIO" \
  "output_file=$OUT_FILE" \
  "${image_pairs[@]}"

write_status_json "$LOG_PATH" "Higgsfield MCP image generation $MODEL" "pending_mcp_execution" "Prepared MCP request at $REQ_PATH. Run it with the host-provided Higgsfield MCP image tool, then record the sanitized result with: bash workspace/scripts/record-mcp-json.sh image <mcp-response.json>"

log_info "Prepared Higgsfield image MCP request: $REQ_PATH"
log_info "Model name and single-vs-multi-image input support must be verified in the connected Higgsfield MCP environment (references/known-failure-patterns.md FP-004)."
