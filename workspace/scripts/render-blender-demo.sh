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

"$BLENDER_BIN" --background --python "$REPO_ROOT/workspace/blender/codex_factory_demo.py"

if [[ ! -s "$REPO_ROOT/workspace/assets/3d/renders/codex_factory_demo.png" ]]; then
  echo "Blender render did not produce codex_factory_demo.png." >&2
  exit 1
fi

cat > "$REPO_ROOT/workspace/assets/3d/manifests/codex_factory_demo.json" <<JSON
{
  "id": "codex_factory_demo",
  "name": "Codex Factory Demo",
  "type": "render",
  "path": "workspace/assets/3d/renders/codex_factory_demo.png",
  "blend_path": "workspace/assets/3d/blend/codex_factory_demo.blend",
  "script_path": "workspace/blender/codex_factory_demo.py",
  "rights_status": "generated",
  "use_scope": "local factory UI, Seedance reference plate, internal docs",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "review_status": "pending",
  "notes": "Local Blender render. No paid generation, no external API, no publishing."
}
JSON

echo "$REPO_ROOT/workspace/assets/3d/renders/codex_factory_demo.png"
