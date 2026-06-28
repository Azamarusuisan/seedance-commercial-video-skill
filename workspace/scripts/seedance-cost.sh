#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

MODEL="${HIGGSFIELD_MODEL:-seedance_2_0}"
PROMPT_FILE="${PROMPT_FILE:-workspace/prompts/seedance-9x16-v1.txt}"
IMAGE_PATH="$(default_image_file)"
DURATION="${DURATION:-15}"
RESOLUTION="${RESOLUTION:-1080p}"
BITRATE_MODE="${BITRATE_MODE:-high}"
GENERATE_AUDIO="${GENERATE_AUDIO:-false}"
MODE="${MODE:-std}"
LOG_PATH="$LOG_DIR/cost-estimate.json"
REQ_PATH="$MCP_REQUEST_DIR/seedance-cost.request.json"

approval_gate "$PROMPT_FILE" "$LOG_PATH" "Higgsfield MCP Seedance cost $MODEL"

image_arg=""
if [ -f "$IMAGE_PATH" ]; then
  image_arg="image=$IMAGE_PATH"
fi

write_mcp_request_with_prompt \
  "$REQ_PATH" \
  "higgsfield_mcp.generate_cost" \
  "Higgsfield MCP: estimate Seedance generation cost" \
  "workspace/logs/cost-estimate.json" \
  "$PROMPT_FILE" \
  "model=$MODEL" \
  "aspect_ratio=9:16" \
  "duration=$DURATION" \
  "resolution=$RESOLUTION" \
  "bitrate_mode=$BITRATE_MODE" \
  "generate_audio=$GENERATE_AUDIO" \
  "mode=$MODE" \
  "$image_arg"

write_status_json "$LOG_PATH" "Higgsfield MCP Seedance cost $MODEL" "pending_mcp_execution" "Prepared MCP request at workspace/mcp-requests/seedance-cost.request.json. Run it with the host-provided Higgsfield MCP tool."

log_info "Prepared Seedance cost MCP request: $REQ_PATH"
log_info "Run the request with Higgsfield MCP, then save the sanitized result to $LOG_PATH."

