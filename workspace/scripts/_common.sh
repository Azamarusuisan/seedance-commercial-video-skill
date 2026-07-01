#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$REPO_ROOT/workspace/logs"
MCP_REQUEST_DIR="$REPO_ROOT/workspace/mcp-requests"

mkdir -p "$LOG_DIR"
mkdir -p "$MCP_REQUEST_DIR"

log_info() {
  printf '[info] %s\n' "$*"
}

log_warn() {
  printf '[warn] %s\n' "$*" >&2
}

require_repo() {
  if [ ! -f "$REPO_ROOT/SKILL.md" ]; then
    log_warn "Repository root could not be verified: $REPO_ROOT"
    exit 1
  fi
}

write_status_json() {
  local path="$1"
  local command_name="$2"
  local status="$3"
  local reason="$4"
  python3 - "$path" "$command_name" "$status" "$reason" <<'PY'
import datetime
import json
import sys

path, command_name, status, reason = sys.argv[1:5]
payload = {
    "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "command": command_name,
    "status": status,
    "reason": reason,
    "security_note": "No API key, token, cookie, session, password, or payment credential was saved."
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
}

write_mcp_request_json() {
  local path="$1"
  local request_type="$2"
  local tool_hint="$3"
  local output_log="$4"
  shift 4
  python3 - "$path" "$request_type" "$tool_hint" "$output_log" "$@" <<'PY'
import datetime
import json
import sys

path, request_type, tool_hint, output_log, *pairs = sys.argv[1:]
args = {}
for pair in pairs:
    key, sep, value = pair.partition("=")
    if not sep:
        continue
    if value in ("true", "false"):
        args[key] = value == "true"
    else:
        try:
            args[key] = int(value)
        except ValueError:
            args[key] = value

payload = {
    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "request_type": request_type,
    "tool_hint": tool_hint,
    "arguments": args,
    "output_log": output_log,
    "execution": "Run this with the Higgsfield MCP tool exposed by the host agent. Do not use the unrelated PyPI higgsfield package.",
    "security_note": "Do not save API keys, cookies, sessions, tokens, payment data, or raw browser storage."
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
}

write_mcp_request_with_prompt() {
  local path="$1"
  local request_type="$2"
  local tool_hint="$3"
  local output_log="$4"
  local prompt_file="$5"
  shift 5
  python3 - "$path" "$request_type" "$tool_hint" "$output_log" "$prompt_file" "$@" <<'PY'
import datetime
import json
import sys

path, request_type, tool_hint, output_log, prompt_file, *pairs = sys.argv[1:]
with open(prompt_file, "r", encoding="utf-8") as f:
    prompt = f.read()

args = {
    "prompt_file": prompt_file,
    "prompt": prompt,
}
for pair in pairs:
    key, sep, value = pair.partition("=")
    if not sep:
        continue
    if value in ("true", "false"):
        args[key] = value == "true"
    else:
        try:
            args[key] = int(value)
        except ValueError:
            args[key] = value

payload = {
    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "request_type": request_type,
    "tool_hint": tool_hint,
    "arguments": args,
    "output_log": output_log,
    "execution": "Run this with the Higgsfield MCP tool exposed by the host agent. Save the sanitized MCP response to output_log.",
    "security_note": "Do not save API keys, cookies, sessions, tokens, payment data, or raw browser storage."
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
}

redact_json_file() {
  local input="$1"
  local output="$2"
  python3 - "$input" "$output" <<'PY'
import datetime
import json
import sys

input_path, output_path = sys.argv[1:3]
blocked = ("token", "secret", "cookie", "password", "authorization", "api_key", "apikey", "session", "credential")

def redact(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if any(word in str(k).lower() for word in blocked):
                out[k] = "[REDACTED]"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    return obj

try:
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    payload = redact(data)
except Exception:
    payload = {
        "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "failed",
        "reason": "Command did not return valid JSON. Raw output was not saved."
    }

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
}

default_image_file() {
  if [ -n "${IMAGE_FILE:-}" ]; then
    printf '%s\n' "$IMAGE_FILE"
    return
  fi
  if [ -f "$REPO_ROOT/workspace/assets/reference-image-v1.png" ]; then
    printf '%s\n' "$REPO_ROOT/workspace/assets/reference-image-v1.png"
    return
  fi
  # No generic reference image. The keiba assets are a shipped sample, not a
  # universal default, so never adopt them silently: warn loudly so a fresh
  # project doesn't ship another project's image. Set IMAGE_FILE to override.
  local fallback="$REPO_ROOT/workspace/assets/reference-keiba-ai-v1.png"
  if [ -f "$REPO_ROOT/workspace/assets/reference-keiba-ai-gptimage-v1.png" ]; then
    fallback="$REPO_ROOT/workspace/assets/reference-keiba-ai-gptimage-v1.png"
  fi
  log_warn "No generic reference image at workspace/assets/reference-image-v1.png. Falling back to sample asset: $fallback. Set IMAGE_FILE=... to use your own."
  printf '%s\n' "$fallback"
}

approval_gate() {
  local prompt_file="$1"
  local log_path="$2"
  local command_name="$3"

  if [ "${APPROVED:-0}" != "1" ]; then
    write_status_json "$log_path" "$command_name" "blocked" "APPROVED=1 is required before cost or generation."
    log_warn "Blocked: set APPROVED=1 only after the user approves the final brief, prompt, reference image/assets, budget, and intended use."
    exit 2
  fi

  # grep, not rg: a safety gate must not fail open when ripgrep is absent.
  if grep -iE 'do not run|pending|proposal|not approved' "$prompt_file" >/dev/null 2>&1; then
    write_status_json "$log_path" "$command_name" "blocked" "Prompt still contains pending/proposal markers."
    log_warn "Blocked: remove pending/proposal markers from $prompt_file after final approval."
    exit 2
  fi
}
