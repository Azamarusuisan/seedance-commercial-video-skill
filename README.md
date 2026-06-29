# seedance-commercial-video-skill

Higgsfield / Seedance short-video production skill and MCP-first workflow package. It supports commercials, social posts, product demos, app walkthroughs, explainers, event teasers, portfolio clips, background loops, and story scenes.

## Included Skill

- `SKILL.md`
- `skills/seedance/SKILL.md`

## Included Reference

- `references/seedance-cm-workflow.md`
- `references/image-to-video-handoff.md`
- `references/tiktok-story-cast-workflow.md`
- `references/higgsfield-mcp-demo-patterns.md`
- `references/public-demand-short-video-patterns.md`
- `skills/seedance/references/seedance-cm-workflow.md`
- `skills/seedance/references/image-to-video-handoff.md`
- `skills/seedance/references/tiktok-story-cast-workflow.md`
- `skills/seedance/references/higgsfield-mcp-demo-patterns.md`
- `skills/seedance/references/public-demand-short-video-patterns.md`

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

TikTok風の物語動画や劇団型のキャスト運用では、`workspace/assets/cast/` に人物・小道具・背景素材を置き、`workspace/assets/cast/cast-manifest.example.json` をコピーして案件ごとの素材manifestを作ります。Seedanceに渡す参照画像は原則1枚に絞り、複数キャストや実キャラ風素材はクリップごとに参照画像を切り替えるか、プロンプトで明示します。

60秒の物語動画は、生成前に `workspace/prompts/tiktok-storyboard-60s-template.md` を使って8〜12コマの台本を作り、映像・セリフ・字幕・素材・次の展開理由を固定してから4本前後のSeedanceプロンプトへ分解します。外部のX投稿やHIGGSFIELDMCP-demoは `references/higgsfield-mcp-demo-patterns.md` に制作パターンとして記録し、素材そのものは権利確認なしに最終物へ使いません。

市場・TikTok・UGC寄せの動画では、`references/public-demand-short-video-patterns.md` を使って、2秒フック、15秒商品広告、同一人物の旅Vlog、UGC広告バッチ、Virality Predictor後検証の型を先に選びます。公開投稿は需要シグナルとして分析し、映像素材そのものは権利確認なしに最終物へ使いません。

需要寄せで複数案を作る場合は、`workspace/prompts/public-demand-hook-variants-template.md` に2〜4案を書き、フック・想定感情・商品記憶・字幕方針を比較してから生成します。

## Safety Notes

- note公開、認証情報保存、権利不明素材の公開/商用利用はしない。
- 生成前に素材権利・公開可否・商用利用可否・主張の根拠を人間が確認する。
- 実在人物・有名人・第三者キャラクター風の素材は、ユーザーが使用権を確認した支給素材として扱う。権利不明の場合は内部ドラフトに留める。
- 的中保証、利益保証、No.1、公式提携、医療・金融・法律上の断定を根拠なしに入れない。
