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
WAIT_TIMEOUT="${WAIT_TIMEOUT:-60m}"
WAIT_INTERVAL="${WAIT_INTERVAL:-10s}"
JOB_LOG="${JOB_LOG:-$LOG_DIR/job-v1.json}"
URL_LOG="${URL_LOG:-$LOG_DIR/result-urls.md}"
OUT_MP4="${OUT_MP4:-workspace/outputs/final-cm-v1.mp4}"
REQ_PATH="${REQ_PATH:-$MCP_REQUEST_DIR/seedance-generate.request.json}"

approval_gate "$PROMPT_FILE" "$JOB_LOG" "Higgsfield MCP Seedance generate $MODEL"

image_arg=""
if [ -f "$IMAGE_PATH" ]; then
  image_arg="image=$IMAGE_PATH"
fi

write_mcp_request_with_prompt \
  "$REQ_PATH" \
  "higgsfield_mcp.generate_create" \
  "Higgsfield MCP: create Seedance video job and wait for completion" \
  "$JOB_LOG" \
  "$PROMPT_FILE" \
  "model=$MODEL" \
  "aspect_ratio=$ASPECT_RATIO" \
  "duration=$DURATION" \
  "resolution=$RESOLUTION" \
  "bitrate_mode=$BITRATE_MODE" \
  "generate_audio=$GENERATE_AUDIO" \
  "mode=$MODE" \
  "wait=true" \
  "wait_timeout=$WAIT_TIMEOUT" \
  "wait_interval=$WAIT_INTERVAL" \
  "result_url_log=$URL_LOG" \
  "download_path=$OUT_MP4" \
  "$image_arg"

write_status_json "$JOB_LOG" "Higgsfield MCP Seedance generate $MODEL" "pending_mcp_execution" "Prepared MCP request at $REQ_PATH. Run it with the host-provided Higgsfield MCP tool."
# Single-job semantics: record-mcp-json.sh rewrites this file wholesale from the
# job JSON, so write a fresh placeholder here too. For multiple clips, override
# URL_LOG per clip instead of accumulating in one file.
cat > "$URL_LOG" <<EOF
# Result URLs

Pending Higgsfield MCP execution for $REQ_PATH.
After running the prepared Seedance generation MCP request, record the result URL here and download the MP4 to $OUT_MP4 if available.
EOF

log_info "Prepared Seedance generation MCP request: $REQ_PATH"
log_info "Run the request with Higgsfield MCP, then save sanitized job JSON to $JOB_LOG and result URLs to $URL_LOG."
