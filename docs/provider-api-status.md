# Provider API Status

Real provider adapters are intentionally disabled in Studio v2 P0.

- Seedance: mock only
- GPT Image: mock only
- ElevenLabs: mock only
- Palmier / upscale / export: not wired into Studio v2

Human-run integration can be added after OPEN-2 is resolved. Until then, all automated tests use `studio.providers.mock.MockProvider`.
