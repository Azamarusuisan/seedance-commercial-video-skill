# Cross-Agent Runbook

This runbook keeps the same CM workflow usable from Codex, Claude Code, Hermes, and OpenCrew-style automation.

## Current Project

- Service: 競馬AI
- Reading: けいばエーアイ
- Target: X users who like horse racing, AI, and visually strong short videos
- Desired reaction: "AIでここまで綺麗なCMを作れるのか"
- Creative direction: usage-scene style, futuristic AI horse-racing data visualization
- Final emphasis: フジ AI開発
- User-provided materials: none
- Asset policy: generated abstract visuals only unless rights are confirmed

## Human Gates

Stop and ask the user before passing each gate:

1. CM concept approval
2. Final Seedance prompt approval
3. Higgsfield login and paid/credit status
4. Cost approval
5. Video generation
6. note draft insertion
7. Any public release

The last gate must never be automated here. note publishing is prohibited.

## Standard Command Order

Run from the repository root:

```bash
bash workspace/scripts/preflight.sh
```

If GPT Image reference generation is required:

```bash
bash workspace/scripts/gpt-image-reference.sh
```

If Higgsfield login is needed:

```bash
bash workspace/scripts/open-higgsfield-login.sh
```

After the user logs in manually, prepare MCP status requests:

```bash
bash workspace/scripts/higgsfield-status.sh
```

Run the generated request files through the host-provided Higgsfield MCP tool, then record sanitized responses with:

```bash
bash workspace/scripts/record-mcp-json.sh account <mcp-account-response.json>
bash workspace/scripts/record-mcp-json.sh model <mcp-model-response.json>
```

After the prompt is final and explicitly approved, prepare MCP cost and generation requests:

```bash
APPROVED=1 bash workspace/scripts/seedance-cost.sh
APPROVED=1 bash workspace/scripts/seedance-generate.sh
```

Then run the generated request files through Higgsfield MCP and record sanitized responses:

```bash
bash workspace/scripts/record-mcp-json.sh cost <mcp-cost-response.json>
bash workspace/scripts/record-mcp-json.sh job <mcp-job-response.json>
```

Before final handoff:

```bash
bash workspace/scripts/secret-scan.sh
git status --short
```

## Environment Variables

Use environment variables only for the current shell/session. Do not write secrets to `.env`.

- `OPENAI_API_KEY`: needed only for GPT Image API reference generation.
- `HIGGSFIELD_MCP_AVAILABLE`: optional marker for shell preflight; real MCP availability must be checked in the host agent's MCP tool list.
- `HERMES_CDP_PORT`: defaults to `9223`.
- `HIGGSFIELD_MODEL`: defaults to `seedance_2_0`.
- `PROMPT_FILE`: defaults to `workspace/prompts/seedance-9x16-v1.txt`.
- `IMAGE_FILE`: defaults to `workspace/assets/reference-keiba-ai-gptimage-v1.png`, then falls back to `workspace/assets/reference-keiba-ai-v1.png`.
- `DURATION`: defaults to `15`.
- `RESOLUTION`: defaults to `1080p`.
- `BITRATE_MODE`: defaults to `high`.
- `GENERATE_AUDIO`: defaults to `false`.
- `MODE`: defaults to `std`.
- `DOWNLOAD`: set to `1` to attempt MP4 download after generation if a result URL is found.

## Approval Contract

The Seedance scripts require `APPROVED=1`. They also refuse to run if the prompt still contains pending markers such as `Do not run`, `pending`, or `proposal`.

When the user approves the final prompt, remove the pending header from `workspace/prompts/seedance-9x16-v1.txt` and keep only the actual Seedance prompt.

The scripts do not execute a local Higgsfield CLI. They prepare MCP request JSON under `workspace/mcp-requests/`. Use the Higgsfield MCP tool exposed by Codex, Claude Code, Hermes, or OpenCrew to execute the request.

## Logging Contract

All agents should record state in:

- `workspace/logs/generation-log.md`
- `workspace/logs/account-status.json`
- `workspace/logs/model-seedance_2_0.json`
- `workspace/logs/cost-estimate.json`
- `workspace/logs/job-v1.json`
- `workspace/logs/result-urls.md`
- `workspace/delivery/final-report.md`

Do not save raw cookies, bearer tokens, API keys, local storage dumps, browser profiles, or payment details.

## Browser Contract

Use only:

```bash
/Users/stork/Applications/Hermes Chrome.command
```

Do not use Safari, the normal Chrome profile, browser password managers, payment settings, or a signed-in personal browser profile.
