# Hermes Autonomous Loop

Use this reference when Hermes or another browser-capable agent should autonomously iterate Seedance/Higgsfield/TikTok ad creative work.

Core rule: autonomous execution is allowed only inside a run-permission manifest. If the action is not explicitly allowed, stop at planning and write the missing permission.

## 1. Permission Model

Do not treat a casual "run it" as unlimited permission. Before autonomous execution, create or read:

`workspace/prompts/hermes-run-permission.md`

The manifest must define:

- run ID
- owner / approver
- allowed platforms and accounts
- allowed actions
- disallowed actions
- login/session mode
- budget caps
- generation caps
- ad account caps
- asset rights status
- high-risk category status
- allowed time window
- stop conditions
- log path
- emergency stop signal

## 2. Action Tiers

### Tier A: Free Autonomous Work

Allowed by default during a normal creative task:

- reference analysis
- contact sheets
- script drafts
- hook variants
- storyboard panels
- Seedance prompt drafts
- subtitle/telop plans
- NG expression checks
- LP consistency checklists
- A/B test tables
- post-launch diagnosis from user-provided metrics

### Tier B: Paid Generation Work

Allowed only when the manifest sets caps:

- image generation
- Seedance video generation
- ElevenLabs/TTS generation
- upscaling
- repeated regenerations
- downloading and packaging outputs

Required caps:

- max total credits or spend
- max jobs
- max retries per concept
- max duration/resolution
- allowed models
- output directory

### Tier C: Ad Account / Publishing Work

Allowed only when the manifest explicitly lists the exact action:

- use an already-authenticated browser session
- pause for user-completed login, then continue
- ad submission / publish
- campaign creation
- campaign/ad/ad group pause
- budget change
- bid change
- schedule change
- targeting change
- Spark Ads authorization/use
- external post creation
- pinned comment / comment reply
- UTM/URL updates in ad setup

Required scope:

- account ID/name
- campaign/ad group/ad IDs or creation naming rule
- max spend/budget
- max bid
- allowed objective
- allowed target region
- allowed LP URL
- allowed creative IDs
- login/session mode: existing session only, user-completed login, or no login
- approval owner

### Tier D: Destructive / Billing / Identity Work

Allowed only when manifest explicitly allows the exact action and gives a rollback or no-rollback acknowledgement:

- campaign/ad/ad group deletion
- billing/payment changes
- account linking
- login/session changes
- permission changes
- irreversible publish/post deletion
- use of real people/creator assets in paid ads
- high-risk regulated category launch

If rollback is impossible, log `no_rollback_ack=true` before executing.

## 3. Standard Loop

1. Read run-permission manifest.
2. Create run plan.
3. Check stop conditions and current logs.
4. Gather references and current metrics.
5. Generate 2-4 hook/concept variants.
6. Score variants against objective.
7. Produce scripts/prompts/assets within budget caps.
8. Run allowed generation or account operations only if manifest permits.
9. Verify outputs.
10. Record iteration log.
11. Pick next action or stop.

Never run unbounded loops. Each loop must have a max iteration count.

## 4. Stop Conditions

Stop immediately when:

- max spend/credits/jobs/retries reached
- current time is outside approved window
- required asset rights are unknown for a paid/public action
- high-risk category lacks approval owner
- LP URL differs from manifest
- account/campaign ID differs from manifest
- platform asks for login/MFA/payment confirmation not covered by manifest
- Hermes would need to store, reveal, or type a password/secret
- review rejection repeats twice with same reason
- generation fails three times on the same concept
- `workspace/run/HERMES_STOP` exists
- user says stop/pause

## 5. Logging

Before and after every Tier B/C/D action, append to:

`workspace/prompts/hermes-iteration-log.csv`

Required fields:

- timestamp
- run ID
- tier
- action
- target account/campaign/job
- input artifact
- output artifact
- cost/spend estimate
- result
- reason
- next action

## 6. Output Package

Every autonomous run should leave:

- run permission manifest
- run plan
- iteration log
- generated prompts/scripts
- source/reference notes
- output paths/URLs
- failed attempts and reasons
- winning pattern notes
- next run recommendation

## 7. Permission Wording

This is acceptable:

```text
For run TT-2026-06-29-001, Hermes may generate up to 8 Seedance drafts, spend up to X credits, use only assets in workspace/assets/cast with rights_status=user_supplied_confirmed or generated, publish no ads, and stop after 2 failed generations per concept.
```

This can allow ad operations:

```text
For run TT-2026-06-29-002, Hermes may publish approved creatives A and B as Non-Spark Ads to TikTok account <account>, campaign <campaign>, daily budget cap <amount>, bid cap <amount>, LP <url>, between <time window>. Hermes may pause those ads if spend exceeds <amount> without CV or if review is rejected. No deletion or billing changes allowed.
```

Do not execute if permission is vague, missing caps, or references "anything needed."

## 8. Login And Secrets

Hermes may operate only through an already-authenticated profile or after the user completes login/MFA manually. Do not store passwords, tokens, recovery codes, payment credentials, or MFA secrets in repo files, prompts, logs, screenshots, or manifests.
