# OpenCrew Instructions

Follow `AGENTS.md` and `workspace/agent-guides/cross-agent-runbook.md`.

Suggested crew roles:

- Planner: reads the brief, asks only missing creative questions, and updates `workspace/inputs/project-brief.md`.
- Creative Director: updates `workspace/briefs/cm-brief.md` and keeps claims safe.
- Prompt Engineer: writes `workspace/prompts/seedance-9x16-v1.txt` and image prompts.
- Operator: runs only the scripts in `workspace/scripts/` and the host-provided Higgsfield MCP tool.
- Delivery Reviewer: checks `workspace/delivery/pre-delivery-check.md`, `known-limitations.md`, and `final-report.md`.

Crew handoff rules:

- Pass file paths and approval status, not secrets.
- Do not run Higgsfield generation until the Operator sees explicit approval.
- Do not use a local `higgsfield` CLI or unrelated PyPI package for video generation. Use Higgsfield MCP.
- Do not let any role publish note content.
