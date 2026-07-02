#!/usr/bin/env bash
set -euo pipefail

BASE="21ec5aed83af44f9b3c2ec969ea8102af7d5039f"
HEAD_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git ls-remote origin main | cut -f1)"

[ "$HEAD_SHA" = "$REMOTE_SHA" ] || { echo "FAIL: HEADがorigin/mainと不一致(未push)"; exit 1; }

git diff --stat "$BASE..HEAD" -- workspace references tests/fixtures | grep -q . \
  && { echo "FAIL: 凍結領域に変更"; exit 1; } || true

rg -n "SKIP_|BYPASS|FORCE_APPROVE|NO_GATE|APPROVED=1" studio/ --glob '!**/self_audit.sh' && exit 1 || true
rg -n "def (write|set|update|save)" studio/core/permission.py && exit 1 || true
git ls-files | grep -E "^studio/projects/" && exit 1 || true
git ls-files -z studio docs PLAN.md CODEX.md CLAUDE.md AGENTS.md HERMES.md OPENCREW.md SKILL.md README.md .gitignore 2>/dev/null \
  | tr '\0' '\n' | grep -v '^studio/tests/self_audit.sh$' | tr '\n' '\0' \
  | xargs -0 rg -l "cloudfront|X-Amz-|Bearer " 2>/dev/null && exit 1 || true

python3 -m studio.tests.run
echo "SELF-AUDIT: ALL GREEN"
