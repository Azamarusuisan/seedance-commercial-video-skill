# Generation Checkpoint UI

Open `generation-checkpoint.html` in a browser before running Seedance/Higgsfield generation.

For the Codex-driven live loop, run:

```bash
bash workspace/scripts/serve-ui.sh
```

Then open:

```text
http://127.0.0.1:8787/workspace/ui/live-workflow.html
```

Purpose:

- Review the current cast assets.
- Review the factory-style live workflow and local asset library.
- Confirm which materials will be used for generation.
- Confirm Seedance visual-only, ElevenLabs narration, and post-edited subtitles.
- Track Seedance job status, result URLs, credits, review decisions, and retry reasons.
- Send the current next instruction to the local Codex inbox from the browser.
- Watch real local data from `/api/factory-data`: state JSON, asset library, Codex inbox, source captures, generated cast files, output folders, Blender screen captures, and Higgsfield MCP request/log handoffs.
- Produce a copyable approval summary for Codex/Hermes before paid generation.

This UI binds to `127.0.0.1` by default. It does not submit Higgsfield jobs; it is a human-visible local factory dashboard before generation.

Blender app screen projection:

```bash
bash workspace/scripts/capture-blender-screen.sh
LOOP=1 INTERVAL=1 bash workspace/scripts/capture-blender-screen.sh
```

The command writes `workspace/assets/3d/live/blender_screen_current.png` and `blender-screen-state.json`. The Factory UI polls local data every second and projects that local capture into the center workflow panel.

Higgsfield MCP connection:

- `workspace/scripts/higgsfield-status.sh` prepares account/model request JSON.
- `workspace/scripts/seedance-cost.sh` prepares cost request JSON.
- `workspace/scripts/seedance-generate.sh` prepares generation request JSON.
- Actual Higgsfield MCP execution must happen in a host that exposes the Higgsfield MCP tool.
- Sanitized results are recorded under `workspace/logs/`; no API keys, cookies, sessions, payment data, or browser storage exports should be saved.
