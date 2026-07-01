# Assets

No external or third-party commercial assets are used in this draft.

## Current Reference Assets

- `reference-keiba-ai-v1.png`
  - Purpose: image-to-video discussion reference for Seedance.
  - Source: built-in `image_gen` output copied into this project.
  - Status: available locally.
  - Note: the user requested GPTIMAGE specifically after this file was created. OpenAI Image API / GPT Image regeneration is blocked until `OPENAI_API_KEY` is available in the shell environment.

For client-specific commercial generation, place only user-provided or commercially licensed materials here, then record rights notes in `workspace/briefs/cm-brief.md` and `workspace/delivery/final-report.md`.

For TikTok/story or theater-cast projects, use `workspace/assets/cast/` plus a project-specific cast manifest. Keep raw person/source images local or private unless the repo intentionally includes licensed sample assets.

For the company's own reusable brand materials (logos, product photography, past campaign assets, brand guidelines), use `workspace/assets/brand/` plus `brand-manifest.json`. This is local-only by design — no external cloud database (e.g. Supabase) is connected, per the user's security preference. Prefer these company-owned assets over generated references whenever they exist, since they carry no third-party rights risk.
