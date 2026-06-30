# Local Security Review Report

## Executive Summary

Scope was expanded to the maximum safe local scope:

- Repository: `/Users/zettai/Downloads/seedance-commercial-video-skill`
- Local UI: `http://localhost:8787`
- No external targets, no paid generation, no staging, no production, no third-party scanning.

Result:

- 2 practical local UI risks were found and fixed.
- 1 hardening issue was fixed.
- No high-confidence secrets were found by the existing secret scan.
- Local non-destructive HTTP checks pass.

## Scope

In scope:

- `workspace/ui/server.py`
- `workspace/ui/*.js`
- `workspace/ui/*.html`
- `workspace/scripts/*.sh`
- workflow state files and local server behavior

Out of scope:

- Higgsfield external API calls
- Palmier automation
- GitHub remote operations
- Any external domain or staging/prod target
- Authenticated scans, brute force, load tests, destructive tests

## Threat Model

Assets:

- Local workflow state JSON
- Seedance job metadata and result URLs
- Local generated MP4 paths
- Codex inbox messages
- Terminal forwarding behavior
- Repo files served by the local UI server

Trust boundaries:

- Browser page -> local UI server
- Local UI server -> repository files
- Local UI server -> Terminal forwarding
- Local scripts -> logs and MCP handoff JSON

Main attacker model:

- A malicious webpage opened in the user's browser attempts to POST to `localhost:8787`.
- A local user or local process attempts to read sensitive-looking repo paths through the static server.
- A malformed local state entry attempts to inject unsafe media paths into the UI.

## Findings

### F-001: Cross-origin POST could send instructions to local Codex inbox

Severity: High

Impact:

- A malicious webpage could attempt a cross-origin POST to `/api/send-to-codex`.
- Before the fix, CORS used `Access-Control-Allow-Origin: *`.
- Terminal forwarding was enabled by default in `serve-ui.sh`, increasing impact if the browser accepted the request path.

Evidence:

- `workspace/ui/server.py` previously allowed `Access-Control-Allow-Origin: *`.
- `workspace/scripts/serve-ui.sh` previously defaulted `CODEX_FORWARD_TO_TERMINAL=1`.

Root cause:

- Local-only service assumed local trust but exposed a browser-callable POST endpoint without origin restriction.

Fix:

- Restrict CORS to localhost origins on the same port.
- Reject disallowed Origins with HTTP 403.
- Default Terminal forwarding to off.

Changed files:

- `workspace/ui/server.py`
- `workspace/scripts/serve-ui.sh`

Verification:

```bash
curl -s -o /tmp/out -w '%{http_code}' \
  -H 'Origin: https://evil.example' \
  -H 'Content-Type: application/json' \
  --data '{"message":"security-test"}' \
  http://localhost:8787/api/send-to-codex
# 403
```

Regression:

- `workspace/scripts/security-local-check.sh`

### F-002: Static server could expose sensitive-looking repository paths

Severity: Medium

Impact:

- The local UI server serves from repository root.
- If files like `.env`, token files, cookie exports, or `.git/config` existed, they could be requested through the static server.

Evidence:

- `SimpleHTTPRequestHandler` served `REPO_ROOT`.

Root cause:

- Static file serving had no denylist for sensitive path names.

Fix:

- Block `.git`.
- Block `.env` variants.
- Block filenames containing `cookie`, `token`, `secret`, `session`, or `credential`.

Changed file:

- `workspace/ui/server.py`

Verification:

```bash
curl -s -o /tmp/out -w '%{http_code}' http://localhost:8787/.git/config
# 404

curl -s -o /tmp/out -w '%{http_code}' http://localhost:8787/.env
# 404
```

Regression:

- `workspace/scripts/security-local-check.sh`

### F-003: UI media path helper allowed `file:` and `data:` schemes

Severity: Low

Impact:

- State JSON is local, but allowing `file:` or `data:` in generated media paths is unnecessary.
- It widens the rendering surface if local state is corrupted.

Evidence:

- `toProjectPath()` in UI scripts allowed `https?:`, `data:`, and `file:`.

Root cause:

- The helper was permissive for convenience.

Fix:

- Allow only `http(s)`, absolute paths, `state/*`, or repo-relative paths.

Changed files:

- `workspace/ui/factory-futuristic.js`
- `workspace/ui/factory-pages.js`

Verification:

```bash
node --check workspace/ui/factory-futuristic.js
node --check workspace/ui/factory-pages.js
```

## Positive Observations

- Server binds to localhost by default.
- Non-local bind now requires `ALLOW_NONLOCAL_UI=1`.
- Request body size for `/api/send-to-codex` is capped at 256 KB.
- Secrets are redacted in `record-mcp-json.sh`.
- `secret-scan.sh` exists and passed.
- Generation scripts include approval gates.
- Current workflow check confirms generated MP4s exist, are readable, are 1080x1920, are about 15 seconds, and have no audio tracks.

## Verification Commands

Executed:

```bash
python3 -m py_compile workspace/ui/server.py
bash -n workspace/scripts/*.sh
node --check workspace/ui/factory-futuristic.js
node --check workspace/ui/factory-pages.js
bash workspace/scripts/secret-scan.sh
bash workspace/scripts/ascension-workflow-check.sh
bash workspace/scripts/security-local-check.sh
git diff --check
```

HTTP checks:

```text
bad Origin POST blocked -> 403
.git static path blocked -> 404
.env static path blocked -> 404
factory data reachable -> 200
local_only=true and terminal_forward=false
```

## Remaining Risks

- This was not a full authenticated application pentest; the app has no user auth model.
- No external or staging tests were run by design.
- If `ALLOW_NONLOCAL_UI=1` is used, the server becomes a trusted-network service and needs stronger access control.
- `/api/factory-data` exposes local workflow metadata to local browser contexts; acceptable for localhost, not acceptable for network exposure.

## Next Safe Steps

1. Keep `CODEX_FORWARD_TO_TERMINAL=0` by default.
2. Run `workspace/scripts/security-local-check.sh` after server changes.
3. Do not run ZAP or external scans without a separate explicit scope and approval.
