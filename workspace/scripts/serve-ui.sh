#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8787}"
BIND="${BIND:-localhost}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export CODEX_FORWARD_TO_TERMINAL="${CODEX_FORWARD_TO_TERMINAL:-0}"
export CODEX_TERMINAL_APP="${CODEX_TERMINAL_APP:-Terminal}"

cd "$REPO_ROOT"
exec python3 "$REPO_ROOT/workspace/ui/server.py" --bind "$BIND" --port "$PORT"
