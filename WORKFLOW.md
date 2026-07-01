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
[任意]Blenderプリビズ?         Blenderプリビズ(完全自動、構図の正)
   ↓                              ↓
構図抽出/visual-handoff      承認ゲート:構図/カメラ/配置レビュー(Blender、無料)
   ↓                              ↓
storyboard board作成         storyboard board作成
   ↓                              ↓
写実キービジュアル生成       Higgsfield MCP画像生成(写実storyboard/key visual)
   ↓                              ↓
承認ゲート:写実絵コンテ      承認ゲート:写実絵コンテ承認
   ↓                              ↓
Seedance image-to-video       セリフ有無の確認
                                   ↓
                              Higgsfield MCP ElevenLabsナレーション
                                   ↓
                              Blender本アニメーション最終化
                                   ↓
                              Higgsfield Seedance image-to-video
   ↓                              ↓
承認ゲート:素材承認(両パス共通、コスト・ログイン・権利確認込み)
   ↓
[任意・承認後]Palmier Pro BGM/SFX生成(mirelo-sfx video-to-audio / elevenlabs-music等)
   ↓
Palmier Pro仕上げ(import_media → sync_audio → 字幕 → 色 → [upscale確認] → export_project)
   ↓
承認ゲート:最終書き出し前
   ↓
