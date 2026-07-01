#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8787}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
URL="http://127.0.0.1:${PORT}/workspace/ui/live-workflow.html"

if curl -fsS "http://127.0.0.1:${PORT}/api/factory-data" >/dev/null 2>&1; then
  open "$URL"
  exit 0
fi

osascript <<APPLESCRIPT
tell application "Terminal"
  activate
  do script "cd ${REPO_ROOT} && PORT=${PORT} BIND=127.0.0.1 bash workspace/scripts/serve-ui.sh"
end tell
APPLESCRIPT

sleep 2
open "$URL"
