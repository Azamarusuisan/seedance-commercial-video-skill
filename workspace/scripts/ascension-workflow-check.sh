#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

STATE="workspace/ui/state/generation-state.json"
RUNBOOK="workspace/briefs/ascension-line-workflow-runbook.md"

fail=0

check_file() {
  local path="$1"
  local label="$2"
  if [ -s "$path" ]; then
    log_info "ok: $label -> $path"
  else
    log_warn "missing: $label -> $path"
    fail=1
  fi
}

check_file "$RUNBOOK" "workflow runbook"
check_file "workspace/assets/3d/blend/action_movie_previs.blend" "Blender blend"
check_file "workspace/assets/3d/renders/action_movie_previs.png" "Blender render"
check_file "workspace/briefs/3d-action-movie-ascension-60s-script.md" "narration script"
check_file "workspace/subtitles/ascension_line/caption-plan.json" "caption plan"
check_file "workspace/assets/storyboards/ascension_line/generated_storyboard_contact_sheet.png" "support storyboard"

jq -r '
  "current_work=" + (.current_work.title // "-"),
  "workflow_contract=" + (.workflow_contract.status // "missing"),
  "primary_source=" + (.workflow_contract.primary_source // "-"),
  "paid_generation_gate=" + (.workflow_contract.paid_generation_gate // "-"),
  "palmier=" + (.palmier.mcp_status // "-"),
  "voice=" + (.voice.status // "-"),
  "subtitles=" + (.subtitles.status // "-"),
  "jobs=" + ([.jobs[] | .id + ":" + .status] | join(", "))
' "$STATE"

contract_status="$(jq -r '.workflow_contract.status // "missing"' "$STATE")"
primary_source="$(jq -r '.workflow_contract.primary_source // ""' "$STATE")"
permission="$(jq -r '.approval_contract.current_permission // ""' "$STATE")"
primary_asset="$(jq -r '.source_lock.primary_assets.render_png.path // ""' "$STATE")"
support_role="$(jq -r '.source_lock.support_assets.generated_storyboard.role // ""' "$STATE")"
can_generate="$(jq -r 'if .computed | has("can_generate") then .computed.can_generate else "missing" end' "$STATE")"

if [ "$contract_status" != "locked_for_review" ]; then
  log_warn "workflow contract is not locked_for_review"
  fail=1
fi

if [ "$primary_source" != "Blender previs" ]; then
  log_warn "primary source must be Blender previs"
  fail=1
fi

if [ "$permission" != "not_granted_for_next_generation" ]; then
  log_warn "next generation permission should be blocked until explicit user approval"
  fail=1
fi

if [ "$primary_asset" != "workspace/assets/3d/renders/action_movie_previs.png" ]; then
  log_warn "source lock primary render must be Blender render"
  fail=1
fi

if [ "$support_role" != "support_reference_only" ]; then
  log_warn "generated storyboard must remain support_reference_only"
  fail=1
fi

if [ "$can_generate" != "false" ]; then
  log_warn "computed.can_generate must be false until a payload hash is approved"
  fail=1
fi

jq -e '
  [.jobs[] | select(.reference_image != "workspace/assets/3d/renders/action_movie_previs.png")] | length == 0
' "$STATE" >/dev/null || {
  log_warn "all Seedance jobs must use Blender render as primary reference"
  fail=1
}

jq -e '
  [.jobs[] | select((has("generate_audio") | not) or .generate_audio != false)] | length == 0
' "$STATE" >/dev/null || {
  log_warn "all Seedance jobs must keep generate_audio=false"
  fail=1
}

for clip in clip_01 clip_02; do
  local_path="$(jq -r --arg clip "$clip" '.jobs[] | select(.id == $clip) | .local_path // ""' "$STATE")"
  job_json="$(jq -r --arg clip "$clip" '.jobs[] | select(.id == $clip) | (.versions[0].job_json // "")' "$STATE")"
  check_file "$local_path" "$clip MP4"
  check_file "$job_json" "$clip job json"
  if command -v ffprobe >/dev/null 2>&1 && [ -s "$local_path" ]; then
    probe="$(ffprobe -v error -show_entries stream=index,codec_type,width,height -show_entries format=duration -of json "$local_path")"
    width="$(printf '%s' "$probe" | jq -r '[.streams[] | select(.codec_type=="video")][0].width')"
    height="$(printf '%s' "$probe" | jq -r '[.streams[] | select(.codec_type=="video")][0].height')"
    duration="$(printf '%s' "$probe" | jq -r '.format.duration')"
    audio_count="$(printf '%s' "$probe" | jq -r '[.streams[] | select(.codec_type=="audio")] | length')"
    if [ "$width" != "1080" ] || [ "$height" != "1920" ]; then
      log_warn "$clip unexpected resolution: ${width}x${height}"
      fail=1
    fi
    python3 - "$duration" <<'PY' || fail=1
import sys
d = float(sys.argv[1])
if not (14.0 <= d <= 16.5):
    print(f"[warn] unexpected duration: {d}", file=sys.stderr)
    raise SystemExit(1)
PY
    if [ "$audio_count" != "0" ]; then
      log_warn "$clip has audio tracks but generate_audio=false"
      fail=1
    fi
  fi
done

if [ "$fail" -ne 0 ]; then
  log_warn "workflow check failed"
  exit 2
fi

log_info "workflow check passed"
