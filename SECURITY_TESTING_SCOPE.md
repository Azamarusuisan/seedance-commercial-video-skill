# SECURITY_TESTING_SCOPE

## Purpose

This security review is limited to the local repository and local UI server for `seedance-commercial-video-skill`.

Purpose:

- Identify security risks in the local workflow UI and helper scripts.
- Avoid destructive, high-load, credential-exposing, or third-party-impacting tests.
- Produce safe findings, fixes, and follow-up test ideas.

## Authorized Targets

- Repository:
  - `/Users/zettai/Downloads/seedance-commercial-video-skill`
- Allowed local environment:
  - `http://localhost:8787`
  - `http://127.0.0.1:8787`

## Out of Scope

- Any external domain, API, IP, staging server, or production server.
- Higgsfield paid generation, account actions, or API calls.
- Palmier Pro automation beyond local status inspection.
- GitHub remote access.
- Brute force, DoS, load testing, credential attacks, persistence, stealth, lateral movement, or destructive operations.
- Reading or printing secrets, tokens, cookies, credentials, browser storage, or real user data.

## Allowed Testing Mode

1. Source-code review.
2. Threat modeling.
3. Local non-destructive checks.
4. Small test/demo scripts that do not mutate production data.

## Human Approval Required

Ask before:

- Any external network access.
- Any security scanner.
- Any authenticated request.
- Any destructive file or data operation.
- Any command expected to run longer than 5 minutes.
- Any request burst above 30 requests per minute.

## Evidence Handling

- Do not print secrets.
- Use file paths and line references instead of raw sensitive data.
- Keep reproduction local and non-destructive.

## Required Output

Report findings with:

- Title
- Severity
- Impact
- Evidence
- Root cause
- Safe reproduction or verification
- Recommended fix
- Regression test idea
- Remaining questions
