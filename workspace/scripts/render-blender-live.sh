#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BLENDER_BIN="${BLENDER_BIN:-}"

if [[ -z "$BLENDER_BIN" && -x "/Applications/Blender.app/Contents/MacOS/Blender" ]]; then
  BLENDER_BIN="/Applications/Blender.app/Contents/MacOS/Blender"
fi

if [[ -z "$BLENDER_BIN" ]]; then
  BLENDER_BIN="$(command -v blender || true)"
fi

if [[ -z "$BLENDER_BIN" ]]; then
  echo "Blender is not installed or not on PATH." >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/workspace/assets/3d/live"
rm -f "$REPO_ROOT"/workspace/assets/3d/live/blender_live_*.png

"$BLENDER_BIN" --background --python "$REPO_ROOT/workspace/blender/codex_factory_live.py"

if [[ ! -s "$REPO_ROOT/workspace/assets/3d/live/live-state.json" ]]; then
  echo "Blender live render did not produce live-state.json." >&2
  exit 1
fi

echo "$REPO_ROOT/workspace/assets/3d/live/live-state.json"
