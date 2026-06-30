#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIVE_DIR="$REPO_ROOT/workspace/assets/3d/live"
OUT="$LIVE_DIR/blender_screen_current.png"
STATE="$LIVE_DIR/blender-screen-state.json"
INTERVAL="${INTERVAL:-1}"
LOOP="${LOOP:-0}"
ACTIVATE_BLENDER="${ACTIVATE_BLENDER:-0}"
CAPTURE_COUNT=0

mkdir -p "$LIVE_DIR"

json_string() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

write_state() {
  local status="$1"
  local message="$2"
  local rect="${3:-}"
  local updated_at
  updated_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  cat > "$STATE" <<JSON
{
  "status": "$(json_string "$status")",
  "message": "$(json_string "$message")",
  "updated_at": "$(json_string "$updated_at")",
  "source": "macos_screencapture",
  "mode": "blender_app_screen",
  "latest_frame": "workspace/assets/3d/live/blender_screen_current.png",
  "window_rect": "$(json_string "$rect")",
  "capture_count": $CAPTURE_COUNT,
  "interval_seconds": "$(json_string "$INTERVAL")",
  "local_only": true,
  "paid_generation_executed": false
}
JSON
}

capture_once() {
  if [[ "$ACTIVATE_BLENDER" == "1" ]]; then
    osascript -e 'tell application "Blender" to activate' >/dev/null 2>&1 || true
    sleep 0.2
  fi

  local window_info window_id rect window_name
  window_info="$(swift - <<'SWIFT' 2>/dev/null || true
import Foundation
import CoreGraphics

let list = CGWindowListCopyWindowInfo(.optionAll, kCGNullWindowID) as? [[String: Any]] ?? []
let windows = list.filter { window in
    let owner = window[kCGWindowOwnerName as String] as? String ?? ""
    let layer = window[kCGWindowLayer as String] as? Int ?? -1
    let bounds = window[kCGWindowBounds as String] as? [String: Any] ?? [:]
    let width = bounds["Width"] as? Int ?? 0
    let height = bounds["Height"] as? Int ?? 0
    return owner == "Blender" && layer == 0 && width > 600 && height > 400
}

guard let best = windows.max(by: { lhs, rhs in
    let lb = lhs[kCGWindowBounds as String] as? [String: Any] ?? [:]
    let rb = rhs[kCGWindowBounds as String] as? [String: Any] ?? [:]
    let la = (lb["Width"] as? Int ?? 0) * (lb["Height"] as? Int ?? 0)
    let ra = (rb["Width"] as? Int ?? 0) * (rb["Height"] as? Int ?? 0)
    return la < ra
}) else {
    exit(1)
}

let id = best[kCGWindowNumber as String] as? Int ?? 0
let name = best[kCGWindowName as String] as? String ?? "Blender"
let bounds = best[kCGWindowBounds as String] as? [String: Any] ?? [:]
let x = bounds["X"] as? Int ?? 0
let y = bounds["Y"] as? Int ?? 0
let w = bounds["Width"] as? Int ?? 0
let h = bounds["Height"] as? Int ?? 0
print("\(id)|\(x),\(y),\(w),\(h)|\(name)")
SWIFT
)"

  if [[ -z "$window_info" ]]; then
    write_state "failed" "BlenderウィンドウIDを取得できません。Blenderを起動してください。" ""
    return 1
  fi

  IFS='|' read -r window_id rect window_name <<<"$window_info"

  local tmp
  tmp="$LIVE_DIR/blender_screen_current.tmp.png"
  screencapture -x -l "$window_id" "$tmp"
  mv "$tmp" "$OUT"
  CAPTURE_COUNT=$((CAPTURE_COUNT + 1))
  write_state "captured" "Blenderアプリ画面をローカルキャプチャしました: $window_name" "$rect"
}

if [[ "$LOOP" == "1" ]]; then
  while true; do
    capture_once || true
    sleep "$INTERVAL"
  done
else
  capture_once
fi
