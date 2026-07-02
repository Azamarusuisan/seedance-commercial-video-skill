# v1凍結 / workspace/ 経路の有料生成禁止

This repository is entering the Studio v2 implementation track described in `PLAN.md`.
The existing v1 `workspace/` generation paths are frozen for new paid execution.
Do not run Higgsfield, Seedance, Palmier, ElevenLabs, upscale, export, publishing, or external-posting actions through v1.
Treat `workspace/`, `references/`, and `tests/fixtures/` as preserved legacy evidence unless a task explicitly says to add a non-destructive notice or new v2-compatible file.

# Agent Instructions

This repository can be operated from Codex, Claude Code, Hermes, or OpenCrew-style runners. Use the shared scripts and runbook instead of inventing agent-specific flows.

## Required Reading

Before video planning, prompt writing, image-to-video handoff, generation, or delivery checks, read:

- `skills/seedance/SKILL.md` for plugin operation
- `skills/seedance/references/seedance-cm-workflow.md` for plugin operation
- `skills/seedance/references/image-to-video-handoff.md` for generated-image to video handoff
- `SKILL.md` and `references/seedance-cm-workflow.md` for root-skill compatibility
- `references/image-to-video-handoff.md` for root-skill compatibility
- `references/end-to-end-movie-pipeline.md` when the request needs multi-shot character/product consistency or a full Blender-to-Palmier-Pro movie pipeline
- `workspace/agent-guides/cross-agent-runbook.md`

## Hard Rules

- Do not publish to note. Draft creation and draft insertion only.
- Do not store API keys, passwords, cookies, browser sessions, tokens, SSH keys, or recovery codes.
- Do not use web images or third-party materials in final public/commercial output unless rights are confirmed.
- Do not claim guaranteed hits, profits, revenue, customer acquisition, No.1, only, official partnership, or other unsupported outcomes.
- Stop before Higgsfield generation unless the user has approved the video use case, concept, prompt, reference image/assets, budget, and Higgsfield login/credit state.
- Use Hermes Chrome only for browser automation: `/Users/stork/Applications/Hermes Chrome.command`.

## Shared Entry Points

Run from the repository root:

```bash
bash workspace/scripts/preflight.sh
bash workspace/scripts/open-higgsfield-login.sh
bash workspace/scripts/higgsfield-status.sh
bash workspace/scripts/higgsfield-image.sh
bash workspace/scripts/elevenlabs-narration.sh
bash workspace/scripts/gpt-image-reference.sh
bash workspace/scripts/seedance-cost.sh
bash workspace/scripts/seedance-generate.sh
bash workspace/scripts/secret-scan.sh
```

Generation scripts intentionally stop unless human approval is explicit.

Higgsfield is MCP-first in this repo. The shell scripts prepare request JSON under `workspace/mcp-requests/`; the actual account check, cost estimate, and generation must be run through the Higgsfield MCP tool exposed by the host environment.
