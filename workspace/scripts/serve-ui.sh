#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8787}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cd "$REPO_ROOT"
printf 'Seedance live workflow UI:\n'
printf '  http://127.0.0.1:%s/workspace/ui/live-workflow.html\n' "$PORT"
printf '  http://127.0.0.1:%s/workspace/ui/generation-checkpoint.html\n' "$PORT"
exec python3 -m http.server --bind 127.0.0.1 --directory "$REPO_ROOT" "$PORT"
