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
