#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

if [ "$#" -ne 1 ]; then
  cat >&2 <<'EOF'
Usage:
  bash workspace/scripts/prepare-storyboard-image-request.sh <path/to/visual-handoff.json>

Reads a visual-handoff.json (workspace/schemas/visual-handoff.schema.json) written by
build-visual-handoff.py, and prepares (does not execute) an image-generation MCP request for
the shot's storyboard prompt, via workspace/scripts/higgsfield-image.sh (the CLAUDE.md-preferred,
Higgsfield-authenticated route). No paid generation is executed by this script.
EOF
  exit 2
fi

HANDOFF_PATH="$1"
PERMISSION_PATH="${PERMISSION_MANIFEST:-${RUN_PERMISSION:-}}"

if [ ! -f "$HANDOFF_PATH" ]; then
  log_warn "visual-handoff.json not found: $HANDOFF_PATH"
  exit 1
fi

PROMPT_FILE="$(python3 -c "import json,sys; data=json.load(open(sys.argv[1])); print(data.get('storyboard_prompt_path') or data.get('output',{}).get('prompt_path',''))" "$HANDOFF_PATH")"
RENDER_PATH="$(python3 -c "import json,sys; data=json.load(open(sys.argv[1])); print(data.get('blender_source',{}).get('render_path') or data.get('source',{}).get('asset_path',''))" "$HANDOFF_PATH")"

if [ -z "$PROMPT_FILE" ] || [ ! -f "$PROMPT_FILE" ]; then
  log_warn "storyboard_prompt_path missing or not found in $HANDOFF_PATH: '$PROMPT_FILE'"
  exit 1
fi

if [ -z "$RENDER_PATH" ] || [ ! -f "$RENDER_PATH" ]; then
  log_warn "blender_source.render_path missing or not found in $HANDOFF_PATH: '$RENDER_PATH'"
  exit 1
fi

log_info "Preparing storyboard image-generation request (prepared_only; no paid generation executes here)."
log_info "Blender render (composition reference, never a Seedance input): $RENDER_PATH"
log_info "Storyboard prompt: $PROMPT_FILE"

if [ -z "$PERMISSION_PATH" ]; then
  log_warn "prepared_only: PERMISSION_MANIFEST/RUN_PERMISSION is missing. No MCP request JSON will be created."
  log_warn "Create a run permission manifest with allowed_actions.prepare_image_generation_request=true first."
  exit 0
fi

python3 - "$PERMISSION_PATH" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.is_file():
    print(f"[blocked] permission manifest not found: {path}", file=sys.stderr)
    raise SystemExit(1)
data = json.loads(path.read_text(encoding="utf-8"))
actions = data.get("allowed_actions", {})
if actions.get("prepare_image_generation_request") is not True and actions.get("prepare_gpt_image_storyboard_prompt") is not True:
    print("[blocked] permission manifest does not allow image request preparation", file=sys.stderr)
    raise SystemExit(1)
if actions.get("execute_image_generation") is True:
    print("[warning] execute_image_generation=true is present, but this script still only prepares a request.", file=sys.stderr)
PY

HIGGSFIELD_IMAGE_SOURCE_IMAGE="$RENDER_PATH" PROMPT_FILE="$PROMPT_FILE" bash workspace/scripts/higgsfield-image.sh

log_info "Prepared. This is prepared_only: run the request through the host Higgsfield MCP image tool, then update visual-handoff.json's storyboard_status and storyboard_image_path once a human approves the result."
