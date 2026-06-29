---
description: Plan and prepare a Higgsfield MCP / Seedance short-video workflow.
argument-hint: "[brief]"
---

# Seedance Short Video

Use the installed `seedance` skill for this request.

Note: some CLI/plugin versions do not expose personal plugin command files in the `/` command list.
If `/seedance` is not recognized, invoke the skill by typing a normal prompt that starts with
`seedance`, for example: `seedance 15秒の解説動画を9:16と16:9で作る`.

Before task actions, read `skills/seedance/SKILL.md` and the referenced workflow files under `skills/seedance/references/`. Follow the use-case router, image-to-video handoff, TikTok storyboard/cast-library route, demand-pattern route, TikTok ad-ops route, Hermes autonomous-loop route, rights gate, budget lock, retry strategy, acceptance criteria, and delivery package rules.

## Arguments

- `brief`: short-video brief, optional

## Workflow

1. Treat the rest of the message as a short-video brief.
2. If the brief is incomplete, collect only missing essentials: video use case, project/name, pronunciation if relevant, audience, placement, duration, aspect ratio, count, reference assets, audio policy, demand target for social work, TikTok ad context when paid ads are involved, autonomous run-permission manifest when execution is requested, storyboard panel count for narrative work, budget, job limit, and retry limit.
3. Do not generate paid jobs until budget and deliverables are clear.
4. Do not use third-party web assets in final public/commercial outputs unless the user confirms rights.
5. Keep the workflow generic. Do not hard-code a project name, client name, celebrity, brand, or product unless the user provides it in the current brief.
6. Run Higgsfield account checks, cost estimates, and generation through Higgsfield MCP. Do not use a local `higgsfield` CLI or unrelated package.
7. For TikTok/story work, make the storyboard script first, then collapse approved panels into Seedance prompts. Keep exact narration in external TTS and exact Japanese subtitles in editing.
8. For viral/market-demand work, pick a hook pattern first, then generate 2-4 concept variants before spending credits on polished output.
9. For TikTok Ads or autonomous Hermes work, execute only within an explicit run-permission manifest; otherwise stop before publishing, account operations, external posting, paid generation, or destructive actions.
