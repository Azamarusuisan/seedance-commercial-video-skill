# Claude Code Instructions

Follow `AGENTS.md` and `workspace/agent-guides/cross-agent-runbook.md`.

Claude Code-specific notes:

- Use the repo-local scripts under `workspace/scripts/` for preflight, login opening, MCP request preparation, GPT Image reference generation, and result logging.
- Run Higgsfield account checks, Seedance cost estimates, and Seedance generation through the host-provided Higgsfield MCP tool, not a local `higgsfield` package.
- Do not paste or save credentials into files, prompts, logs, or shell history.
- If Higgsfield or note asks for login, stop and ask the user to complete it manually in Hermes Chrome.
- Keep CM generation gated until the user approves the final brief and prompt.
- Do not press note publish buttons or finalize paid settings.
