# WORKFLOW.md — このツールの全体フロー(裏側ロジック、1〜100)

このリポジトリは「アプリ」ではなく、Claude Code / Codex / Hermes / OpenCrewなどのエージェントが読んで従う**スキル定義+スクリプト集**。実行主体は常にエージェントで、ユーザーは自然言語のブリーフと各ゲートでの承認だけを行う。UI(`workspace/ui/*`)は人間が状態を覗くための補助画面であり、ロジックの本体ではない。このドキュメントはUIを一切扱わず、裏側のロジックだけを1から100まで書き下す。

## 1. 全体像

```
自然言語ブリーフ
   ↓
[ルーティング判定] 軽量パス or 重量パス
   ↓                              ↓
軽量パス(単発CM等)          重量パス(複数ショット/短編/物語)
   ↓                              ↓
[任意]Blenderプリビズ?         Blenderプリビズ(完全自動、必須)
   ↓                              ↓
参照画像を用意                Higgsfield MCP画像生成(絵コンテ)
   ↓                              ↓
Seedance image-to-video       承認ゲート:絵コンテ
                                   ↓
                              セリフ有無の確認
                                   ↓
                              Higgsfield MCP ElevenLabsナレーション
                                   ↓
                              Blender本アニメーション最終化
                                   ↓
                              Higgsfield Seedance image-to-video
   ↓                              ↓
承認ゲート:素材承認(両パス共通、コスト・ログイン・権利確認込み)
   ↓
Palmier Pro仕上げ(import_media → sync_audio → 字幕 → 色 → [upscale確認] → export_project)
   ↓
承認ゲート:最終書き出し前
   ↓
納品(delivery package)
```

認証が必要な窓口は実質2つだけ: **Higgsfieldログイン**(画像・音声・動画の生成すべてがここに依存)と**Palmier Proサインイン**(仕上げ工程)。個別サービスのAPIキー(OPENAI_API_KEY等)は重量パスでは使わない。

## 2. 登場するシステムと役割

| システム | 役割 | 接続方式 |
|---|---|---|
| エージェント(Claude Code / Codex / Hermes / OpenCrew) | 全工程のオーケストレーター。ブリーフ解釈、プロンプト作成、スクリプト実行、承認確認 | ローカルシェル + MCP |
| Blender | 3Dプレビズ・最終アニメーションのローカルレンダー | `blender --background --python <script>`(ローカル、課金なし) |
| Higgsfield MCP | 画像生成(絵コンテ)・ElevenLabs音声生成・Seedance動画生成 | ホスト側が提供するMCPツール。このリポジトリのシェルスクリプトはMCPリクエストJSONを準備するだけで、実行はホストのMCPツールが行う |
| Palmier Pro | 動画編集の仕上げ(字幕・色・アップスケール・書き出し) | `mcp__palmier-pro__*` ツール群をエージェントが直接呼ぶ |
| note | ブログ/記事の下書き(このツールの外側の話) | 手動のみ。公開ボタンは絶対に押さない |

## 3. 認証・課金の窓口

- **Higgsfieldログイン**: `workspace/scripts/open-higgsfield-login.sh` でHermes Chromeを開き、ユーザーが手動でログインする。認証情報の自動入力・保存は一切しない。ログイン状態は`workspace/scripts/higgsfield-status.sh`がMCPリクエストとして準備し、ホストのHiggsfield MCPツールで実際に確認する。
- **Palmier Proサインイン**: Palmier Proアプリ側でユーザーが事前にサインイン/契約している前提。`mcp__palmier-pro__get_timeline`の`canGenerate`が`false`ならここで止まる。
- **APIキー**: 重量パスでは一切使わない。軽量パス(既存の単発CM運用)では`workspace/scripts/gpt-image-reference.sh`が`OPENAI_API_KEY`を使うことがあるが、これは環境変数としてそのセッションのみ設定し、リポジトリやログには絶対に書かない。

## 4. 入口: ブリーフのロック(共通)

どちらのパスに進むかを決める前に、必ず以下を確定させる:

- `video_use_case`(commercial / social-post / product-demo / app-walkthrough / explainer / event-teaser / portfolio / background-loop / story-scene)
- プロジェクト/商品/サービス名、読み方
- ターゲット視聴者、掲載先
- アスペクト比、尺、本数
- 音声ポリシー(ナレーションあり/なし、BGM)、テキストポリシー
- 予算上限、最大ジョブ数、最大リトライ回数
- 参照素材(画像/動画/ロゴ/ブランド資料)の有無と権利状況
- 複数ショット/物語進行があるか(§5のルーティング判定に使う)

