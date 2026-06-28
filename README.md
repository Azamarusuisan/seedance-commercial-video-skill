# seedance-commercial-video-skill

Higgsfield / Seedance short-video production skill and MCP-first workflow package. It supports commercials, social posts, product demos, app walkthroughs, explainers, event teasers, portfolio clips, background loops, and story scenes.

## Included Skill

- `SKILL.md`
- `skills/seedance/SKILL.md`

## Included Reference

- `references/seedance-cm-workflow.md`
- `references/image-to-video-handoff.md`
- `skills/seedance/references/seedance-cm-workflow.md`
- `skills/seedance/references/image-to-video-handoff.md`

## Cross-Agent Operation

Codex、Claude Code、Hermes、OpenCrew形式の実行環境から同じ手順で扱えるように、共通入口を追加しています。

- `AGENTS.md`
- `CLAUDE.md`
- `HERMES.md`
- `OPENCREW.md`
- `workspace/agent-guides/cross-agent-runbook.md`
- `workspace/scripts/`

まず以下を実行してください。

```bash
bash workspace/scripts/preflight.sh
```

Higgsfieldログインが必要な場合は、通常のブラウザではなくHermes Chromeを開きます。

```bash
bash workspace/scripts/open-higgsfield-login.sh
```

Higgsfield / Seedance 実行はMCP前提です。`workspace/scripts/higgsfield-status.sh`、`seedance-cost.sh`、`seedance-generate.sh` はローカルCLIを呼ばず、`workspace/mcp-requests/` にHiggsfield MCP用のリクエストJSONを作ります。MCP接続済みのエージェントがその内容でMCPを実行し、結果を `workspace/logs/` に保存してください。

画像生成から動画にする場合は、`workspace/scripts/gpt-image-reference.sh` で `workspace/assets/reference-image-v1.png` を作り、`IMAGE_FILE=workspace/assets/reference-image-v1.png` を指定して `seedance-cost.sh` / `seedance-generate.sh` を実行します。

## Safety Notes

- note公開、認証情報保存、権利不明素材の公開/商用利用はしない。
- 生成前に素材権利・公開可否・商用利用可否・主張の根拠を人間が確認する。
- 的中保証、利益保証、No.1、公式提携、医療・金融・法律上の断定を根拠なしに入れない。
