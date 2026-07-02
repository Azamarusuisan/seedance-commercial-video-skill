# Fact Check 2026-07-02

## Git

- Branch: `main`
- Remote sync: `origin/main` up to date before T0 work.
- Local commits ahead before T0: none.
- Working tree before T0: clean.

## Required Files

Present:

- `CLAUDE.md`
- `CODEX.md`
- `AGENTS.md`
- `HERMES.md`
- `OPENCREW.md`
- `workspace/scripts/validate-seedance-input.py`
- `references/known-failure-patterns.md`
- `tests/fixtures/approved-storyboard-asset.json`
- `tests/fixtures/blender-previs-asset.json`
- `tests/fixtures/learning-preflight-pass.md`
- `tests/fixtures/review-blender-leak.json`
- `tests/fixtures/run-permission-safe.json`

## Current UI / Project State

The latest `main` already includes files that the external audit said were missing:

- `workspace/ui/preflight.html`
- `workspace/ui/storyboard.html`
- `workspace/ui/generation-review.html`
- `workspace/projects/macneo-pc-cm-15s/project-state.json`
- `workspace/projects/macneo-pc-cm-15s/keyvisual-generation-summary.json`

This means the audit's "missing preflight/project-state" finding is outdated for latest `main`.

## Permission Manifests

Observed permission files:

- `workspace/run/permission.example.json`
- `workspace/run/lipstick-cm-30s.permission.json`
- `workspace/run/macneo-pc-cm-15s.permission.json`

Current execution-related values:

- `permission.example.json`
  - `execute_paid_generation=false`
  - `execute_image_generation=false`
  - `prepare_seedance_cost_request=false`
  - `prepare_seedance_generation_request=false`
  - `publish_ad=false`
  - budget cap: `0`

- `lipstick-cm-30s.permission.json`
  - `execute_paid_generation=false`
  - `execute_image_generation=false`
  - `prepare_seedance_cost_request=false`
  - `prepare_seedance_generation_request=false`
  - `publish_ad=false`
  - budget cap: `0`

- `macneo-pc-cm-15s.permission.json`
  - `execute_image_generation=true`
  - `prepare_seedance_cost_request=false`
  - `prepare_seedance_generation_request=false`
  - `execute_paid_generation=false`
  - `generate_audio=false`
  - `post_edit=false`
  - `publish_ad=false`
  - budget cap: `50`

T0 did not change permission values.

## PLAN / Work Order Mismatches To Resolve Later

- `studio/` does not exist yet. T0 only adds the plan/work order and ignores runtime implementation.
- `workspace/run/macneo-pc-cm-15s.permission.json` still has `execute_image_generation=true`; this is existing state from the MacNeo key-visual run and was not changed in T0.
- `workspace/run/macneo-pc-cm-15s.permission.json` budget note says only one image2 storyboard/conte-sheet generation was approved, while latest project state includes generated key visuals. This is an existing state-note mismatch and should be handled in the later state-management phase, not by T0.
- v1 `workspace/` remains present and tracked as legacy evidence. T0 freezes new paid execution through v1 but does not delete, move, or rewrite existing legacy assets.
- `generation-state.json` remains ignored under `.gitignore`; latest UI can read project-specific state, but a canonical v2 `project.json` model is not implemented yet.

## T0 Changes Applied

- Added `PLAN.md` from the provided zip.
- Added `docs/CODEX-WORKORDER.md` from the provided zip.
- Added v1 freeze notices to:
  - `CLAUDE.md`
  - `CODEX.md`
  - `AGENTS.md`
  - `HERMES.md`
  - `OPENCREW.md`
- Added `studio/projects/` to `.gitignore`.

## Safety Notes

- No paid generation was run.
- No Higgsfield, Seedance, Palmier, ElevenLabs, upscale, export, publishing, or external-posting action was run.
- No existing `workspace/`, `references/`, or `tests/fixtures/` file was deleted, moved, or rewritten.