納品(delivery package)
```

認証が必要な窓口は実質2つだけ: **Higgsfieldログイン**(画像・音声・動画の生成がここに依存)と**Palmier Proサインイン**(仕上げ工程 + BGM/SFX生成)。個別サービスのAPIキー(OPENAI_API_KEY等)は重量パスでは使わない。BGM/SFX生成だけは唯一「Higgsfieldに一本化」の例外で、Palmier Pro自身の生成ツールを使う(§2、理由は生成プラットフォームの節を参照)。

**絵コンテについて: Blenderレンダーは主参照ではない。** Blenderは構図・カメラ・位置関係の正(`composition_only`)で、Seedance入力不可。Seedanceの主画像は、Blender構図を元にGPT Image/Higgsfield画像生成で作った写実storyboard/key visual(`visual_truth`)だけ。リップCMで「Blenderレンダーをそのままstart_imageにしてテキストで肉付け」は実際に失敗済みなので、ここを省略しない。

## 2. 登場するシステムと役割

| システム | 役割 | 接続方式 |
|---|---|---|
| エージェント(Claude Code / Codex / Hermes / OpenCrew) | 全工程のオーケストレーター。ブリーフ解釈、プロンプト作成、スクリプト実行、承認確認 | ローカルシェル + MCP |
| Blender | 3Dプリビズ・最終アニメーションのローカルレンダー。**構図の正(composition truth)。Seedance入力不可** | `blender --background --python <script>`(ローカル、課金なし) |
| Higgsfield MCP | 写実storyboard/key visual生成、ElevenLabs音声生成、Seedance動画生成 | ホスト側が提供するMCPツール。このリポジトリのシェルスクリプトはMCPリクエストJSONを準備するだけで、実行はホストのMCPツールが行う |
| Palmier Pro | 動画編集の仕上げ(字幕・色・アップスケール・書き出し)+ **BGM/SFX生成**(`generate_audio`、唯一のHiggsfield一本化の例外) | `mcp__palmier-pro__*` ツール群をエージェントが直接呼ぶ |
| note | ブログ/記事の下書き(このツールの外側の話) | 手動のみ。公開ボタンは絶対に押さない |

## 3. 認証・課金の窓口

- **Higgsfieldログイン**: `workspace/scripts/open-higgsfield-login.sh` でHermes Chromeを開き、ユーザーが手動でログインする。認証情報の自動入力・保存は一切しない。ログイン状態は`workspace/scripts/higgsfield-status.sh`がMCPリクエストとして準備し、ホストのHiggsfield MCPツールで実際に確認する。
- **Palmier Proサインイン**: Palmier Proアプリ側でユーザーが事前にサインイン/契約している前提。`mcp__palmier-pro__get_timeline`の`canGenerate`が`false`ならここで止まる。仕上げ工程に加えて、`upscale_media`と`generate_audio`(BGM/SFX)もここでの課金対象。
- **APIキー**: 重量パスでは一切使わない。軽量パス(既存の単発CM運用)では`workspace/scripts/gpt-image-reference.sh`が`OPENAI_API_KEY`を使うことがあるが、これは環境変数としてそのセッションのみ設定し、リポジトリやログには絶対に書かない。

## 4. 入口: ブリーフのロック(共通)

どちらのパスに進むかを決める前に、必ず以下を確定させる:

- `video_use_case`(commercial / social-post / product-demo / app-walkthrough / explainer / event-teaser / portfolio / background-loop / story-scene)
- プロジェクト/商品/サービス名、読み方
- ターゲット視聴者、掲載先
- アスペクト比、尺、本数
- 音声ポリシー(ナレーションあり/なし、BGM)、テキストポリシー
- 予算上限、最大ジョブ数、最大リトライ回数
- 参照素材(画像/動画/ロゴ/ブランド資料)の有無と権利状況。まず`workspace/assets/brand/brand-manifest.json`(自社素材ライブラリ)を確認し、あれば最優先で使う
- 複数ショット/物語進行があるか(§5のルーティング判定に使う)

## 5. ルーティング判定: 軽量パス vs 重量パス

判定基準(どちらか一つでも当てはまれば重量パス):

- 複数ショットにわたって同じキャラクター/商品/空間が再登場する
- 起承転結など物語進行がある(短編映画、複数カットのCM)

迷う場合はユーザーに一言確認する。判定結果は会話でそのまま確定してよく、UI操作は不要。

## 6. 軽量パス: フルフロー

単発CM・素材差し替えだけで足りる案件。詳細は`references/seedance-cm-workflow.md`と`references/image-to-video-handoff.md`。

1. **Blender使用確認(新規)**: `command -v blender`でBlenderが使える場合、参照画像を用意する前に一度確認する:「Blenderを使うとこのクオリティが出ます。使用しますか?」
   - **YES**: 重量パス§7-2と同じ手法(エージェントがブリーフからbpyスクリプトを新規に書き、`blender --background --python`で無人実行、`workspace/blender/action_movie_previs.py`を土台にする)でBlenderプリビズを1枚レンダーする。この画像は構図参照専用で、Seedanceの`IMAGE_FILE`には使わない。
   - **NO(デフォルト)/Blender未インストール**: 従来通り、ユーザー提供素材を優先し、なければ`workspace/scripts/gpt-image-reference.sh`で生成する。
   - どちらの場合も、参照画像の承認は既存のG2(参照素材承認)ゲートで扱う。専用の新規ゲートは作らない。
2. 参照画像を`workspace/assets/`または`workspace/projects/<project_id>/shots/<shot_id>/`に保存する。Blenderを使った場合は`build-visual-handoff.py`で構図情報を抽出し、`build-storyboard-board.py`でスクショ型のstoryboard board/contact sheetを作る。写実のキービジュアルを作って承認してからSeedanceに渡す。
3. アスペクト比ごとにSeedanceプロンプトを1本ずつ書く(`workspace/prompts/`)。16:9のプロンプトを9:16にそのまま流用しない。
4. `bash workspace/scripts/higgsfield-status.sh` でアカウント/モデル状態のMCPリクエストを準備し、ホストのHiggsfield MCPツールで実行して結果を確認する。
5. `PERMISSION_MANIFEST=<permission.json> ASSET_MANIFEST=<approved-keyvisual.json> APPROVED={{SET_TO_1_ONLY_AFTER_GATE_CHECK}} bash workspace/scripts/seedance-cost.sh` でコスト見積もりMCPリクエストを準備する。`APPROVED=1`単独では通らない。
6. Higgsfield MCPでコスト見積もりを実行し、結果を`bash workspace/scripts/record-mcp-json.sh cost <response.json>`で記録する。
7. ユーザーが予算・プロンプト・参照素材・権利を最終承認する。
8. `PERMISSION_MANIFEST=<permission.json> ASSET_MANIFEST=<approved-keyvisual.json> APPROVED={{SET_TO_1_ONLY_AFTER_GATE_CHECK}} bash workspace/scripts/seedance-generate.sh` で生成MCPリクエストを準備し、Higgsfield MCPで実行、`record-mcp-json.sh job <response.json>`で記録する。生成実行は別承認。
9. 必要ならBGM/SFX生成(§7-9bと同じ手順)とPalmier Proで仕上げ(§7-10と同じ手順)。
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

### 7-3. 絵コンテ = Blenderレンダー(構図参照、無料)

- **写実キービジュアルのプロンプトを書く前に、必ず`references/cm-creative-craft-knowledge.md`(構成・ショット文法・光と色の型・プロンプト語彙)を読む。** 「なんとなく」で書くと出力がガチャ化する(実際に起きた問題)。
- **7-2のBlenderレンダーは絵コンテであり、構図・カメラ・商品形状の正。** ただし高級CM・写実CMでは、低ポリ/ブロックアウトのBlender画像をSeedanceの`start_image`に直接渡さない。直接渡すと「肉付け」ではなく、生のBlender感を引きずる。
- Seedanceへ渡す主画像は、Blender絵コンテを元に作った写実キービジュアルにする。Blenderレンダーはその写実化の入力・比較対象・承認用の設計図として残す。
- 個別promptだけではなく、必ずstoryboard board/contact sheetを作る。上段にhero/mood、下段に6-8 panels、各panelにtime/role/source/Seedance useを表示する。これが人間のレビュー面になる。
- `workspace/scripts/higgsfield-image.sh`(Higgsfield MCP画像生成)は、この写実キービジュアル生成に使ってよい。使う場合も、生成絵コンテだけを根拠に次に進まず、Blender設計図と並べて「構図は守れているか」を確認する。
- 写実キービジュアル生成をスキップしてよいのは、Seedanceへ進まない構図レビュー段階だけ。Seedanceへ進む場合は、承認済み`storyboard.png`/key visualが必須。

### 7-4. 承認ゲート1: 絵コンテ承認

- ここで止まる。**Blenderレンダー(無料)をそのままユーザーに見せて**、構図・配置・一貫性を確認し、明示的にOKを出すまで次に進まない。低コストな段階で修正を吸収する。Higgsfield画像生成を使った場合はそれも並べて見せてよいが、承認の根拠はBlenderレンダー側にする。

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

- **生成前に必須: `references/known-failure-patterns.md`の全エントリと`references/cm-creative-craft-knowledge.md`(構成・ライティング・カメラワークの型)を読み、今回のプロンプト・参照画像が既知の失敗パターンを踏んでいないか、良い型に沿っているかを確認する。** 確認したことを案件のcondition md(または`review.json`)に一行残す。これは機械的なゲートではなく運用ルールなので、エージェントが毎回自分で確認する。
- 承認済みの写実キービジュアルを参照画像として`workspace/scripts/seedance-cost.sh`→`seedance-generate.sh`に渡す。軽量パスと同じスクリプト・同じ承認手順(§6の3〜7と同一)。
- ショットごとに同じ`.blend`由来の参照画像を使うことで、複数ショット間の一貫性を保つ。
- **プロンプトは「肉付け」方針で書く**: Blenderの構図・配置・カメラを守り、写実キービジュアルの質感・光・素材感を起点に、映画的な動きを足す。低品質なBlender画像をテキストだけで高級CMへ変換できると期待しない。
- **光・空気感は撮影用語で書く。図形的な名詞(ring/particle/line/dot)を数えられるモノとして描写しない**(FP-003)。bokeh、volumetric haze、soft glints、lens flareなど写真的な語彙を使う。
- **複数の参照素材(商品/人物/構図違い)がある場合、1枚に事前合成しない。まずツール本来のAPI/CLIが複数画像入力に対応していないか確認する**(FP-004)。対応していれば、複数画像をそのまま渡し、プロンプトで各画像の役割(index/role)を明記する。`gpt-image-reference.sh`は複数`--image`対応が必要(§6タスク12参照)。Higgsfield MCPのSeedanceが`start_image`/`end_image`や複数参照に対応しているかも、`higgsfield-status.sh`のmodel_get相当で確認してから前提を決める。

### 7-9. 承認ゲート2: 素材承認

- Seedance投入前に、コスト承認・Higgsfieldログイン/クレジット確認・参照画像・プロンプト・出力先を確認する。既存の軽量パスと同じ位置づけのゲート。

### 7-9b. Palmier ProでBGM/SFX生成(任意)

**唯一の例外: BGM/SFXだけはHiggsfield MCPではなくPalmier Pro自身の生成ツールを使う。** Higgsfield MCPが音楽/SFX生成モデルを持っているかは未確認(前例なし)だが、Palmier Proはこのセッションで`list_models(type=audio)`により実在を確認済み。エージェントが`mcp__palmier-pro__*`ツールを直接呼ぶ(シェルスクリプト経由ではない)。

- ユーザーがBGM/SFXを希望する場合のみ実施。希望しない場合はスキップして7-10に進む。
- **SFX**: `mirelo-sfx-v1.5-video-to-audio`(入力が`video`)に、確定したSeedance出力動画をそのまま渡す。テキストでタイミング指定する必要はなく、モデルが映像を見て適切な効果音のタイミング・種類を判断する。
- **BGM**: `elevenlabs-music`(`durations: [15,30,60,90,120,180]`など尺指定に対応)や`lyria3-pro`/`minimax-music-v2.6`で、ブリーフの雰囲気(トーン、テンポ感)をテキストで指定し、動画の合計尺に合わせて生成する。
- **承認: `upscale_media`と同じ運用ルールを適用する。** 呼ぶ前に必ず`list_models`で対象モデルの仕様を提示し、費用発生をユーザーに自然言語で確認してから実行する(Palmier Pro MCPには`APPROVED=1`のような機械的ゲートが存在しないため)。

### 7-10. Palmier Proで最終仕上げ

エージェントが`mcp__palmier-pro__*`ツールを直接呼ぶ(シェルスクリプト経由ではない)。

1. `import_media`: Seedance出力、ナレーション音声、(7-9bで生成した場合)BGM/SFXをPalmier Proプロジェクトに取り込む。
2. `sync_audio`: ナレーション・BGM・SFXとショットのタイミングを合わせる。
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
| G3 | 絵コンテ承認 | **Blenderレンダー**(主参照、無料)。Higgsfield画像生成は使う場合のみ補助として並べる | 重量パスのみ |
| G4 | Higgsfieldログイン/クレジット確認 | MCP account_status | 両方 |
| G5 | プロンプト最終承認 | pending/proposalマーカー除去 | 両方(スクリプトの`approval_gate`が機械的にチェック) |
| G6 | コスト承認 | Seedance/画像/音声のコスト見積 | 両方 |
| G7 | 動画生成実行 | Seedance image-to-video | 両方 |
| G8 | Palmier Pro生成系承認(`upscale_media` / `generate_audio`のBGM・SFX) | モデル仕様+費用の事前提示 | 両方(使う場合のみ) |
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

### 保存・pushポリシー(標準運用)

**プロジェクトの過程で生成された素材(Blenderレンダー、`.blend`、参照画像、絵コンテ、ドラフトプロンプト等)は、都度その都度、該当するフォルダ(上記の軽量パス/重量パスの規約、または`workspace/assets/cast/`)に保存し、コミット・pushする。** ローカルに置きっぱなしにして失われる状態を作らない。実例: `workspace/assets/3d/renders/`と`workspace/blender/*.py`、`workspace/prompts/<project>/`は生成のたびに追加・push対象。

**例外: `workspace/assets/brand/`配下の画像/動画ファイル(自社ブランド素材)だけは、ユーザーの明示的なセキュリティ判断によりローカルのみで、pushしない。** マニフェスト(`.json`)とREADMEはpush対象だが、実体ファイルは`.gitignore`で除外したまま変更しない。

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

- **自社所有素材(`workspace/assets/brand/`、`rights_status: company_owned`)を最優先で使う。** 第三者権利の懸念が一切ない。ローカルのみで管理し、外部クラウドDBには接続しない(セキュリティ方針)。
- 自社素材がない場合はユーザー提供素材を優先。権利不明の場合は内部ドラフト扱いにし、最終公開物と区別する。
- 実在の人物・ブランド・キャラクターの模倣は権利確認なしに行わない。
- Blenderの手続き生成物(プリミティブ+マテリアル)は権利リスクが低い。外部GLB/OBJ/HDRIを使う場合のみ通常のRights Gateを適用する。
- ElevenLabsで実在人物の声を複製する場合は本人同意が必須。同意が取れない/不明な場合は既定ライブラリボイスを使う。
- 最終的な権利クリアランスの判断は必ず人間(ユーザー/クライアント)が行う。エージェントは判断を代行しない。

## 12. 予算・コストロック

- 有料生成(Higgsfield MCP: 画像/音声/動画、Palmier Pro: upscale_media、generate_audioによるBGM/SFX)の前には必ずコスト見積もり/モデル仕様確認と、ユーザーの明示承認が要る。
- 予算が不明な場合は最小構成(ドラフト1本、1アスペクト比、音声なし、追加バリアントなし)で進める。
- 再生成は通常2回まで。3回目以降は予算・参照素材・プロンプトの見直しをユーザーに確認する。

## 13. セキュリティ方針

- APIキー・パスワード・Cookie・セッション・トークン・支払い情報は、ファイル・プロンプト・ログ・シェル履歴のどこにも保存しない。
- Higgsfieldログインが必要な場合は`workspace/scripts/open-higgsfield-login.sh`でHermes Chromeを開き、ユーザーが手動でログインする。自動入力はしない。
- ブラウザ自動化は常に専用の Hermes Chrome(`/Users/stork/Applications/Hermes Chrome.command`)のみを使う。通常のChromeプロファイルやSafariなど、サインイン済みの個人ブラウザは自動化しない。
- 最終手渡し前に`bash workspace/scripts/secret-scan.sh`でシークレット混入をチェックする。

## 14. 既知の制約・未検証事項

- Higgsfield MCPの画像生成モデル実名(暫定`image2`)とimg2img対応可否は未検証。Blenderを使う案件では写実storyboard/key visual生成が必須なので、接続環境で最初にモデル名と入力画像対応を確認する。
- **検証済み・失敗: 「Blenderレンダーをそのまま`start_image`にして、テキストプロンプトの『肉付け』指示だけで写実化する」は実際に試して失敗した**(リップスティックCM、2026-07-01、270 credits消費)。低ポリ感が残り、図形的な光表現(`ring`/`particle`)が2Dグラフィックとして描画された。正しくは、写実キービジュアルを別途生成(GPT Image edit mode等)し、承認してからSeedanceに渡す。詳細は`references/known-failure-patterns.md`(FP-001〜003)。
- **`gpt-image-reference.sh`と`seedance-cost.sh`/`seedance-generate.sh`は参照画像を1枚しか渡せない設計になっている。** しかしGPT Imageの実CLIは複数`--image`(役割付き)に対応済み(FP-004)。Higgsfield MCP側のSeedanceが`start_image`/`end_image`や複数参照に対応しているかは未確認。スクリプト側が複数画像に未対応だったため、これまで参照素材を1枚に事前合成する不自然な運用をしていた(FP-002の一因)。§6タスク12で修正予定。
- Palmier Proの`mirelo-sfx-v1.5-video-to-audio`(動画からSFX生成)は`list_models`で存在を確認しただけで、実際に動画を渡して満足のいく効果音が返るかは未検証。`elevenlabs-music`等のBGM尺指定(`durations`)も同様に未実行。最初の1回は試し生成で品質を見る前提とする。
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
| Blender直渡し禁止・写実storyboard必須の共通ロジック | `workspace/agent-guides/generic-video-generation-logic.md` |
| 自社素材ライブラリ(ローカルのみ、Supabase等クラウドDB非接続) | `workspace/assets/brand/README.md` |
| 失敗パターンの蓄積台帳(生成前に必ず確認、§7-8) | `references/known-failure-patterns.md` |
| 実装タスクと決定の経緯 | `CODEX.md` |
| 共通の運用ルール・ハードルール | `AGENTS.md`, `workspace/agent-guides/cross-agent-runbook.md` |
| スキル定義本体 | `SKILL.md` |
