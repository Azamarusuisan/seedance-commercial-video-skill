# Live Workflow State

`generation-state.json` is the file Codex updates after each terminal instruction.
`asset-library.json` stores reusable generated cast manifests, first-party UI/Codex captures, external reference URLs, and blocked-source records.

The live UI reads it every few seconds from:

```text
workspace/ui/live-workflow.html
```

Run a local server from the repository root because browser `fetch()` does not reliably read JSON from `file://`.

The live UI can also send an instruction to Codex through:

```text
POST /api/send-to-codex
```

The server prints the instruction in the terminal and appends it to:

```text
workspace/ui/state/codex-inbox.jsonl
```

This is a local inbox bridge, not direct stdin injection into an already running Codex TUI session.

When served by `workspace/ui/server.py`, the UI also reads:

```text
GET /api/factory-data
```

That endpoint aggregates real local data from `generation-state.json`, `asset-library.json`, `codex-inbox.jsonl`, the generated cast folder, source captures, output files, and git status. It is intended for a local-only package where the user's PC is the server and the browser is the control-room viewer.