## 5. ルーティング判定: 軽量パス vs 重量パス

判定基準(どちらか一つでも当てはまれば重量パス):

- 複数ショットにわたって同じキャラクター/商品/空間が再登場する
- 起承転結など物語進行がある(短編映画、複数カットのCM)

迷う場合はユーザーに一言確認する。判定結果は会話でそのまま確定してよく、UI操作は不要。

## 6. 軽量パス: フルフロー

単発CM・素材差し替えだけで足りる案件。詳細は`references/seedance-cm-workflow.md`と`references/image-to-video-handoff.md`。

1. **Blender使用確認(新規)**: `command -v blender`でBlenderが使える場合、参照画像を用意する前に一度確認する:「Blenderを使うとこのクオリティが出ます。使用しますか?」
   - **YES**: 重量パス§7-2と同じ手法(エージェントがブリーフからbpyスクリプトを新規に書き、`blender --background --python`で無人実行、`workspace/blender/action_movie_previs.py`を土台にする)でBlenderプリビズを1枚レンダーし、そのレンダーをこの案件の参照画像として使う(下記2に進む)。
   - **NO(デフォルト)/Blender未インストール**: 従来通り、ユーザー提供素材を優先し、なければ`workspace/scripts/gpt-image-reference.sh`で生成する。
   - どちらの場合も、参照画像の承認は既存のG2(参照素材承認)ゲートで扱う。専用の新規ゲートは作らない。
2. 参照画像を`workspace/assets/`に保存する(1で確定したもの: Blenderレンダー、ユーザー提供素材、またはGPT Image生成のいずれか)。
3. アスペクト比ごとにSeedanceプロンプトを1本ずつ書く(`workspace/prompts/`)。16:9のプロンプトを9:16にそのまま流用しない。
4. `bash workspace/scripts/higgsfield-status.sh` でアカウント/モデル状態のMCPリクエストを準備し、ホストのHiggsfield MCPツールで実行して結果を確認する。
5. `APPROVED=1 bash workspace/scripts/seedance-cost.sh` でコスト見積もりMCPリクエストを準備する(プロンプトに`pending`/`proposal`等のマーカーが残っていると`APPROVED=1`でもブロックされる)。
6. Higgsfield MCPでコスト見積もりを実行し、結果を`bash workspace/scripts/record-mcp-json.sh cost <response.json>`で記録する。
7. ユーザーが予算・プロンプト・参照素材・権利を最終承認する。
8. `APPROVED=1 bash workspace/scripts/seedance-generate.sh` で生成MCPリクエストを準備し、Higgsfield MCPで実行、`record-mcp-json.sh job <response.json>`で記録する。
9. 必要ならPalmier Proで仕上げ(§7-10と同じ手順)。
10. 出力・設定・権利注意事項を`workspace/delivery/`にまとめる。

## 7. 重量パス: フルフロー

詳細仕様は`references/end-to-end-movie-pipeline.md`。ここでは全体フローとして再掲する。

### 7-1. プロジェクト初期化

- プロジェクトID(英数字・ハイフン・アンダースコアのみ)とショットID(`shot_01`のように固定幅)を決める。
- `workspace/projects/<project_id>/` 配下にブリーフと各ショットの成果物を格納する規約(§9参照)。

### 7-2. Blenderプリビズ(完全自動、課金なし)

- エージェントがブリーフから`bpy`スクリプトを新規に書く。土台は`workspace/blender/action_movie_previs.py`(手続き型プリミティブ+マテリアル+カメラキーフレーム、外部3Dアセット読み込みなし)。
- `command -v blender` で存在確認してから `blender --background --python workspace/blender/<project>_previs.py` を無人実行する。
- この `.blend` がプロジェクトの正。以降の全ショットはこのシーンから書き出し、キャラクター/商品/カメラの一貫性を担保する。

### 7-3. Higgsfield MCP画像生成(絵コンテ)

- `bash workspace/scripts/higgsfield-image.sh` でMCPリクエストを準備する。`IMAGE_FILE`にBlenderレンダーpngを渡せるかはHiggsfield MCP側次第(img2img対応は接続環境で要確認、未検証)。
- `APPROVED=1`が必須。プロンプトファイルに`pending`等のマーカーが残っている限りブロックされる(`approval_gate`関数)。
- ホストのHiggsfield MCPツールで実行し、`bash workspace/scripts/record-mcp-json.sh image <response.json>`で結果を記録する。

### 7-4. 承認ゲート1: 絵コンテ承認

- ここで止まる。絵コンテの内容・構図・色調をユーザーが確認し、明示的にOKを出すまで次に進まない。低コストな段階で修正を吸収する。

