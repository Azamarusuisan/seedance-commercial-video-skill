# Hermes Run Permission Manifest

Status: required before autonomous paid generation, ad-account operations, external posting, destructive actions, or regulated-category launch.

- Run ID:
- Owner / approver:
- Approval timestamp:
- Platform(s):
- Account ID/name:
- Campaign/ad group/ad IDs or creation naming rule:
- LP URL:
- Objective:
- Allowed time window:
- Login/session mode: existing session only / user-completed login / no login
- High-risk category: none / beauty / health / medical / pharma / supplement / diet / finance / investment / real estate / jobs / politics / religion / gambling / minors / other
- Legal/ad review owner:
- Asset rights allowed:
  - generated:
  - user_supplied_confirmed:
  - licensed:
  - internal_draft_only:
  - unknown:
- AIGC disclosure checked: yes / no / not needed

## Allowed Actions

Mark only what is allowed.

- Tier A planning/research:
- Tier B paid generation:
- Tier C ad publish/account operations:
- Tier D destructive/billing/identity operations:

Exact allowed actions:

- TBD

Explicitly disallowed actions:

- TBD

## Caps

- Max total credits/spend:
- Max generation jobs:
- Max retries per concept:
- Max Seedance duration:
- Max resolution:
- Allowed models:
- Max ad daily budget:
- Max bid:
- Max total ad spend:
- Max campaigns/ad groups/ads:
- Max external posts/comments:

## Login / Secrets

- Hermes may use existing authenticated session:
- Hermes may pause for user-completed login/MFA:
- Hermes may store passwords/tokens/MFA/payment secrets: no

## Stop Conditions

- Stop file: `workspace/run/HERMES_STOP`
- Stop on spend cap:
- Stop on job cap:
- Stop on repeated review rejection:
- Stop on repeated generation failure:
- Stop on LP/account mismatch:
- Stop on missing rights:
- Stop on login/MFA/payment prompt:

## Logging

- Run plan path: `workspace/prompts/hermes-run-plan.md`
- Iteration log path: `workspace/prompts/hermes-iteration-log.csv`
- Output package path:

## No-Rollback Acknowledgement

Required only for irreversible actions.

- no_rollback_ack: false
- actions covered:
