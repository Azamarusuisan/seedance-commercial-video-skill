# Seedance Handoff After Approval

Seedance handoff is blocked until all of these are true:

- 4 primary key visuals exist.
- Each key visual has `asset-manifest.json`.
- `asset_kind=photoreal_key_visual`.
- `role=visual_truth`.
- `approval_status=approved`.
- `seedance_input_allowed=true`.
- `known_failure_checked_at` exists.
- `learning-preflight.md` contains `can_prepare_seedance_request: true`.
- run-permission manifest allows `prepare_seedance_cost_request=true`.
- model, duration, resolution, output path, and total cost are approved by a human.

Until then:

- no Seedance cost request
- no Seedance generation request
- no audio/BGM/SFX/subtitles/Palmier finishing