### 7-5. セリフ確認

- 「カメラ目線で喋るカットはありますか?」を自然言語で一度確認する。
- YES: リップシンクはこのパイプラインのどのツールも解決しないことを明示し、(a)顔アップを避ける演出、(b)専用リップシンクツールの検討、のどちらかを選ばせる。
- NO(デフォルト): ナレーション主体で進める。

### 7-6. Higgsfield MCP ElevenLabsナレーション

- `bash workspace/scripts/elevenlabs-narration.sh` でMCPリクエストを準備する(ナレーションテキストファイル、言語、ボイスID、出力先を指定)。
- `APPROVED=1`必須、pending markerチェックあり。
- ホストのHiggsfield MCPツールで実行し、`record-mcp-json.sh narration <response.json>`で記録する。
- 以降、映像の尺はこの音声に合わせる(音声が主、映像が従)。

### 7-7. Blender本アニメーション最終化

- 承認済みカットのみ、音声の尺に合わせてカメラ・フレーム範囲を確定し、`.blend`を更新する。

### 7-8. Higgsfield Seedance image-to-video

- Blenderの最終レンダーを参照画像として`workspace/scripts/seedance-cost.sh`→`seedance-generate.sh`に渡す。軽量パスと同じスクリプト・同じ承認手順(§6の3〜7と同一)。
- ショットごとに同じ`.blend`由来の参照画像を使うことで、複数ショット間の一貫性を保つ。

### 7-9. 承認ゲート2: 素材承認

- Seedance投入前に、コスト承認・Higgsfieldログイン/クレジット確認・参照画像・プロンプト・出力先を確認する。既存の軽量パスと同じ位置づけのゲート。

### 7-10. Palmier Proで最終仕上げ

エージェントが`mcp__palmier-pro__*`ツールを直接呼ぶ(シェルスクリプト経由ではない)。

1. `import_media`: Seedance出力とナレーション音声をPalmier Proプロジェクトに取り込む。
2. `sync_audio`: 音声とショットのタイミングを合わせる。
3. 字幕/テロップの配置(`add_captions`など)。
4. `apply_color`: 色調整。
5. `upscale_media`(必要な場合のみ): **課金対象の生成系ツールなので、呼ぶ前に必ず`list_models`でモデル仕様を提示し、対象クリップ・出力品質・費用発生をユーザーに自然言語で確認してから実行する。** Seedanceのような機械的な`APPROVED=1`ゲートはPalmier Pro MCPには存在しないため、これは運用ルールとして徹底する。
6. `export_project`: 最終書き出し。

### 7-11. 承認ゲート3: 最終書き出し前承認

- 書き出し前の最終確認。ここを通過するまで公開・納品扱いにしない。

## 8. 承認ゲート一覧(横断まとめ)

| # | ゲート名 | 内容 | 該当パス |
|---|---|---|---|
| G1 | 用途・コンセプト承認 | video_use_case、企画内容 | 両方 |
| G2 | 参照素材承認 | 参照画像/写真、権利状況 | 両方 |
| G3 | 絵コンテ承認 | Higgsfield MCP画像生成の結果 | 重量パスのみ |
| G4 | Higgsfieldログイン/クレジット確認 | MCP account_status | 両方 |
| G5 | プロンプト最終承認 | pending/proposalマーカー除去 | 両方(スクリプトの`approval_gate`が機械的にチェック) |
| G6 | コスト承認 | Seedance/画像/音声のコスト見積 | 両方 |
| G7 | 動画生成実行 | Seedance image-to-video | 両方 |
| G8 | Palmier Pro `upscale_media`承認 | モデル仕様+費用の事前提示 | 両方(使う場合のみ) |
| G9 | 最終書き出し前承認 | export_project前 | 両方 |
| G10 | 公開判断 | noteなどへの公開 | ツール外、常に手動 |

G5, G6, G7は`_common.sh`の`approval_gate`関数がコード上で機械的に強制する(`APPROVED=1`環境変数 + プロンプトファイル内のpending/proposal/do not run/not approvedマーカー検出)。それ以外は運用ルール(ドキュメント上のハードルール)としてエージェントが徹底する。

## 9. フォルダ/ファイル規約

### 軽量パス(既存、変更なし)

```text
workspace/assets/reference-image-v1.png
workspace/prompts/seedance-9x16-v1.txt
workspace/prompts/seedance-16x9-v1.txt
workspace/logs/*.json
workspace/outputs/final-cm-v1.mp4
```

単一プロジェクト前提の"-v1"命名。

### 重量パス(新規)

