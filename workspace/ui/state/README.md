# Live Workflow State

`generation-state.json` is the file Codex updates after each terminal instruction.

The live UI reads it every few seconds from:

```text
workspace/ui/live-workflow.html
```

Run a local server from the repository root because browser `fetch()` does not reliably read JSON from `file://`.
