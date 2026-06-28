# Higgsfield MCP Requests

Files in this directory are handoff payloads for agents that have the Higgsfield MCP tool connected.

The shell scripts do not call a local `higgsfield` CLI. They prepare MCP request JSON so Codex, Claude Code, Hermes, or OpenCrew operators can run the host-provided Higgsfield MCP tool and save sanitized responses into `workspace/logs/`.

For image-to-video jobs, set `IMAGE_FILE` or place a generated reference at `workspace/assets/reference-image-v1.png`. The cost and generation scripts include the resolved image path in the MCP request when the file exists.

Do not place API keys, cookies, sessions, tokens, browser storage exports, or payment data here.
