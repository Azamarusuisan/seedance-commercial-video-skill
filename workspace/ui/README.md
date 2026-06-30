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
- Confirm which materials will be used for generation.
- Confirm the removed blond male guide is excluded.
- Confirm Seedance visual-only, ElevenLabs narration, and post-edited subtitles.
- Track Seedance job status, result URLs, credits, review decisions, and retry reasons.
- Produce a copyable approval summary for Codex/Hermes before paid generation.

This UI does not submit Higgsfield jobs. It is a human checkpoint before generation.
