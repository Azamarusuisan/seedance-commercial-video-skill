# Higgsfield MCP Demo And X Reference Patterns

Use this reference when the user asks to learn from external Higgsfield/Seedance examples, X posts, or demo repositories.

## Source Links

- X reference post: `https://x.com/D_studioproject/status/2071457354689004023`
- Demo repository: `https://github.com/kazujp225/HIGGSFIELDMCP-demo`

Do not copy third-party assets into final public/commercial outputs unless rights are confirmed. Use these sources as production-pattern references unless the user explicitly provides rights-cleared assets.

## X Reference Summary

Observed from the public post metadata and media:

- Post text: making a Mochi ad using Claude x Seedance 2.0 4K on Higgsfield MCP.
- Output style: short product ad, social feed shape, approximately 15 seconds.
- Downloaded reference media metadata:
  - duration: about 15.1s
  - frame rate: 30fps
  - available source variant: up to 2160x2432
  - inspected local variant: 1080x1216

Creative pattern:

- Product-first soft commercial look.
- Repeating UI/storyboard-like planning frames before and between action shots.
- Pink/white product color story.
- Fast 15s ad pacing.
- Human lifestyle use shots plus product hero shots.
- Clear product pack visibility.
- Lightweight on-screen captioning/branding.

Reusable lesson:

- Treat a public X post as a style/structure reference, not as a source asset for final delivery.
- Extract timing, shot density, color story, product/actor balance, and final hero-shot pattern.
- Rebuild with original or user-cleared assets.

## HIGGSFIELDMCP-demo Patterns

The demo repo shows a complete production package for a fictional Japanese cosmetics CM:

- reference screenshots from X
- generated product/base image
- product master and mask
- start image prompts separated from video prompts
- Seedance raw outputs
- text/audio-in-generation tests
- text/audio-post-edit tests
- overlay PNGs
- voice/BGM/audio mix files
- model comparison logs
- contact sheets and preview frames
- static review site
- MCP/CLI connection manual
- final execution report

Reusable production pattern:

1. Save external inspiration separately from generated assets.
2. Make a start image that locks product, actor, layout, and color direction.
3. Write a video prompt with exact timing beats.
4. Generate Seedance first as the main candidate.
5. Save raw outputs, job JSON, ffprobe metadata, contact sheets, and preview frames.
6. Compare "model-generated text/audio" and "post-edited text/audio" as separate tracks.
7. Package the final review materials in a static site or structured delivery folder.

## Text/Audio Policy Split

The demo highlights an important fork:

### Generate-In-Model Mode

Use when the user wants to compare model capability or accepts text/audio imperfections.

- `generate_audio=true`
- ask model to generate captions, voice, music, and scene text
- useful for model comparison
- Japanese text may contain errors
- not ideal when copy must be exact

### Post-Production Exact Mode

Use when exact Japanese copy, product labels, subtitles, or voice-over timing matter.

- `generate_audio=false`
- Seedance makes visuals only
- TTS/voice-over is generated separately
- subtitles/telop are burned in during editing
- best for final TikTok/Shorts story videos and client-facing copy accuracy

Default for Zettai-style TikTok story work:

```text
Seedance visual-only.
External narration.
Post-edited Japanese subtitles/telop.
One primary reference image per clip.
Continuous story chain across clips.
```

## Packaging Checklist

For every serious run, keep:

- prompt files
- reference/source manifest
- rights notes
- cost estimate
- job JSON
- raw MP4
- final edited MP4
- ffprobe JSON
- contact sheet
- preview frame
- subtitle/audio files
- delivery notes
- known limitations

This makes the project learnable by future agents and easier to rerun.
