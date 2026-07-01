# Codex To Claude Handoff — 2026-07-01

## Current Status

Codex pulled latest `main` and executed the safe part of `CODEX.md` task 11 for `lipstick-cm-30s`.

Completed:

- Read `CODEX.md`, `AGENTS.md`, `workspace/agent-guides/cross-agent-runbook.md`.
- Read `references/known-failure-patterns.md` FP-001 through FP-008.
- Read `references/cm-creative-craft-knowledge.md` prompt rules and checklist.
- Prepared Higgsfield MCP image request JSONs for the 4 photoreal key visual prompts.
- Did not execute Higgsfield MCP, Seedance, Palmier generation, audio, upscale, or publishing.

Prepared local request payloads:

- `workspace/mcp-requests/lipstick-cm-keyvisual-clip_01_start-image2.request.json`
- `workspace/mcp-requests/lipstick-cm-keyvisual-clip_01_end-image2.request.json`
- `workspace/mcp-requests/lipstick-cm-keyvisual-clip_02_final-image2.request.json`
- `workspace/mcp-requests/lipstick-cm-keyvisual-clip_02_lips-image2.request.json`

Important caveat:

- `clip_02_lips` is currently prepared from the lips crop only because `clip_01_end_key.png` does not exist yet.
- The preferred final execution for `clip_02_lips` is the multi-image route in `workspace/projects/lipstick-cm-30s/shots/clip_02_lips/storyboard-request.json`: first generate `clip_01_end_key.png`, then use it as the world/lighting reference together with `workspace/assets/cast/generated_20260629/rina_hayun_lips_closeup.png`.

## Ready-To-Paste Claude Task

```text
このリポジトリの `lipstick-cm-30s` を引き継いでください。

対象:
/Users/zettai/Downloads/seedance-commercial-video-skill

まず読んでください:
- CODEX.md
- CLAUDE.md
- WORKFLOW.md
- references/known-failure-patterns.md
- references/cm-creative-craft-knowledge.md
- workspace/projects/lipstick-cm-30s/codex-to-claude-handoff-20260701.md
- workspace/projects/lipstick-cm-30s/keyvisual-generation-approval-v2.md
- workspace/projects/lipstick-cm-30s/storyboard/06-seedance-handoff-after-approval.md

状況:
Codexは `CODEX.md` task 11 の安全な準備だけ完了しました。4枚の写実キービジュアル用 Higgsfield MCP request JSON は `workspace/mcp-requests/lipstick-cm-keyvisual-*-image2.request.json` に準備済みです。ただし、この環境ではHiggsfield MCP実行ツールが無いため、画像生成そのものは未実行です。

絶対ルール:
- 有料Seedance生成をしない。
- Seedanceコスト見積もりに進まない。
- Palmier生成、音声生成、upscale、外部投稿、広告公開をしない。
- raw Blender render を Seedance の start_image / end_image にしない。
- `workspace/assets/references/lipstick-cm/clip_02_product_plus_rina_lips_clean.png` を使わない。これは失敗済み合成参照です。
- `clip_02_lips` は商品+唇を1枚に合成しない。

やること:
1. Higgsfield MCP の画像モデル名、`image2` の有無、単一/複数参照画像入力のパラメータを確認する。
2. 可能なら、準備済み request JSON を使って以下3枚を生成する:
   - clip_01_start_key
   - clip_01_end_key
   - clip_02_final_key
3. `clip_02_lips` は `clip_01_end_key.png` 生成後に、以下2枚参照で実行する:
   - `workspace/assets/references/lipstick-cm/keyvisuals/clip_01_end_key.png` = world / lighting / color-grade reference
   - `workspace/assets/cast/generated_20260629/rina_hayun_lips_closeup.png` = anonymous lips and skin-tone support only
4. 生成結果を `workspace/assets/references/lipstick-cm/keyvisuals/` に保存する。
5. sanitize済みMCPレスポンスだけを `workspace/logs/` に保存し、必要なら `record-mcp-json.sh image <response.json>` を使う。
6. 4枚を元のBlenderパネルと並べて、人間承認用に提示する。
7. 承認を得るまで、asset-manifest / storyboard-review / visual-handoff を approved にしない。
8. 承認を得るまで、permission manifest の Seedance 関連フラグを true にしない。

出力:
- 生成した画像パス
- 使ったMCPモデルと参照画像パラメータ
- 4枚比較の確認結果
- まだ人間承認待ちであること
- 実行していないこと: Seedance / audio / upscale / publish
```
