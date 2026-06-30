#!/usr/bin/env bash
set -euo pipefail

tracked="$(git ls-files | grep -v '^workspace/scripts/security-public-leak-check\.sh$')"

if [ -z "$tracked" ]; then
  echo "[info] no tracked files"
  exit 0
fi

patterns='(https://[^[:space:]"`<>]*cloudfront\.net/user_|"subscription_plan_type"|"checked_at".*"higgsfield account status"|gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|hf_[0-9]{8}_[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,})'

hits="$(printf '%s\n' "$tracked" | xargs rg -n --hidden --no-messages "$patterns" || true)"

if [ -n "$hits" ]; then
  echo "[warn] public-leak check found tracked operational URLs/secrets:" >&2
  printf '%s\n' "$hits" >&2
  exit 1
fi

echo "[info] public-leak check passed"
