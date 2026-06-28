---
description: Plan and prepare a Higgsfield MCP / Seedance short-video workflow.
argument-hint: "[brief]"
---

# Seedance Short Video

Use the installed `seedance` skill for this request.

Note: some CLI/plugin versions do not expose personal plugin command files in the `/` command list.
If `/seedance` is not recognized, invoke the skill by typing a normal prompt that starts with
`seedance`, for example: `seedance 15秒の解説動画を9:16と16:9で作る`.

Before task actions, read `skills/seedance/SKILL.md` and the referenced workflow files under `skills/seedance/references/`. Follow the use-case router, image-to-video handoff, rights gate, budget lock, retry strategy, acceptance criteria, and delivery package rules.

## Arguments

- `brief`: short-video brief, optional

## Workflow

1. Treat the rest of the message as a short-video brief.
2. If the brief is incomplete, collect only missing essentials: video use case, project/name, pronunciation if relevant, audience, placement, duration, aspect ratio, count, reference assets, audio policy, budget, job limit, and retry limit.
3. Do not generate paid jobs until budget and deliverables are clear.
4. Do not use third-party web assets in final public/commercial outputs unless the user confirms rights.
5. Keep the workflow generic. Do not hard-code a project name, client name, celebrity, brand, or product unless the user provides it in the current brief.
6. Run Higgsfield account checks, cost estimates, and generation through Higgsfield MCP. Do not use a local `higgsfield` CLI or unrelated package.
