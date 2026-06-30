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

Current reusable generated set:

```text
workspace/assets/cast/generated_20260629/
  contact_sheet.jpg
  cast-manifest.json
  ai_influencer_aoi_rin_01.png
  ai_influencer_rina_hayun_01.png
  cast_f_beauty_01.png ... cast_m_ordinary_04.png

workspace/assets/cast/source_refs_20260629/
  source-manifest.json
```

Use `generated_20260629/cast-manifest.json` when writing TikTok story scripts or Seedance prompts that need a theater-like cast. The images in that folder are intentionally committed even though cast images are normally ignored.

Previously removed guide/source references are intentionally excluded from active cast/source use. Do not add them back as default guides or source references unless the user explicitly re-approves them.

Important:

- Record rights notes for every person/source asset.
- Use one primary reference image per Seedance clip when the endpoint only accepts one start image.
- For exact narration and Japanese captions, keep Seedance visual-only and add voice/subtitles in editing.
