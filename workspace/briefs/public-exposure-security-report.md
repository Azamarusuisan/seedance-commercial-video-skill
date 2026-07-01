# Public Exposure Security Report

## Scope

Maximum safe scope was applied without stealth, evasion, or third-party testing.

Checked:

- Local repository tracked files
- Git remote configuration
- Runtime logs and state files
- Higgsfield handoff metadata stored locally
- Local UI server behavior

Not performed:

- No attack against Higgsfield.
- No attack against GitHub.
- No staging or production scan.
- No stealth, evasion, brute force, DoS, or authenticated third-party testing.

Reason:

- Those targets are third-party or require a separate written authorization window. Defensive exposure review of our own repo and local server is allowed and was performed.

## Key Result

The main public-exposure risk was not a password or API key. It was operational metadata:

- Higgsfield result URLs
- CloudFront user path fragments
- account/credit status logs
- job JSON with prompt and media URLs
- runtime UI state containing result URLs and messages

These are not classic secrets, but they should not be committed to a public repository.

## Fixes Applied

### 1. Runtime logs and state removed from Git tracking

Removed from the Git index only. Local files remain on disk.

- `workspace/logs/*.json`
- `workspace/logs/*.md`
- `workspace/mcp-requests/*.json`
- `workspace/ui/state/*.json`

This prevents generated result URLs, account status, and local workflow state from being published on the next commit.

### 2. `.gitignore` expanded

Added:

```gitignore
workspace/logs/*.json
workspace/logs/*.md
workspace/mcp-requests/*.json
workspace/ui/state/*.json
```

### 3. Public leak check added

File:

- `workspace/scripts/security-public-leak-check.sh`

Purpose:

- Scan only Git-tracked files.
- Fail if tracked files contain likely public-leak patterns:
  - `cloudfront.net/user_`
  - `subscription_plan_type`
  - Higgsfield account status markers
  - common token/key formats

Current result:

```text
[info] public-leak check passed
```

### 4. Local UI hardening remains active

Already fixed:

- bad Origin POST blocked with 403
- `.git/config` blocked with 404
- `.env` blocked with 404
- Terminal forwarding defaults to false
- non-local bind requires `ALLOW_NONLOCAL_UI=1`

## Verification

Executed:

```bash
python3 -m py_compile workspace/ui/server.py
bash -n workspace/scripts/*.sh
node --check workspace/ui/factory-futuristic.js
node --check workspace/ui/factory-pages.js
bash workspace/scripts/secret-scan.sh
bash workspace/scripts/security-public-leak-check.sh
bash workspace/scripts/security-local-check.sh
bash workspace/scripts/ascension-workflow-check.sh
git diff --check
```

All passed.

## Current Git Meaning

The `D` entries for logs/state in `git status` mean:

- they will be removed from Git tracking on commit
- the local files still exist
- they are now ignored and should not be pushed

This is intentional.

## Remaining Caution

If these URLs or logs were already pushed before this change, removing them from the next commit does not erase prior GitHub history. Full history cleanup requires a separate explicit task and force-push plan.

## Safe Next Step

Before any push:

```bash
bash workspace/scripts/security-public-leak-check.sh
```

If it fails, do not push.
