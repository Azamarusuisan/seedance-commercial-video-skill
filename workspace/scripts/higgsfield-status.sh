#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

ACCOUNT_LOG="$LOG_DIR/account-status.json"
MODEL_LOG="$LOG_DIR/model-seedance_2_0.json"
ACCOUNT_REQ="$MCP_REQUEST_DIR/account-status.request.json"
MODEL_REQ="$MCP_REQUEST_DIR/model-seedance_2_0.request.json"

write_mcp_request_json \
  "$ACCOUNT_REQ" \
  "higgsfield_mcp.account_status" \
  "Higgsfield MCP: account/status, current user, plan, credits, login state" \
  "workspace/logs/account-status.json"

write_mcp_request_json \
  "$MODEL_REQ" \
  "higgsfield_mcp.model_get" \
  "Higgsfield MCP: get model metadata for seedance_2_0" \
  "workspace/logs/model-seedance_2_0.json" \
  "model=seedance_2_0"

write_status_json "$ACCOUNT_LOG" "Higgsfield MCP account status" "pending_mcp_execution" "Prepared MCP request at workspace/mcp-requests/account-status.request.json. Run it with the host-provided Higgsfield MCP tool after manual login."
write_status_json "$MODEL_LOG" "Higgsfield MCP model get seedance_2_0" "pending_mcp_execution" "Prepared MCP request at workspace/mcp-requests/model-seedance_2_0.request.json. Run it with the host-provided Higgsfield MCP tool."

log_info "Prepared Higgsfield MCP status requests:"
log_info "$ACCOUNT_REQ"
log_info "$MODEL_REQ"
log_info "This shell does not call a local higgsfield CLI. Use the Higgsfield MCP tool exposed by the agent host."