```text
workspace/projects/<project_id>/
  brief.md
  shots/
    <shot_id>/
      previs.blend
      previs.png
      storyboard.png
      narration.mp3
      seedance_prompt.txt
      seedance_output.mp4
      review.json
```

`<project_id>`は英数字・ハイフン・アンダースコアのみ。`<shot_id>`は`shot_01`のように固定幅。

## 10. ロギング・記録の仕組み

すべてのMCP実行結果は`workspace/scripts/record-mcp-json.sh <kind> <response.json>`でサニタイズ(APIキー/トークン/Cookie等を`[REDACTED]`化)した上で記録する。

| kind | 出力先 |
|---|---|
| account | `workspace/logs/account-status.json` |
| model | `workspace/logs/model-seedance_2_0.json` |
| cost | `workspace/logs/cost-estimate.json` |
| job | `workspace/logs/job-v1.json` + `workspace/logs/result-urls.md` |
| narration | `workspace/logs/narration-result.json` |
| image | `workspace/logs/image-result.json` |

MCPリクエスト自体(実行前のペイロード)は`workspace/mcp-requests/*.request.json`に保存される。これはホストのHiggsfield MCPツールに渡すためのリクエスト内容であり、実行結果ではない。

## 11. 権利ゲート

- ユーザー提供素材を優先。権利不明の場合は内部ドラフト扱いにし、最終公開物と区別する。
- 実在の人物・ブランド・キャラクターの模倣は権利確認なしに行わない。
- Blenderの手続き生成物(プリミティブ+マテリアル)は権利リスクが低い。外部GLB/OBJ/HDRIを使う場合のみ通常のRights Gateを適用する。
- ElevenLabsで実在人物の声を複製する場合は本人同意が必須。同意が取れない/不明な場合は既定ライブラリボイスを使う。
- 最終的な権利クリアランスの判断は必ず人間(ユーザー/クライアント)が行う。エージェントは判断を代行しない。

## 12. 予算・コストロック

- 有料生成(Higgsfield MCP: 画像/音声/動画、Palmier Pro: upscale_media)の前には必ずコスト見積もり/モデル仕様確認と、ユーザーの明示承認が要る。
- 予算が不明な場合は最小構成(ドラフト1本、1アスペクト比、音声なし、追加バリアントなし)で進める。
- 再生成は通常2回まで。3回目以降は予算・参照素材・プロンプトの見直しをユーザーに確認する。

## 13. セキュリティ方針

- APIキー・パスワード・Cookie・セッション・トークン・支払い情報は、ファイル・プロンプト・ログ・シェル履歴のどこにも保存しない。
- Higgsfieldログインが必要な場合は`workspace/scripts/open-higgsfield-login.sh`でHermes Chromeを開き、ユーザーが手動でログインする。自動入力はしない。
- ブラウザ自動化は常に専用の Hermes Chrome(`/Users/stork/Applications/Hermes Chrome.command`)のみを使う。通常のChromeプロファイルやSafariなど、サインイン済みの個人ブラウザは自動化しない。
- 最終手渡し前に`bash workspace/scripts/secret-scan.sh`でシークレット混入をチェックする。

## 14. 既知の制約・未検証事項

- Higgsfield MCPの画像生成モデルの実名(暫定`image2`)と、Blenderレンダーを入力画像として渡すimg2img相当の対応可否は未検証。Higgsfield MCPが接続された環境で最初に確認する。
- リップシンクは未解決。カメラ目線の会話カットは演出で回避するか、専用ツールを別途検討する。
- 音声と映像のタイミング合わせはPalmier Proの`sync_audio`と手動の速度調整に依存し、完全自動同期は保証しない。
- Blenderの自動生成シーンは手続き型プリミティブが中心。写実的な3Dアセットが必要な場合は別途モデリングが必要。
- Factory UI(`workspace/ui/*`)の役割・見た目を見直すかどうかは未決定(`CODEX.md`§5参照)。このドキュメントの対象外。

## 15. 関連ファイル索引

| 目的 | ファイル |
|---|---|
| 重量パスの詳細仕様 | `references/end-to-end-movie-pipeline.md` |
| 軽量パスの詳細仕様 | `references/seedance-cm-workflow.md`, `references/image-to-video-handoff.md` |
| Blenderプレビュー規約 | `references/blender-3d-preview-workflow.md` |
| 実装タスクと決定の経緯 | `CODEX.md` |
| 共通の運用ルール・ハードルール | `AGENTS.md`, `workspace/agent-guides/cross-agent-runbook.md` |
| スキル定義本体 | `SKILL.md` |
