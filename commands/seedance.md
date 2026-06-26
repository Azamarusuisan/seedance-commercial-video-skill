---
description: Plan, generate, review, or package a short commercial video with the generic Seedance workflow.
---

# Seedance Commercial Video Workflow

Use the installed `seedance` skill for this request.

Before task actions, read `skills/seedance/SKILL.md` and the referenced workflow file under `skills/seedance/references/`. Follow the commercial rights gate, budget lock, retry strategy, acceptance criteria, and delivery package rules.

## Command Behavior

When the user runs `/seedance`, treat the rest of the message as a commercial-video brief. If the brief is incomplete, collect only the missing essentials:

- service, product, or brand name
- required pronunciation
- target audience
- output count, duration, and aspect ratio
- model, product, screenshot, logo, or brand references
- whether AI voice-over and AI in-video text are allowed
- maximum budget, maximum job count, and maximum retry count

Do not generate paid jobs until the budget and deliverables are clear. Do not use third-party web assets in final commercial outputs unless the user confirms they have commercial rights.

Keep the workflow generic. Do not hard-code a project name, client name, celebrity, brand, or product into prompts unless the user provides it in the current brief.
