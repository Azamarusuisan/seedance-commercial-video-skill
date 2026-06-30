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
- Watch real local data from `/api/factory-data`: state JSON, asset library, Codex inbox, source captures, generated cast files, and output folders.
- Produce a copyable approval summary for Codex/Hermes before paid generation.

This UI binds to `127.0.0.1` by default. It does not submit Higgsfield jobs; it is a human-visible local factory dashboard before generation.
