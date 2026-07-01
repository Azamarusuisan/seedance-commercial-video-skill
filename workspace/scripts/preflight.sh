#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

log_info "repo_root=$REPO_ROOT"
log_info "git_status:"
git status --short || true

for required in \
  "SKILL.md" \
  "references/seedance-cm-workflow.md" \
  "references/image-to-video-handoff.md" \
  "skills/seedance/SKILL.md" \
  "skills/seedance/references/seedance-cm-workflow.md" \
  "skills/seedance/references/image-to-video-handoff.md" \
  "workspace/agent-guides/cross-agent-runbook.md" \
  "workspace/inputs/project-brief.md" \
  "workspace/briefs/cm-brief.md" \
  "workspace/prompts/reference-image-v1.txt" \
  "workspace/prompts/seedance-video-generic-template.txt" \
  "workspace/prompts/seedance-9x16-v1.txt"
do
  if [ -f "$required" ]; then
    log_info "found $required"
  else
    log_warn "missing $required"
  fi
done

for cmd in git rg python3; do
  if command -v "$cmd" >/dev/null 2>&1; then
    log_info "$cmd=$(command -v "$cmd")"
  else
    log_warn "$cmd missing"
  fi
done

if [ "${HIGGSFIELD_MCP_AVAILABLE:-0}" = "1" ]; then
  log_info "HIGGSFIELD_MCP_AVAILABLE=1"
else
  log_warn "Higgsfield MCP availability cannot be verified from this shell. Confirm it in the host agent's MCP tool list."
fi

if [ -n "${OPENAI_API_KEY:-}" ]; then
  log_info "OPENAI_API_KEY=present"
else
  log_warn "OPENAI_API_KEY=missing"
fi

image_file="$(default_image_file)"
if [ -f "$image_file" ]; then
  log_info "reference_image=$image_file"
else
  log_warn "reference image missing: $image_file"
fi

bash "$REPO_ROOT/workspace/scripts/secret-scan.sh"
