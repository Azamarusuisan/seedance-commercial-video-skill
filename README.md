# seedance-commercial-video-skill

Higgsfield / Seedance CM production skill and MCP-first workflow package.

## Included Skill

- `SKILL.md`
- `skills/seedance/SKILL.md`

## Included Reference

- `references/seedance-cm-workflow.md`
- `skills/seedance/references/seedance-cm-workflow.md`

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

## Safety Notes

- note公開、認証情報保存、権利不明素材の商用利用はしない。
- 生成前に素材権利・商用利用可否・主張の根拠を人間が確認する。
- 的中保証、利益保証、No.1、公式提携、医療・金融・法律上の断定を根拠なしに入れない。
