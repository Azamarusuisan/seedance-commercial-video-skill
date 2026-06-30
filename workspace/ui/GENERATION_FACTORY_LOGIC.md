# Generation Factory Logic Review

最終更新: 2026-06-30
対象: `workspace/ui/live-workflow.html` / `workspace/ui/server.py` / `workspace/ui/state/*.json`

## 目的

`SEEDANCE THEATER / GENERATION FACTORY` を、ローカルPC上で動くAI動画生成工場UIとして作る。

見せたい体験:

- Seedance / Higgsfield / ElevenLabs / subtitle post edit が一つの制作ラインとして見える
- AIが裏で動画生成ラインを回しているような、映画スタジオ兼工場兼トレーダー端末UI
- 人間が「今AIが何をしているか」「どの素材を使うか」「どこで止まっているか」を見る
- ただし本当に課金生成、広告公開、投稿公開、外部API実行はしない

## 絶対ルール

- Higgsfield / Seedance / ElevenLabs / TikTok / 広告APIをUIから直接呼ばない
- 有料生成、広告公開、外部投稿、ログイン、決済、削除操作を自動実行しない
- `human approval required` と `publish blocked` は必ず画面に残す
- 実データがないKPIを本番数字のように見せない
- mock演出を使う場合は、コード上で `MOCK_*_UI_ONLY` と分かる名前にする
- 権利不明素材やブロック済み素材をアクティブ素材に混ぜない

## ローカル構成

起動:

```bash
bash workspace/scripts/serve-ui.sh
```

URL:

```text
http://127.0.0.1:8787/workspace/ui/live-workflow.html
```

ローカルAPI:

```text
GET  /api/factory-data
POST /api/send-to-codex
```

`127.0.0.1` バインドが基本。配布パッケージもローカルPCをサーバーとして動かす前提。

## データソース

本番用として信用してよい実データ:

| データ | ファイル / API | 用途 |
|---|---|---|
| workflow / jobs / gates / current_work | `workspace/ui/state/generation-state.json` | 工程、ジョブ、停止ゲート、現在作業 |
| asset library | `workspace/ui/state/asset-library.json` | 素材保管庫、source captures、外部参考URL、blocked records |
| Codex inbox | `workspace/ui/state/codex-inbox.jsonl` | UIからCodexへ送った指示ログ |
| cast manifest | `workspace/assets/cast/generated_20260629/cast-manifest.json` | AI演者ライブラリ |
| source captures | `videos/**/assets/source-captures/*` | UI / Codex操作 / 説明動画素材 |
| generated outputs | `videos/**/*.mp4` など | 生成後の成果物 |

`/api/factory-data` は上記を集約してUIへ返す。

## KPI表示方針

本番用では以下を分ける。

### 実データで出せるもの

- Generated cast count
- Source capture count
- Jobs count
- Active jobs count
- Blocked gates count
- Inbox messages count
- Render output file count
- Git changed files count
- Current stage
- Current work
- Last inbox message
- File modified time

### 実データが入るまで出してはいけないもの

- Today’s Generations
- Rendering Speed
- Success Rate
- Avg Render Time
- Cost Estimate
- GPU Usage
- Render time left
- Real success/completion rate

これらは現時点では本物の計測がないため、本番UIでは次のように表示する。

- `pending`
- `not measured`
- `not estimated`
- `no output yet`
- `approval required`

演出として数字を揺らす場合は、UI mock telemetryとして明示し、メインKPIとは分離する。

## 本番用KPI置き換え案

現在のmock KPIを以下へ置き換える。

| 表示名 | 実データ | 表示例 |
|---|---|---|
| Active Stage | `state.meta.active_stage` | `cost_estimate` |
| Planned Jobs | `state.jobs.length` | `4` |
| Estimated Credits | `sum(jobs[].cost_credits)` | 未入力なら `not estimated` |
| Render Outputs | `counts.render_outputs` | `0` |
| Cast Assets | `counts.generated_cast_files` | `17` |
| Approval Gates | `counts.blocked_gates` | `1 blocked` |

## UIコンポーネント

現在のUIはReactではなく、既存構成に合わせた静的HTML/CSS/JSで実装する。

ファイル:

```text
workspace/ui/live-workflow.html
workspace/ui/studio-lines.html
workspace/ui/assets.html
workspace/ui/cast-library.html
workspace/ui/jobs.html
workspace/ui/gates.html
workspace/ui/activity.html
workspace/ui/factory-futuristic.css
workspace/ui/factory-futuristic.js
workspace/ui/factory-pages.js
workspace/ui/server.py
```

論理コンポーネント:

- FuturisticShell
- TopCommandBar
- StatusPill
- MetricCard
- FactoryOverviewPanel
- SystemMonitorPanel
- MarketFeedPanel
- LiveFactoryFloor
- ProductionPipeline
- RecentOutputsStrip
- GenerationQueuePanel
- ActiveGenerationCard
- SystemPerformancePanel
- TerminalLogTape
- AssetLibraryPanel
- JobsPanel
- GatesPanel

