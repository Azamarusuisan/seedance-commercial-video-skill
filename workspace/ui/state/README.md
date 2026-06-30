# Live Workflow State

`generation-state.json` is the file Codex updates after each terminal instruction.

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
