# Claude → Codex Handoff — 2026-07-01

Claude Code's session may be ending soon (context/time limit). This is a consolidated
handoff so Codex (or the next agent) can pick up cleanly without re-deriving everything.
For the full blow-by-blow, `CODEX.md`'s "実装ステータス" log has the complete history;
this file is the condensed "what matters right now" version.

## Where things stand, track by track

**Track A (craft knowledge base, `references/cm-creative-craft-knowledge.md`): DONE.**
Phases 1–3 complete and pushed (commits `330f1dc`, `c581625`, `c48d9e0`). No further
work needed unless the user asks for more research.

**Track B (lipstick-cm-30s retry — the actual proof the pipeline works): NOT DONE.**
This is the one thing that actually matters and hasn't happened. Status:
- Scaffolding, prompts, permission manifests: all ready (see below).
- Actual generation: **zero images generated, zero Seedance runs.** Neither Claude
  Code's session nor Codex's last session had a live Higgsfield MCP tool connected.
  Codex prepared 4 request JSONs (`workspace/mcp-requests/lipstick-cm-keyvisual-*-image2.request.json`)
  but could not execute them (see `workspace/projects/lipstick-cm-30s/codex-to-claude-handoff-20260701.md`).
- **The exact copy-paste `/goal` prompt for whoever has live Higgsfield MCP access is at
  the very top of `CODEX.md`.** Use it as-is.

**Track C (Higgsfield model verification): still blocked**, same reason as Track B.

**Track D (UI): already resolved earlier, no action needed.**

## Real bugs found and fixed this session (read known-failure-patterns.md FP-001 through FP-008 before touching any prompt)

1. **FP-007**: `visual-handoff.json` for all 4 lipstick shots pointed `prepare-storyboard-image-request.sh`
   at an unfilled template scaffold (`shots/<id>/gpt-image-storyboard-prompt.txt`) instead of the
   actual hand-written prompts in `workspace/prompts/lipstick-cm/keyvisuals/final/*.prompt.txt`.
   **Fixed** — the JSON now points at the real files. Verified end-to-end with zero-cost dry runs.
2. **FP-008**: `workspace/prompts/lipstick-cm/{clip_01_0-15s,clip_02_15-30s}_9x16_seedance_{draft,final}.txt`
   turned out to be the *actual* prompts from the failed 270-credit run, sitting under a `final/`
   directory name with no warning, still cited by `seedance-conditions.md`/`brief.md`/the script doc
   as current. **All marked SUPERSEDED** with clear banners pointing to the corrected process.
   Do not use them.
3. MacNeo's `seedance-approval.md` had a stale "Aspect ratio: 9:16" line contradicting the rest
   of the same doc (already switched to 16:9). **Fixed.**
4. MacNeo's active prompt (`seedance-15s-16x9.txt`) and a separately-drifted planning doc
   (`storyboard-structure.md`) both had FP-003 vocabulary risk ("electric arcs"/"electric energy"
   as literal drawn-shape language). **Both fixed** to photographic vocabulary (glints/rim
   light/lens flare), matching the FP-003 rule. `workspace/learning/prompt-rules.md` and
   `pre-generation-learning-check.py`'s automated check already agree with this rule but the
   automated check's word list is too narrow (doesn't catch "arc"/"electric") — flagged in
   CODEX.md for whoever extends that script.
5. `workspace/run/lipstick-cm-30s.permission.json` didn't exist — **created** (prep-only,
   `execute_image_generation`/`execute_paid_generation`/both Seedance-prepare flags all `false`
   until real human approval happens).

## Important architectural discovery — needs Codex verification

`mcp__palmier-pro__generate_video`'s own tool schema explicitly documents Seedance-specific
parameters (`referenceImageMediaRefs`/`referenceVideoMediaRefs`/`referenceAudioMediaRefs`, all
noted as **"Seedance only"**). This strongly suggests Seedance may be reachable **directly through
Palmier Pro's MCP connection**, not necessarily a separate "Higgsfield MCP" server. This would also
explain (and validate, not contradict) the "Model target: Seedance 2 via Palmier MCP" line that was
in MacNeo's `storyboard-structure.md`.

**However**: in this Claude Code session, both `mcp__palmier-pro__get_timeline` and
`list_models(type=video)` returned `"Editor not available"` — meaning the Palmier Pro desktop
app itself isn't open/signed-in from wherever this session's MCP connection points. **Codex should
try these same two calls** (`get_timeline`, `list_models`) on its end. If Palmier Pro is actually
connected there, that may be a second, real execution path for Track B — potentially simpler than
chasing down a separate Higgsfield MCP connection. Record whatever you find (works / still
"Editor not available" / model names returned) in `CODEX.md` or `known-failure-patterns.md`.

**Codex follow-up**: Palmier Pro is connected in the Codex session. `get_timeline` returned
`canGenerate: true`; `list_models(type=image)` returned `nano-banana-pro`, `gpt-image-2`, and
other image models; `list_models(type=video)` returned `seedance-2`, `seedance-2-fast`, and
other video models. This confirms a technically viable Palmier execution path exists, but it is
still a paid generation path and a route change from the earlier Higgsfield-only decision. Do not
run it without fresh user approval.

## Exact next steps, in order

1. Pull latest `main`.
2. Check whether Higgsfield MCP is connected in your environment right now (an account/model-list
   call, similar to `higgsfield-status.sh`'s pattern — no cost). If yes, use the `/goal` prompt at
   the top of `CODEX.md` (task 11) to actually generate the 4 lipstick key visuals.
3. If Higgsfield MCP is *not* connected either, try `mcp__palmier-pro__get_timeline` and
   `list_models(type=video)`. If Palmier Pro *is* connected on your end, that's a viable
   alternative path — but confirm with the user before spending real credits through it, since
   it deviates from the established "Higgsfield-only for generation" architecture decision
   (get explicit sign-off, don't assume).
4. Either way: once you have a working generation tool, follow `CODEX.md` task 11's numbered
   steps exactly — they're tested and current as of this handoff. Generate the 4 key visuals,
   show them beside the Blender panels, get human approval, **then and only then** flip the
   approval fields (asset-manifest.json / storyboard-review.json / visual-handoff.json /
   `workspace/run/lipstick-cm-30s.permission.json`'s Seedance flags — both places, independently
   gated, confirmed by direct testing), then proceed to Seedance cost estimate → generation.
5. Record the outcome (success or failure) in `references/known-failure-patterns.md` as the next
   FP entry (or a "what actually worked" note) — this is the first real data point on whether the
   whole corrected pipeline actually produces a good result, which is the actual goal of this
   entire multi-session effort.

## Do not

- Do not use `workspace/prompts/lipstick-cm/final/clip_0{1,2}_*_seedance_final.txt` — superseded, FP-008.
- Do not use `workspace/assets/references/lipstick-cm/clip_02_product_plus_rina_lips_clean.png` as a
  Seedance input — it's the actual FP-002 collage from the failed run (has its own `DO_NOT_USE_*.md`
  warning file next to it).
- Do not treat `asset-manifest.json` approval alone as sufficient — the permission manifest's
  `prepare_seedance_cost_request`/`prepare_seedance_generation_request` flags are an independent
  gate that must also be flipped (confirmed by direct testing this session).
- Do not spend real credits through Palmier Pro without the user's explicit fresh sign-off, even
  if it turns out to be technically reachable — that's a deviation from the documented architecture
  decision, not just a technical detail.
