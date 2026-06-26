# /seedance

Use the installed `seedance` skill for this request.

Before task actions, read `skills/seedance/SKILL.md` and the referenced workflow file under `skills/seedance/references/`. Follow the commercial rights gate, budget lock, retry strategy, acceptance criteria, and delivery package rules.

## Arguments

- `brief`: commercial video brief, optional

## Workflow

1. Treat the rest of the message as a commercial-video brief.
2. If the brief is incomplete, collect only missing essentials: service or product name, pronunciation, audience, duration, aspect ratio, count, reference assets, audio policy, budget, job limit, and retry limit.
3. Do not generate paid jobs until budget and deliverables are clear.
4. Do not use third-party web assets in final commercial outputs unless the user confirms commercial rights.
5. Keep the workflow generic. Do not hard-code a project name, client name, celebrity, brand, or product unless the user provides it in the current brief.