## 個別ページ設計

サイドバーはアンカーではなく、以下の個別ページへ移動する。

| Page | File | 意図 | 実データ |
|---|---|---|---|
| Factory | `live-workflow.html` | 全体管制室 | `/api/factory-data` 全体 |
| Studio Lines | `studio-lines.html` | workflow工程と現在作業 | `generation-state.json.workflow[]` |
| Assets | `assets.html` | 素材棚、source captures、Blender lane | `asset-library.json`, `counts`, `blender` |
| Cast Library | `cast-library.html` | AI演者一覧と利用範囲 | `cast-manifest.json` |
| Jobs | `jobs.html` | Seedance clip job状態 | `generation-state.json.jobs[]` |
| Gates | `gates.html` | 権利・費用・承認・公開停止 | `generation-state.json.gates[]` |
| Activity | `activity.html` | Codex inbox、activity、更新ファイル | `codex-inbox.jsonl`, `activity[]`, `files.recent` |

各ページは「このページの意図」「読んでいる実データ」「次に判断すること」を上部に出す。

## Live Factory Floor 方針

中央パネルは、単なる文字看板ではなく「中でラインが動いている」見た目にする。

入れる要素:

- 奥行きのある工場フロア
- conveyor lane
- floating video cards
- render core
- robot arm
- ceiling rig
- machine bay
- live monitor
- light beams
- scanline / subtle noise

`SEEDANCE THEATER` 文字は補助要素にする。主役は工場ライン。

## ライブラリ作り込み方針

素材ライブラリは本番運用の中核にする。

分類:

1. Generated Cast
   - ID
   - name
   - role
   - image
   - rights_status
   - use_scope
2. Source Captures
   - UIキャプチャ
   - Codex操作画面
   - 説明動画ソース
3. External References
   - URL
   - checked_at
   - extracted_pattern
   - use_scope
   - 素材コピー禁止
4. Blocked Records
   - active libraryに混ぜない素材
   - 固有名はUI上に出しすぎない
5. Outputs
   - 生成済みMP4 / 音声 / 字幕 / review状態

6. Blender / 3D Preview Lane
   - Blenderがある場合のみローカルで3D preview / render plate / GLB確認を行う
   - Blenderがない場合は `unavailable` と表示し、CSS/Three.js/Higgsfield 3D代替を検討する
   - `workspace/assets/3d/renders` の最新plateを中央の `LIVE FACTORY FLOOR` に投影する
   - `bash workspace/scripts/render-blender-demo.sh` でCodexからローカルBlenderレンダーを更新できる
   - 有料生成や外部API実行とは切り離す

本番用ライブラリに追加したい項目:

```json
{
  "id": "",
  "name": "",
  "type": "cast | source_capture | output | external_reference | blocked",
  "path": "",
  "thumbnail_path": "",
  "rights_status": "",
  "use_scope": "",
  "project_tags": [],
  "created_at": "",
  "review_status": "pending | approved | blocked",
  "notes": ""
}
```

## Codex送信ロジック

UIの「この内容をCodexに送信」は、直接Codex TUIへstdin注入しない。

実際の動き:

1. Browser button
2. `POST /api/send-to-codex`
3. `workspace/ui/state/codex-inbox.jsonl` に追記
4. サーバーターミナルへログ出力
5. `generation-state.json` のactivityへ追加
6. 人間またはCodexがそのログを見て次の状態更新を行う

## 配布パッケージ

作成:

```bash
bash workspace/scripts/package-local-factory.sh
```

出力:

```text
dist/seedance-local-factory-*.zip
```

デフォルトで含めないもの:

- `codex-inbox.jsonl`
- 外部参考スクリーンショット
- source refs画像
- 権利不明・ブロック済み素材の実ファイル

## レビューしてほしい論点

1. KPIは完全に実データだけに寄せるか、UI mock telemetryを別枠で残すか
2. 中央Factory FloorはCSS演出で十分か、生成画像を背景素材として使うか
3. ライブラリの分類は `cast / captures / outputs / references / blocked` で足りるか
4. Codex inboxを人間確認制にするか、許可時だけ自動処理に進めるか
5. `cost estimate active` の次に、Higgsfield MCP見積をどう保存するか
6. 本番配布ZIPにどの素材まで含めるか
7. X投稿用説明動画では、このUIをそのままキャプチャするか、HyperFramesで説明動画化するか

## 現在の安全状態

- Active stage: `cost_estimate`
- Seedance generation: 未実行
- ElevenLabs generation: 未実行
- Subtitle post edit: 未実行
- Publish: blocked
- Human approval: required
- External API: UIからは未実行
- Paid generation: not executed
