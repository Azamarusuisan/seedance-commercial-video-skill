#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

NARRATION_TEXT_FILE="${NARRATION_TEXT_FILE:-workspace/prompts/narration-v1.txt}"
LANGUAGE="${NARRATION_LANGUAGE:-ja}"
VOICE_ID="${ELEVENLABS_VOICE_ID:-}"
OUT_FILE="${NARRATION_OUT:-workspace/assets/audio/narration-v1.mp3}"
LOG_PATH="${NARRATION_LOG:-$LOG_DIR/narration-status.json}"
REQ_PATH="${REQ_PATH:-$MCP_REQUEST_DIR/elevenlabs-narration.request.json}"

if [ ! -f "$NARRATION_TEXT_FILE" ]; then
  write_status_json "$LOG_PATH" "Higgsfield MCP ElevenLabs narration" "blocked" "Narration text file not found: $NARRATION_TEXT_FILE"
  log_warn "Missing narration text file: $NARRATION_TEXT_FILE (see workspace/prompts/narration-generic-template.txt)"
  exit 1
fi

approval_gate "$NARRATION_TEXT_FILE" "$LOG_PATH" "Higgsfield MCP ElevenLabs narration"

if [ -z "$VOICE_ID" ]; then
  log_warn "ELEVENLABS_VOICE_ID is not set. Choose a voice through the Higgsfield MCP tool before running this request."
fi

mkdir -p "$REPO_ROOT/$(dirname "$OUT_FILE")"

voice_arg=""
if [ -n "$VOICE_ID" ]; then
  voice_arg="voice_id=$VOICE_ID"
fi

write_mcp_request_with_prompt \
  "$REQ_PATH" \
  "higgsfield_mcp.elevenlabs_tts" \
  "Higgsfield MCP: generate ElevenLabs narration audio" \
  "$LOG_PATH" \
  "$NARRATION_TEXT_FILE" \
  "language=$LANGUAGE" \
  "output_file=$OUT_FILE" \
  "$voice_arg"

write_status_json "$LOG_PATH" "Higgsfield MCP ElevenLabs narration" "pending_mcp_execution" "Prepared MCP request at $REQ_PATH. Run it with the host-provided Higgsfield MCP tool, then record the sanitized result with: bash workspace/scripts/record-mcp-json.sh narration <mcp-response.json>"

log_info "Prepared ElevenLabs narration MCP request: $REQ_PATH"
log_info "This shell does not call ElevenLabs directly and does not store an ElevenLabs API key. Use the Higgsfield MCP tool exposed by the host agent."
