# Work Order 2 Completion Audit

Date: 2026-07-02
Head checked: `8923b8d`

## Verified

- T-A: `studio/tests/self_audit.sh` exists and passes after push.
- T12': `docs/first-run.md` exists and states not to start with a full CM.
- T13: `studio/memory/seeds/*.json` exists, every seed item has `source` and `status`, and FP-001 through FP-008 are covered.
- T14: `studio/agents/compiler.py` uses seed structure, camera playbook, active look tokens, negative defaults, and keeps candidate tokens out of active prompt terms.
- T15: `studio/core/contract_validator.py` loads active/candidate prompt rules from seed JSON, fails closed when seed files are missing, and reports FP IDs.
- T16: `studio/memory/production_memory.py` and `studio/memory/import_v1.py` exist. v1 import is idempotent and read-only in tests.
- T17: `studio/core/jobs.py` applies retry playbook recipes, returns prompt diffs, blocks unknown tags, and stops on repeated tags.
- T18 partial: `studio/ui/web/` exists with a local-only stdlib server and optional FastAPI adapter. API flow covers create project, register asset, approve, mock generate, review, and memory recording.

## Verification Commands

```bash
python3 -m studio.tests.run
bash studio/tests/self_audit.sh
```

Current result: 27 tests pass, `SELF-AUDIT: ALL GREEN`.

## Known Conflict

Work Order 2 contains two incompatible requirements:

1. Global premise and T-A require no diff under `workspace/`, `references/`, or `tests/fixtures` after the Studio v2 base commit.
2. T18 asks to modify v1 `workspace/ui/live-workflow.html` and Factory pages to add a visible frozen banner.

Directly editing `workspace/ui/*.html` would satisfy T18 but fail T-A self-audit. The current implementation preserves T-A and shows the frozen banner in Studio v2 UI instead:

`V1 FROZEN — 閲覧専用。制作はStudio v2へ`

Human decision needed: either keep `workspace/` immutable, or explicitly allow a narrow v1 UI banner exception and update `self_audit.sh` accordingly.
