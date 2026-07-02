#!/usr/bin/env bash
set -euo pipefail

BASE="21ec5aed83af44f9b3c2ec969ea8102af7d5039f"
HEAD_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git ls-remote origin main | cut -f1)"

[ "$HEAD_SHA" = "$REMOTE_SHA" ] || { echo "FAIL: HEADがorigin/mainと不一致(未push)"; exit 1; }

# permission manifests are human-edited safety switches, not frozen historical data.
# Their safety is enforced below by requiring all execute/generate flags to stay false.
git diff --stat "$BASE..HEAD" -- workspace references tests/fixtures ':(exclude)workspace/run/*.permission.json' | grep -q . \
  && { echo "FAIL: 凍結領域に変更"; exit 1; } || true

rg -n "SKIP_|BYPASS|FORCE_APPROVE|NO_GATE|APPROVED=1" studio/ --glob '!**/self_audit.sh' && exit 1 || true
rg -n "def (write|set|update|save)" studio/core/permission.py && exit 1 || true
rg -n "STUDIO_SEED_DIR" studio --glob '!studio/memory/seeds.py' --glob '!studio/tests/**' && exit 1 || true
rg -n "permission.json" studio/ui studio/core --glob '!**/tests/**' | rg "write_text|_write_json|dump" && exit 1 || true
git ls-files | grep -E "^studio/projects/" && exit 1 || true
git ls-files -z studio docs PLAN.md CODEX.md CLAUDE.md AGENTS.md HERMES.md OPENCREW.md SKILL.md README.md .gitignore 2>/dev/null \
  | tr '\0' '\n' | grep -v '^studio/tests/self_audit.sh$' | tr '\n' '\0' \
  | xargs -0 rg -l "cloudfront|X-Amz-|Bearer " 2>/dev/null && exit 1 || true
for permission_file in workspace/run/*.permission.json; do
  [ -e "$permission_file" ] || continue
  open_keys="$(
    jq -r '
      paths(scalars) as $p
      | select(getpath($p) == true)
      | ($p | map(tostring)) as $parts
      | ($parts | join(".")) as $key
      | select(any($parts[]; test("(^execute$|^execute_|_execute$|_execute_|_generate$|_generation$|^seedance_generate$|^execute_paid_generation$|^execute_image_generation$)")))
      | $key
    ' "$permission_file"
  )"
  if [ -n "$open_keys" ]; then
    echo "FAIL: v1有料経路が開いている(人間が該当フラグをfalseに設定すること)"
    while IFS= read -r key; do
      [ -n "$key" ] && echo "  $permission_file: $key=true"
    done <<< "$open_keys"
    exit 1
  fi
done

python3 -m studio.tests.run
echo "SELF-AUDIT: ALL GREEN"
