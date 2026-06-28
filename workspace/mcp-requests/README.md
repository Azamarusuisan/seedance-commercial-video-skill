# Higgsfield MCP Requests

Files in this directory are handoff payloads for agents that have the Higgsfield MCP tool connected.

The shell scripts do not call a local `higgsfield` CLI. They prepare MCP request JSON so Codex, Claude Code, Hermes, or OpenCrew operators can run the host-provided Higgsfield MCP tool and save sanitized responses into `workspace/logs/`.

Do not place API keys, cookies, sessions, tokens, browser storage exports, or payment data here.

