#!/usr/bin/env bash
set -euo pipefail

source "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"
require_repo
cd "$REPO_ROOT"

# Fail closed: a secret scan that can't run must not report "clean".
if ! command -v rg >/dev/null 2>&1; then
  log_warn "ripgrep (rg) not found; cannot run the secret scan. Install rg and rerun."
  exit 1
fi

high_confidence_hits="$(rg -l --hidden \
  --glob '!.git/**' \
  --glob '!node_modules/**' \
  --glob '!workspace/outputs/**' \
  --glob '!workspace/**/*.mp4' \
  '(sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|hf_[A-Za-z0-9]{20,})' . || true)"

if [ -n "$high_confidence_hits" ]; then
  log_warn "Potential high-confidence secret patterns found in these files:"
  printf '%s\n' "$high_confidence_hits" >&2
  exit 1
fi

unignored_sensitive_files=""
while IFS= read -r file; do
  [ -n "$file" ] || continue
  case "$file" in
    ./workspace/scripts/secret-scan.sh)
      continue
      ;;
  esac
  if ! git check-ignore -q "$file" 2>/dev/null; then
    unignored_sensitive_files="${unignored_sensitive_files}${file}
"
  fi
done < <(find . -path './.git' -prune -o -type f \( -name '.env' -o -name '.env.*' -o -iname '*cookie*' -o -iname '*token*' -o -iname '*secret*' -o -iname '*session*' \) -print)

if [ -n "$unignored_sensitive_files" ]; then
  log_warn "Sensitive-looking filenames are not git-ignored:"
  printf '%s\n' "$unignored_sensitive_files" >&2
  exit 1
fi

log_info "secret scan passed"
