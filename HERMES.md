# v1凍結 / workspace/ 経路の有料生成禁止

This repository is entering the Studio v2 implementation track described in `PLAN.md`.
The existing v1 `workspace/` generation paths are frozen for new paid execution.
Do not run Higgsfield, Seedance, Palmier, ElevenLabs, upscale, export, publishing, or external-posting actions through v1.
Treat `workspace/`, `references/`, and `tests/fixtures/` as preserved legacy evidence unless a task explicitly says to add a non-destructive notice or new v2-compatible file.

# Hermes Instructions

Follow `AGENTS.md` and `workspace/agent-guides/cross-agent-runbook.md`.

Hermes-specific notes:

- Use the included plugin skill at `skills/seedance/SKILL.md`.
- Use the workflow reference at `skills/seedance/references/seedance-cm-workflow.md`.
- Use `skills/seedance/references/image-to-video-handoff.md` when a generated/reference image should become a Seedance video.
- `SKILL.md` and `references/seedance-cm-workflow.md` remain available for root-skill compatibility.
- Use Hermes Chrome for web login and browser actions:
  `/Users/stork/Applications/Hermes Chrome.command`
- Keep authentication manual. Do not export cookies, local storage, tokens, or browser sessions.
- Run Higgsfield/Seedance through the Higgsfield MCP tool.
- Record the prompt, model, cost estimate, job JSON, result URL, and final MP4 path in `workspace/logs/` and `workspace/delivery/`.
