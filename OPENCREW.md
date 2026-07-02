# v1凍結 / workspace/ 経路の有料生成禁止

This repository is entering the Studio v2 implementation track described in `PLAN.md`.
The existing v1 `workspace/` generation paths are frozen for new paid execution.
Do not run Higgsfield, Seedance, Palmier, ElevenLabs, upscale, export, publishing, or external-posting actions through v1.
Treat `workspace/`, `references/`, and `tests/fixtures/` as preserved legacy evidence unless a task explicitly says to add a non-destructive notice or new v2-compatible file.

# OpenCrew Instructions

Follow `AGENTS.md` and `workspace/agent-guides/cross-agent-runbook.md`.

Suggested crew roles:

- Planner: reads the brief, asks only missing creative questions, and updates `workspace/inputs/project-brief.md`.
- Creative Director: updates the project brief and keeps claims/rights safe for the intended use.
- Prompt Engineer: writes Seedance prompts and reference-image prompts for the requested use case.
- Operator: runs only the scripts in `workspace/scripts/` and the host-provided Higgsfield MCP tool.
- Delivery Reviewer: checks `workspace/delivery/pre-delivery-check.md`, `known-limitations.md`, and `final-report.md`.

Crew handoff rules:

- Pass file paths and approval status, not secrets.
- Do not run Higgsfield generation until the Operator sees explicit approval for the use case, brief, reference image/assets, prompt, budget, and Higgsfield state.
- Do not use a local `higgsfield` CLI or unrelated PyPI package for video generation. Use Higgsfield MCP.
- Do not let any role publish note content.
