#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo

HERMES_CHROME_COMMAND="${HERMES_CHROME_COMMAND:-/Users/stork/Applications/Hermes Chrome.command}"
HERMES_CDP_PORT="${HERMES_CDP_PORT:-9223}"
LOG_PATH="$LOG_DIR/higgsfield-login-status.json"

if [ ! -x "$HERMES_CHROME_COMMAND" ]; then
  write_status_json "$LOG_PATH" "open higgsfield login" "blocked" "Hermes Chrome command is missing or not executable."
  log_warn "Hermes Chrome command is missing: $HERMES_CHROME_COMMAND"
  exit 1
fi

"$HERMES_CHROME_COMMAND" "--remote-debugging-port=$HERMES_CDP_PORT" "https://higgsfield.ai/"
write_status_json "$LOG_PATH" "open higgsfield login" "opened" "Higgsfield opened in Hermes Chrome. User must log in manually."

log_info "Opened Higgsfield in Hermes Chrome on intended CDP port $HERMES_CDP_PORT."
log_info "If login is requested, complete it manually. Do not share passwords, codes, cookies, or payment data."

