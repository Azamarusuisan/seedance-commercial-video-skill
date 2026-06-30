#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
DIST_DIR="$REPO_ROOT/dist"
OUT="$DIST_DIR/seedance-local-factory-$STAMP.zip"
INCLUDE_INBOX="${INCLUDE_INBOX:-0}"

mkdir -p "$DIST_DIR"
cd "$REPO_ROOT"

EXCLUDES=(
  "*/x-reference-*.png"
  "x-reference-*.png"
  "*/source_refs_20260629/*.jpeg"
  "source_refs_20260629/*.jpeg"
  "*/source_refs_20260629/*.jpg"
  "source_refs_20260629/*.jpg"
)

if [[ "$INCLUDE_INBOX" != "1" ]]; then
  EXCLUDES+=("workspace/ui/state/codex-inbox.jsonl")
  EXCLUDES+=("*/workspace/ui/state/codex-inbox.jsonl")
  EXCLUDES+=("codex-inbox.jsonl")
fi

ZIP_ARGS=()
for pattern in "${EXCLUDES[@]}"; do
  ZIP_ARGS+=("-x" "$pattern")
done

zip -rq "$OUT" \
  README.md \
  AGENTS.md \
  CLAUDE.md \
  HERMES.md \
  OPENCREW.md \
  SKILL.md \
  skills \
  references \
  workspace/ui \
  workspace/scripts/serve-ui.sh \
  workspace/scripts/package-local-factory.sh \
  workspace/scripts/render-blender-demo.sh \
  workspace/scripts/render-blender-live.sh \
  workspace/scripts/capture-blender-screen.sh \
  workspace/mcp-requests \
  workspace/logs \
  workspace/assets/cast/README.md \
  workspace/assets/cast/generated_20260629 \
  workspace/assets/cast/source_refs_20260629/source-manifest.json \
  workspace/assets/3d \
  workspace/blender \
  workspace/briefs \
  workspace/prompts \
  videos/codex-inbox-x-demo/assets \
  "${ZIP_ARGS[@]}"

echo "$OUT"
