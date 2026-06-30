#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8787}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cd "$REPO_ROOT"
exec python3 "$REPO_ROOT/workspace/ui/server.py" --bind 127.0.0.1 --port "$PORT"
