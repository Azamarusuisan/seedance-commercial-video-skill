# Public Demand Short-Video Patterns

Use this reference when the user asks for viral, popular, trend-aware, market-demand, UGC, TikTok/Reels/Shorts, autonomous learning, or "what people want" optimization.

Do not copy public reference media into final outputs unless rights are confirmed. Extract structure, pacing, hooks, and production workflow only.

## Demand Learning Loop

1. Scan current public references and record only safe metadata: source URL, creator, date, views/likes/replies, duration, aspect ratio, concept, and visible structure.
2. Classify the pattern: product ad, UGC review, founder/company story, travel Vlog, story scene, faceless explainer, app demo, or product demo.
3. Pick the viewer action to optimize: stop scroll, watch to end, remember product, comment/share, click, or trust the presenter.
4. Write 2-4 concept variants before paid generation. Change the hook, not every variable.
5. Build storyboard panels or 15s beat sheets before Seedance prompts.
6. Generate visuals with exact motion/camera prompts. Keep exact text, narration, and subtitles in post when accuracy matters.
7. Make contact sheets and preview frames for review.
8. If available, run a Virality Predictor / finished-video score route before spending credits on more variants.
9. Save the winning hook, losing hook, reference assets, prompt, job metadata, and final MP4 path.

## Public Reference Snapshot

Observed on 2026-06-29 from public X metadata and local contact-sheet inspection. Counts can change.

| Source | Visible category | Duration / shape | Demand signal at snapshot | Reusable pattern |
|---|---|---:|---:|---|
| `https://x.com/higgsfield/status/2061813474934882482` | Company-in-a-box workflow | 69s, 16:9 | 257k views, 1.4k likes | Brand identity, app screens, ads, founder video, and predictor loop in one narrative. |
| `https://x.com/D_studioproject/status/2062078290249253134` | Drink ad | 15s, vertical | 60k views, 512 likes | Youth/emotion first, product drink moment, wide blue-sky payoff. |
| `https://x.com/D_studioproject/status/2062947055451168924` | Food ad | 15.5s, vertical | 34k views, 178 likes | Prop clue, lonely mood, product break, bold CTA. |
| `https://x.com/D_studioproject/status/2070458816857362561` | Fresh drink ad | 15.4s, vertical | 67k views, 198 likes | Beach/friend group, product refresh, laughter, final product memory. |
| `https://x.com/D_studioproject/status/2070914610853711985` | Snack/chocolate ad | 15.1s, vertical | 60k views, 588 likes | Small daily conflict, expressive face, cute VFX shift, product hero. |
| `https://x.com/D_studioproject/status/2071057120318152733` | Skincare ad | 15.1s, vertical | 13k views, 119 likes | Walk-in lifestyle, product close-up, application, satisfied face, feature icons, pack shot. |
| `https://x.com/D_studioproject/status/2071457354689004023` | Mochi/product ad | 15.1s, vertical | prior local reference | Soft product-first ad, storyboard/planning frames, lifestyle use, final pack shot. |
| `https://x.com/saniaspeaks_/status/2071223180908503428` | Identity-preserving travel Vlog | 15.1s, 16:9 source | 11k views, 249 likes | Same subject, exact outfit, 2s location beats, handheld camcorder style, ambience-only sound. |

## Winning Patterns To Reuse

### 1. 15s Product Ad

Default shape:

```text
0-2s: face, product, motion, or conflict that works without audio
2-5s: world/context and desire
5-9s: product interaction
9-12s: emotional or visual payoff
12-15s: product hero, short caption, brand memory
```

Use for drinks, snacks, skincare, cosmetics, apps, and simple physical products.

### 2. Story Sells Better Than Packshots

The best 15s ads are not only product montages. They show a tiny human change:

- thirsty to refreshed
- awkward to relieved
- lonely to comforted
- dull routine to small magic
- uncertain to confident

Write the emotional state before writing the camera prompt.

### 3. First 2 Seconds Must Work Silent

Use one of these hook types:

- Face close-up with strong expression.
- Product entering frame in an unusual way.
- Visible problem before the solution.
- Camera move through a threshold.
- Before/after contrast.
- Handheld selfie with immediate location/context.

Avoid generic establishing shots unless the location itself is the hook.

### 4. Identity-Preserving Vlog

For travel/beauty/guide videos, use short action beats instead of one vague scene:

```text
00-02 market/selfie
02-04 bridge/follow shot
04-06 buying food
06-08 seaside pause
08-10 bench/prop moment
10-12 shoreline
12-15 selfie loop ending
```

Keep the same subject, outfit, camera texture, and environment sounds across beats. This supports the theater/cast-library workflow.

### 5. UGC Batch Beats One Perfect Draft

For ads, test a small batch:

- 4 hooks x 1 mode before 1 hook x 4 modes.
- Keep product, avatar, duration, and aspect fixed.
- Change only the opening angle: unboxing, problem/solution, review, challenge, or proof.
- Score the first 2 seconds and final product recall before polishing.

### 6. Use Post-Production For Exact Text

Public examples often show generated visuals plus added captions, icons, or product panels. Keep Seedance focused on motion. Add exact Japanese subtitles, logo, product claims, and CTA in editing.

## External Skill / Repo Lessons

Installed locally for Codex on 2026-06-29:

- `higgsfield-generate`
- `higgsfield-soul-id`
- `higgsfield-product-photoshoot`
- `higgsfield-marketplace-cards`

Reference repositories inspected locally:

- `https://github.com/higgsfield-ai/skills`
  - Use official model discovery, Marketing Studio, Virality Predictor, hook/settings libraries, and Soul ID routing when available.
- `https://github.com/AKCodez/higgsfield-claude-skills`
  - Useful taxonomy for ecommerce, UGC, social hook, fashion, food/beverage, and brand-story skill routing.
- `https://github.com/rediumvex/ai-video-generator-claude`
  - Strong emphasis on 2-second hook engineering, camera vocabulary, and timestamped Seedance prompts.
- `https://github.com/HuyLe82US/awesome-seedance-prompts`
  - Useful as a prompt-vault reference across cinematic, anime, UGC, social, and ad styles.
- `https://github.com/OSideMedia/higgsfield-ai-prompt-skill`
  - Useful for character consistency, Seedance prompt modes, production benchmarks, and reusable templates.

Do not bulk-import non-official skill content into this repo. Read, distill, and adapt only the production pattern that helps the current project.

## Demand Checklist

Before generation:

- Does the first frame stop scroll without audio?
- Is there a human emotion or product transformation by second 5?
- Is the product or main character visible enough to remember?
- Is the prompt timed in seconds, not just described as a mood?
- Is the aspect ratio native to the platform?
- Is exact text planned for post-production when accuracy matters?
- Are public references used only as patterns, not copied assets?
- Is there a small variant plan before spending credits on polished output?

After generation:

- Make a contact sheet.
- Check first 2 seconds separately.
- Check final product/character memory.
- Check face/product distortions.
- Check caption/subtitle readability after editing.
- Run a virality/attention scoring tool if available.
- Save what worked back into the project notes.
