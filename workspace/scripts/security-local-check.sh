#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8787}"

check_code() {
  local label="$1"
  local expected="$2"
  shift 2
  local code
  code="$(curl -s -o /tmp/seedance-security-check.out -w '%{http_code}' "$@")"
  if [ "$code" != "$expected" ]; then
    printf '[warn] %s expected %s got %s\n' "$label" "$expected" "$code" >&2
    exit 1
  fi
  printf '[info] %s -> %s\n' "$label" "$code"
}

check_code "bad Origin POST blocked" 403 \
  -H 'Origin: https://evil.example' \
  -H 'Content-Type: application/json' \
  --data '{"message":"security-check-bad-origin"}' \
  "$BASE/api/send-to-codex"

check_code ".git static path blocked" 404 "$BASE/.git/config"
check_code ".env static path blocked" 404 "$BASE/.env"
check_code "factory data reachable" 200 "$BASE/api/factory-data"

python3 - "$BASE" <<'PY'
import json
import sys
from urllib.request import urlopen

base = sys.argv[1]
with urlopen(f"{base}/api/factory-data", timeout=3) as response:
    data = json.load(response)

assert data["ok"] is True
assert data["local_server"]["local_only"] is True
assert data["local_server"]["terminal_forward_enabled"] is False
print("[info] local_only=true and terminal_forward=false")
PY
