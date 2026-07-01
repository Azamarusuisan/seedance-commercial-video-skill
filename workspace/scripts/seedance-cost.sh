#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

MODEL="${HIGGSFIELD_MODEL:-seedance_2_0}"
PROMPT_FILE="${PROMPT_FILE:-workspace/prompts/seedance-9x16-v1.txt}"
IMAGE_PATH="$(default_image_file)"
ASPECT_RATIO="${ASPECT_RATIO:-9:16}"
DURATION="${DURATION:-15}"
RESOLUTION="${RESOLUTION:-1080p}"
BITRATE_MODE="${BITRATE_MODE:-high}"
GENERATE_AUDIO="${GENERATE_AUDIO:-false}"
MODE="${MODE:-std}"
LOG_PATH="${COST_LOG:-$LOG_DIR/cost-estimate.json}"
REQ_PATH="${REQ_PATH:-$MCP_REQUEST_DIR/seedance-cost.request.json}"
PERMISSION_PATH="${PERMISSION_MANIFEST:-${RUN_PERMISSION:-}}"
LEARNING_PREFLIGHT="${LEARNING_PREFLIGHT:-}"
DRY_RUN="${DRY_RUN:-0}"

if [ "$DRY_RUN" != "1" ]; then
  approval_gate "$PROMPT_FILE" "$LOG_PATH" "Higgsfield MCP Seedance cost $MODEL"
fi

image_arg=""
if [ ! -f "$IMAGE_PATH" ]; then
  write_status_json "$LOG_PATH" "Higgsfield MCP Seedance cost $MODEL" "blocked" "IMAGE_FILE is required and was not found: $IMAGE_PATH"
  log_warn "Blocked: IMAGE_FILE is required and must point to an approved photoreal storyboard/key visual."
  exit 1
fi
if [ -z "${ASSET_MANIFEST:-}" ]; then
  write_status_json "$LOG_PATH" "Higgsfield MCP Seedance cost $MODEL" "blocked" "ASSET_MANIFEST is required."
  log_warn "Blocked: set ASSET_MANIFEST to the approved key-visual asset manifest."
  exit 1
fi
if [ -z "$PERMISSION_PATH" ]; then
  write_status_json "$LOG_PATH" "Higgsfield MCP Seedance cost $MODEL" "blocked" "PERMISSION_MANIFEST or RUN_PERMISSION is required."
  log_warn "Blocked: set PERMISSION_MANIFEST/RUN_PERMISSION before preparing Seedance requests."
  exit 1
fi
learning_args=()
if [ -n "$LEARNING_PREFLIGHT" ]; then
  learning_args=(--learning-preflight "$LEARNING_PREFLIGHT")
fi
if ! python3 "$REPO_ROOT/workspace/scripts/validate-seedance-input.py" \
  --image "$IMAGE_PATH" \
  --asset-manifest "$ASSET_MANIFEST" \
  --permission-manifest "$PERMISSION_PATH" \
  ${learning_args[@]+"${learning_args[@]}"}; then
  write_status_json "$LOG_PATH" "Higgsfield MCP Seedance cost $MODEL" "blocked" "validate-seedance-input.py rejected IMAGE_FILE=$IMAGE_PATH. See references/known-failure-patterns.md FP-001."
  exit 1
fi
image_arg="image=$IMAGE_PATH"

if [ "$DRY_RUN" = "1" ]; then
  write_status_json "$LOG_PATH" "Higgsfield MCP Seedance cost $MODEL" "dry_run_validated" "Validation passed. DRY_RUN=1: no MCP request JSON was created."
  log_info "DRY_RUN=1: validation passed; no Seedance cost request was created."
  log_info "Would prepare: model=$MODEL image=$IMAGE_PATH prompt=$PROMPT_FILE aspect_ratio=$ASPECT_RATIO duration=$DURATION resolution=$RESOLUTION bitrate_mode=$BITRATE_MODE"
  exit 0
fi

write_mcp_request_with_prompt \
  "$REQ_PATH" \
  "higgsfield_mcp.generate_cost" \
  "Higgsfield MCP: estimate Seedance generation cost" \
  "$LOG_PATH" \
  "$PROMPT_FILE" \
  "model=$MODEL" \
  "aspect_ratio=$ASPECT_RATIO" \
  "duration=$DURATION" \
  "resolution=$RESOLUTION" \
  "bitrate_mode=$BITRATE_MODE" \
  "generate_audio=$GENERATE_AUDIO" \
  "mode=$MODE" \
  "$image_arg"

write_status_json "$LOG_PATH" "Higgsfield MCP Seedance cost $MODEL" "pending_mcp_execution" "Prepared MCP request at $REQ_PATH. Run it with the host-provided Higgsfield MCP tool."

log_info "Prepared Seedance cost MCP request: $REQ_PATH"
log_info "Run the request with Higgsfield MCP, then save the sanitized result to $LOG_PATH."
