# Cast Assets

Place project-specific cast/reference materials here when building TikTok/Shorts story videos or recurring-character Seedance projects.

Raw person/source images are ignored by git by default. Keep them local or in a private asset store unless they are intentionally licensed sample assets.

Recommended structure:

```text
workspace/assets/cast/
  guides/
  source_refs/
  props/
  creatures/
  locations/
  cast-manifest.json
```

Start from `cast-manifest.example.json`, then create a project-specific `cast-manifest.json`.

Important:

- Record rights notes for every person/source asset.
- Use one primary reference image per Seedance clip when the endpoint only accepts one start image.
- For exact narration and Japanese captions, keep Seedance visual-only and add voice/subtitles in editing.
