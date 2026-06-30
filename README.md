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
- `references/tiktok-ad-ops-workflow.md`
- `references/hermes-autonomous-loop.md`
- `references/blender-3d-preview-workflow.md`
- `skills/seedance/references/seedance-cm-workflow.md`
- `skills/seedance/references/image-to-video-handoff.md`
- `skills/seedance/references/tiktok-story-cast-workflow.md`
- `skills/seedance/references/higgsfield-mcp-demo-patterns.md`
- `skills/seedance/references/public-demand-short-video-patterns.md`
- `skills/seedance/references/tiktok-ad-ops-workflow.md`
- `skills/seedance/references/hermes-autonomous-loop.md`
- `skills/seedance/references/blender-3d-preview-workflow.md`

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

生成前の人間確認には `workspace/ui/generation-checkpoint.html` を開きます。現在のキャスト素材、source captures、60秒台本、Seedance visual-only、Higgsfield ElevenLabs音声、後付け字幕、権利確認をワークフローUIでチェックし、確認サマリーをコピーしてから費用見積もりと生成へ進みます。生成後は同じUIにresult URL、使用クレジット、OK/NG、再生成理由、編集対応メモを残します。

ターミナル指示に応じてCodexが裏で状態を更新し、それをUIに反映するライブ運用では `workspace/ui/live-workflow.html` を使います。`bash workspace/scripts/serve-ui.sh` でPC上に `127.0.0.1` 限定のローカルサーバーを起動し、Codexは `workspace/ui/state/generation-state.json` と `workspace/ui/state/asset-library.json` を更新します。ブラウザは `/api/factory-data` から、状態JSON、素材ライブラリ、Codex inbox、素材フォルダ、source captures、生成結果フォルダ、Blender有無の実データを読みます。UIの「この内容をCodexに送信」ボタンはローカルの `/api/send-to-codex` に送信し、ターミナルログと `workspace/ui/state/codex-inbox.jsonl` に指示を残します。工場風の表示では、AIの作業場を人間が覗くように、素材、台本、生成キュー、音声、字幕、レビューを1本の生成ラインとして確認できます。

Factory UIは個別ページも持ちます。`studio-lines.html`、`assets.html`、`cast-library.html`、`jobs.html`、`gates.html`、`activity.html` はすべて `/api/factory-data` を読み、ページごとに「意図」「実データ」「次の判断」を表示します。

Blender/3D previewを使う場合は `references/blender-3d-preview-workflow.md` を参照します。Blenderはローカル処理だけに使い、有料生成や外部投稿とは切り離します。

ローカル配布パッケージを作る場合は次を実行します。

```bash
bash workspace/scripts/package-local-factory.sh
```

生成されるZIPは `dist/seedance-local-factory-*.zip` に保存されます。デフォルトでは外部参照スクリーンショットと個人のCodex inboxログは含めません。inboxログも含めたい場合だけ `INCLUDE_INBOX=1 bash workspace/scripts/package-local-factory.sh` を使います。

市場・TikTok・UGC寄せの動画では、`references/public-demand-short-video-patterns.md` を使って、2秒フック、15秒商品広告、同一人物の旅Vlog、UGC広告バッチ、Virality Predictor後検証の型を先に選びます。公開投稿は需要シグナルとして分析し、映像素材そのものは権利確認なしに最終物へ使いません。

需要寄せで複数案を作る場合は、`workspace/prompts/public-demand-hook-variants-template.md` に2〜4案を書き、フック・想定感情・商品記憶・字幕方針を比較してから生成します。

TikTok広告として配信する前提では、`references/tiktok-ad-ops-workflow.md` を参照し、Spark Ads / Non-Spark Ads、Pixel / Events API、CV向け15秒構成、審査NG、LP整合、A/Bテスト、配信後学習、人間承認ゲートを確認します。テンプレートは `workspace/prompts/tiktok-*` に置いています。

Hermesに自律反復させる場合は、`references/hermes-autonomous-loop.md` と `workspace/prompts/hermes-run-permission.md` を使います。広告出稿、予算・入札変更、決済、Spark Ads利用、外部投稿、削除、高額生成、権利不明素材の本番利用は、run-permission manifestで明示許可された場合だけ実行できます。

## Safety Notes

- note公開、認証情報保存、権利不明素材の公開/商用利用はしない。
- 生成前に素材権利・公開可否・商用利用可否・主張の根拠を人間が確認する。
- 実在人物・有名人・第三者キャラクター風の素材は、ユーザーが使用権を確認した支給素材として扱う。権利不明の場合は内部ドラフトに留める。
- 的中保証、利益保証、No.1、公式提携、医療・金融・法律上の断定を根拠なしに入れない。
- AIは広告公開、予算変更、入札変更、決済、ログイン、外部投稿、広告削除を、run-permission manifestなしに実行しない。許可がある場合も範囲・上限・停止条件・ログ保存を守る。
