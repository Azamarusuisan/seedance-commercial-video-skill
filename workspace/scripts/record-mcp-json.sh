#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

if [ "$#" -ne 2 ]; then
  cat >&2 <<'EOF'
Usage:
  bash workspace/scripts/record-mcp-json.sh <account|model|cost|job> <mcp-response.json>

This records a sanitized Higgsfield MCP JSON response into the standard workspace log.
Do not pass files containing cookies, sessions, tokens, payment data, or browser storage exports.
EOF
  exit 2
fi

kind="$1"
input="$2"

if [ ! -f "$input" ]; then
  log_warn "Input file not found: $input"
  exit 1
fi

case "$kind" in
  account)
    output="$LOG_DIR/account-status.json"
    ;;
  model)
    output="$LOG_DIR/model-seedance_2_0.json"
    ;;
  cost)
    output="$LOG_DIR/cost-estimate.json"
    ;;
  job)
    output="$LOG_DIR/job-v1.json"
    ;;
  *)
    log_warn "Unknown kind: $kind"
    exit 2
    ;;
esac

redact_json_file "$input" "$output"
log_info "Wrote sanitized MCP response to $output"

if [ "$kind" = "job" ]; then
  python3 - "$output" "$LOG_DIR/result-urls.md" <<'PY'
import json
import sys

job_log, url_log = sys.argv[1:3]
with open(job_log, "r", encoding="utf-8") as f:
    data = json.load(f)

urls = []
def walk(obj):
    if isinstance(obj, dict):
        for value in obj.values():
            walk(value)
    elif isinstance(obj, list):
        for value in obj:
            walk(value)
    elif isinstance(obj, str) and obj.startswith(("http://", "https://")):
        urls.append(obj)

walk(data)
deduped = []
for url in urls:
    if url not in deduped:
        deduped.append(url)

with open(url_log, "w", encoding="utf-8") as f:
    f.write("# Result URLs\n\n")
    if deduped:
        for url in deduped:
            f.write(f"- {url}\n")
    else:
        f.write("No result URL found in sanitized MCP job JSON.\n")
PY
  log_info "Updated $LOG_DIR/result-urls.md"
fi

