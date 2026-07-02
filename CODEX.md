# v1凍結 / workspace/ 経路の有料生成禁止

This repository is entering the Studio v2 implementation track described in `PLAN.md`.
The existing v1 `workspace/` generation paths are frozen for new paid execution.
Do not run Higgsfield, Seedance, Palmier, ElevenLabs, upscale, export, publishing, or external-posting actions through v1.
Treat `workspace/`, `references/`, and `tests/fixtures/` as preserved legacy evidence unless a task explicitly says to add a non-destructive notice or new v2-compatible file.

# Codex Instructions — End-to-End Movie Pipeline 改訂設計書

Follow `AGENTS.md` and `workspace/agent-guides/cross-agent-runbook.md`.

**セッション引き継ぎ(2026-07-01、Claude Codeのセッション終了間際に作成): まず `workspace/agent-guides/claude-to-codex-handoff-20260701.md` を読むこと。** このセッションで見つけた実バグ(FP-007/FP-008等)、Palmier Pro経由でSeedanceが呼べる可能性がある発見、次にやるべき手順が凝縮されている。

## Codex側で /goal を実行する場合の投入文(2026-07-01、Claude Codeが用意)

ユーザーがCodex側のセッションで`/goal`を回す際は、以下をそのまま貼り付けること。

```
/goal

CODEX.md タスク11を実行してください(lipstick-cm-30s のリトライ)。

git pull してから CODEX.md を読んでください。Claude Code が今回のセッションで
FP-007(visual-handoff.json が空のプロンプト雛形を指していたバグ)と FP-008
(270credits失敗した回のプロンプト・条件ファイルが final/ という名前で撤回明記なし
に残っていたバグ)を見つけて修正済みです。permission manifest
(workspace/run/lipstick-cm-30s.permission.json)も作成済みです。

手順(CODEX.md タスク11に詳細あり):
1. references/known-failure-patterns.md(FP-001〜008)と
   references/cm-creative-craft-knowledge.md を読む
2. workspace/prompts/lipstick-cm/keyvisuals/final/*.prompt.txt の4プロンプトを
   Higgsfield MCP経由で実行し、workspace/assets/references/lipstick-cm/keyvisuals/
   に保存
3. 生成した4枚をBlenderパネルと並べて私に見せて、承認を待つ(この承認を得るまで
   次のSeedance見積もり・生成は一切行わない)
4. 承認後、asset-manifest.json / storyboard-review.json / visual-handoff.json の
   approval_status を approved に、seedance_input_allowed を true に更新。
   併せて workspace/run/lipstick-cm-30s.permission.json の
   prepare_seedance_cost_request / prepare_seedance_generation_request も true に
   更新すること(両方揃わないとseedance-cost.shがブロックされる)
5. 承認済みキービジュアルで Seedance コスト見積もり→生成
6. 結果を known-failure-patterns.md に記録(成功でも失敗でも)

limitが近づいたら都度pushして、CODEX.mdに進捗を追記しながら進めてください。
```

## Current Canonical Override (2026-07-01)

このリポジトリの現在の正は、`CLAUDE.md`の **Blender-To-Storyboard Safety Rewrite** と、`references/known-failure-patterns.md` FP-001/FP-005、`workspace/scripts/validate-seedance-input.py` の機械的ゲートである。

- Blender previs/render は `composition_only`。構図・カメラ・配置・スケールの正であり、Seedanceの`IMAGE_FILE`/`start_image`/`end_image`には使わない。
- Seedanceへ渡せる主画像は、承認済みの `photoreal_key_visual` / `approved_storyboard_frame` / `rights_confirmed_user_asset` / `approved_product_reference` だけ。
- BlenderからSeedanceへ進む場合は、Blender previs -> visual handoff -> GPT Image/Higgsfield写実storyboard/key visual -> 人間承認 -> Seedance、の順番を省略しない。
- このファイル内の旧記述で「Blenderレンダーが主参照」「Higgsfield画像生成は任意」「生成絵コンテは補助参照」と読める箇所は、リップCMの実失敗により撤回済み。現在は安全ゲート側を正とする。
- 2026-07-01: `references/cm-creative-craft-knowledge.md`(Phase 1〜3、構成/ショット文法/光と色/構図/プロンプト語彙/編集リズム/音響/プラットフォーム文法/用途別差分/プロンプト前チェックリスト)が完成した。**プロンプトを書く前に`known-failure-patterns.md`とセットで必ず参照すること。**

## 実装ステータス(2026-07-01時点)

- 2026-07-01: 旧方針コミット`7711779`のズレを修正済み。`workspace/scripts/elevenlabs-narration.sh`をHiggsfield MCP経由として復元し、`record-mcp-json.sh`の`narration`種別を復元し、`image`種別を追加し、`workspace/scripts/higgsfield-image.sh`を追加した。
- 2026-07-01: `references/end-to-end-movie-pipeline.md`は、画像生成(絵コンテ)・音声生成(ElevenLabsナレーション)・動画生成(Seedance)をすべてHiggsfield MCP経由にする方針へ更新済み。重量パスでは`gpt-image-reference.sh`を使わない。
- 未検証: Higgsfield MCPの画像生成モデル名とimg2img(参照画像入力)対応可否。接続環境で最初に確認する。
- §5のUI簡素化は未着手。ユーザーに「Factory UIの世界観を残すか、承認専用UIへ寄せるか」を確認してから行う。
- 2026-07-01: `WORKFLOW.md`(全体フローの1〜100言語化)を新規作成し、ユーザーとすり合わせ済み。承認ゲート粒度・フォルダ規約・Palmier Pro仕上げ順は確定。軽量パスへBlender previsを任意オプションとして追加する方針も反映済み。
- 2026-07-01: **BGM/SFX生成が抜けていたことが判明し、Palmier Pro経由で追加する方針が確定(§2b-d、§6タスク9、未着手)。** Higgsfield一本化の唯一の例外。`WORKFLOW.md`§7-9bに詳細。
- 2026-07-01: **撤回済みの旧方針:** Higgsfield画像生成(image2)を必須から任意に格下げし、Blenderレンダーを主参照にする案が一時的にあった。リップスティックCMで実際に270 creditsを使って失敗し、Blenderブロックアウト感が残ることが確認されたため、この案は破棄。現在は写実storyboard/key visual生成と承認が必須。
- 2026-07-01: **未確定・検討中: BGM/SFXをPalmier ProからHiggsfield(Seed Audio 1.0)経由に戻すか。** Higgsfield MCPの音声生成はSeed Audio 1.0とElevenLabs v3の両方を裏に持ち、Seed Audio 1.0は会話・SFX・BGMを1回でまとめて生成できることが判明(Web検索で確認、Higgsfield MCP自体では未検証)。実現すれば§2b-dのPalmier Pro例外を撤回し「生成は完全にHiggsfieldのみ」に戻せる。**ユーザーの最終GOはまだ得ていない。方針変更前に確認すること。**
- 2026-07-01: **対応済み: 自社ブランド素材ライブラリを新設した。** `workspace/assets/brand/`(logos/products/campaigns/guidelines + `brand-manifest.json`)。`workspace/assets/cast/`と同じマニフェスト方式。ローカルのみ、外部クラウドDB(Supabase等)には接続しない方針(ユーザーのセキュリティ判断)。画像/動画ファイルは`.gitignore`でデフォルト除外。`rights_status: "company_owned"`を新設し、Rights Gateで最優先の参照元として扱う(`WORKFLOW.md`§4/§11に反映済み)。
- 2026-07-01: **対応済み: 「生成物は都度assetsに保存してpushする」を標準運用ポリシーとして明文化した(`WORKFLOW.md`§9「保存・pushポリシー」)。** Blenderレンダー・`.blend`・参照画像・絵コンテ・ドラフトプロンプトは生成のたびにコミット・push対象。**唯一の例外は`workspace/assets/brand/`配下の実体ファイル**(マニフェスト/READMEはpush対象だがローカルのみの方針は変更なし)。
- 2026-07-01: **実運用での重要な学び: リップスティックCMで実際にSeedance生成(270 credits)を実行したところ失敗した。** 原因は、Blenderの低ポリレンダーをそのまま`start_image`に渡し、プロンプトの「flesh out」という指示だけで写実化を期待したこと(`workspace/projects/lipstick-cm-30s/postmortem-20260701-blender-fleshout-mismatch.md`)。**これにより「Blenderレンダー→テキストプロンプトだけでSeedanceに肉付けさせる」は不十分であることが実証された。正しくは、Blenderレンダーを土台にGPT Image(`gpt-image-reference.sh`のedit mode)等で写実的な「キービジュアル」を別途生成し、それを承認してからSeedanceの`start_image`にする、という中間ステップが必須。** §7-3/§7-8の「肉付け」記述はこの実運用知見を反映して更新済み。
- 2026-07-01: **対応済み: 失敗パターンを蓄積する`references/known-failure-patterns.md`を新設した(ユーザーの「フィードバックループ」要望への対応)。** Seedance/Blenderは再学習できない第三者モデルなので、ML的な再学習の代わりに「失敗の症状・原因・修正ルールをここに追記し、次の生成前に必ず読む」運用にした。現在FP-001(Blenderブロックアウトの直渡し)、FP-002(商品+人物の1枚合成)、FP-003(`ring`/`particle`等の図形語彙が2Dグラフィックとして描画される — 実際の失敗映像を目視して新規発見)、FP-004(複数画像対応スクリプトの未実装)、FP-005(UI/ドキュメントがBlenderを主素材扱いする文言)の5件を記録。`WORKFLOW.md`§7-8に、Seedance生成前にこのファイルを確認する運用ルールを追加した。今後の失敗はここに追記し続けること。
- 2026-07-01: **対応済み(P0、機械的強制): `workspace/scripts/validate-seedance-input.py`を新設し、`seedance-cost.sh`/`seedance-generate.sh`から自動で呼ばれるようにした。** FP-001(Blender直渡し)がもう「エージェントが覚えておくべき運用ルール」ではなく、コードレベルで強制ブロックされる。`workspace/schemas/`に3スキーマ(asset-manifest/visual-handoff/job-ledger)、`workspace/scripts/build-visual-handoff.py`・`prepare-storyboard-image-request.sh`、`workspace/prompts/templates/gpt-image-from-blender-previs.txt`を追加。5つのreferences docs全てをBlender=構図専用/写実キービジュアル必須の記述に修正済み(詳細は`CLAUDE.md`末尾のP0実装レポート参照)。dry-run/フィクスチャベースのテストのみ実行、Higgsfield MCP/Seedance/GPT Imageの実行は一切なし。**Codex側で確認が必要: Higgsfield MCPのSeedanceが`start_image`/`end_image`/複数参照に対応しているか(§6タスク12)、Higgsfield画像生成の実モデル名。** P1(学習フォルダの完全版)とUIの文言更新は今回スコープ外(理由と代替案はCLAUDE.md参照)。
- 2026-07-01: **次のアクション(最優先、§6タスク11): ユーザーがCodexにリップスティックCMのリトライを指示済み。** 失敗の根本原因を修正した4つのキービジュアルプロンプトが`workspace/prompts/lipstick-cm/keyvisuals/`に用意済み。Codexはこれをまず実行し、ユーザー承認を得てから初めて新しいSeedance生成に進むこと。**生のBlenderレンダーをstart_imageに戻さない。**
- 2026-07-01(Claude Codeが追加確認): `workspace/projects/lipstick-cm-30s/`の状態を棚卸しした。Codex側で`shots/<shot_id>/`(asset-manifest/visual-handoff/storyboard-review/learning-preflight)と`storyboard/`(00〜06の企画・承認ボード・`storyboard-board.html`)の骨組みは既に完成しており、`06-seedance-handoff-after-approval.md`のゲート条件も明確。**ただし4枚の写実キービジュアル画像そのものはまだ1枚も生成されていない**(`workspace/assets/references/lipstick-cm/keyvisuals/`ディレクトリ自体が存在しない。各shotの`storyboard-review.json`は`approval_status: "pending"`のまま、`storyboard-board.json`は`approval_status: "pending_photoreal_storyboard_approval"`のまま)。残っているのは**実行だけ**: `workspace/prompts/lipstick-cm/keyvisuals/final/*.prompt.txt`(最新版)を使って`gpt-image-reference.sh`または`higgsfield-image.sh`で4枚を実際に生成し、Blenderパネルと並べてユーザーに見せ、承認後に各shotの`asset-manifest.json`/`storyboard-review.json`を`approved`に更新してから初めてSeedance側に進むこと。生成前に`references/cm-creative-craft-knowledge.md`(特に§3光と色、§5プロンプト語彙、§10チェックリスト)にも目を通し、既存プロンプトが安定語彙(FP-003)に沿っているか最終確認すること。
- 2026-07-01(Codex追記): この環境ではHiggsfield MCP実行ツールが見えていないため、課金なしの準備まで実施。4枚の写実キービジュアル用request JSONを`workspace/mcp-requests/lipstick-cm-keyvisual-*-image2.request.json`へ用意し、Claude再投入用の`workspace/projects/lipstick-cm-30s/codex-to-claude-handoff-20260701.md`を追加した。画像生成・Seedance見積・Seedance生成・外部投稿は未実行。
- 2026-07-01(Codex追記): Palmier Pro MCPは接続確認済み。`get_timeline`は`canGenerate: true`、`list_models(type=image)`は`nano-banana-pro`/`gpt-image-2`等、`list_models(type=video)`は`seedance-2`/`seedance-2-fast`等を返した。つまりPalmier Pro経由で画像生成とSeedance生成へ進める可能性はある。ただしこれは「Higgsfield MCP一本化」方針からの実行経路変更で、課金も発生するため、ユーザーの明示承認なしには実行しない。
- 2026-07-01(Claude Codeが追加確認・軽微修正): `workspace/projects/macneo-pc-cm-15s/`(新規プロジェクト、Codexが今回のセッション中に追加)を確認した。コミット`96e553d`(16:9+音声ありへの切替)で`seedance-approval.md`の大部分は更新されたが、**`- Aspect ratio: 9:16`の1行だけ更新漏れになっており、同じファイル内の他の記述(プロンプトファイル名`seedance-15s-16x9.txt`、出力パス`-16x9.mp4`、承認文言そのものの「16:9」)と矛盾していた。** Claude Codeがこの1行を`16:9`に修正済み(実行系には触れていない、ドキュメントの整合性修正のみ)。他のフィールドは確認した限り一致している。次にこのプロジェクトを進める前に、`gates`(`cost_model_check`/`human_generation_approval`/`publication_rights`)が全て`blocked`のままであることを再確認し、コスト見積もり前にユーザーへ改めて確認すること。

このファイルは、Claude Codeとのディスカッションで固まった「自然言語の指示だけでCM・短編映画を作れるツール」の改訂設計書 兼 Codexへの実装記録。実際のコード状態と食い違いが出た場合は、このファイルの最新の確定方針(§2以降)を正としてコードを合わせること。全体フローの完成形は`WORKFLOW.md`を参照(このファイルは実装タスクと決定の経緯、`WORKFLOW.md`は完成後の姿)。

**確定方針(現在): 音声生成(ElevenLabsナレーション)・動画生成(Seedance)は全てHiggsfield MCP経由。APIキー(OPENAI_API_KEYを含む)は一切使わない。Blenderを使った案件では、画像生成(写実storyboard/key visual)と人間承認を挟む。Blenderレンダーは主参照ではなく構図参照。** Palmier Proは生成ではなく仕上げ工程(字幕・色・アップスケール・書き出し)専用、**ただしBGM/SFX生成(`generate_audio`)だけは唯一の例外としてPalmier Proを使う。** 軽量パスでもBlender previsを使った場合は同じく写実化を挟む。

## 0. ゴール

ユーザーがCLI(または最小限のチャットUI)に自然言語で指示するだけで、Blenderプリビズ → 絵コンテ → ナレーション/BGM/SFX → Seedance動画 → 字幕/仕上げ、まで一気通貫で回る。**ユーザーが外部ツール(Blender GUI、Higgsfield Web UI、Palmier Proの手動編集画面など)を直接操作する場面を最小化する。** 操作はすべてエージェント(Codex/Claude)がCLI/MCP経由で行い、ユーザーは自然言語での承認・判断のみ行う。生成系のログイン/認証はHiggsfield一本化で、個別のAPIキー管理はしない。

## 1. 現状(このセッションまでに実装済みのもの)

- `references/end-to-end-movie-pipeline.md`: 重量パス(11ステップ)の定義。Higgsfield MCP画像生成 + Higgsfield MCPナレーション + Higgsfield MCP Seedance + Palmier Pro仕上げの方針へ更新済み。
- `workspace/blender/action_movie_previs.py`: Blenderプリビズの雛形。プロジェクトごとにこれを土台に新規bpyスクリプトを書き、`blender --background --python` で無人実行する運用は既に確立済み。**変更不要。**
- `workspace/scripts/gpt-image-reference.sh`: `OPENAI_API_KEY`を使うGPT Image直接呼び出し。Codexが`edit --image`対応を追加済みだが、**重量パスでは使わない方針が確定(§2)。** 重量パスの絵コンテ生成は`higgsfield-image.sh`(新規)に置き換える。既存の軽量パス(単発CM)でこのスクリプトを使い続けるかは§7の未決事項。ファイル自体の削除はしない。
- `workspace/scripts/seedance-cost.sh` / `seedance-generate.sh`: Higgsfield MCP経由のSeedance動画生成リクエスト準備。**変更不要。**
- `workspace/scripts/higgsfield-image.sh`: Higgsfield MCP経由で画像生成(絵コンテ)リクエストを準備するスクリプト。モデル名・img2img対応可否はMCP接続環境で要確認。
- `workspace/scripts/elevenlabs-narration.sh`: 復元済み。Higgsfield MCP経由でElevenLabsナレーションのMCPリクエストを準備する。
- `workspace/scripts/record-mcp-json.sh`: `account|model|cost|job|narration|image` の6種別に更新済み。
- `workspace/ui/*`: 「工場/トレーディング端末」風の多パネルダッシュボード(Factory UI)。**§5でUI/UXの見直しを提案。**

## 2. 生成プラットフォームの最終確定

セッション中に2つの案を検討し、ユーザーが明示的に選んだ結論を記録する。

**検討した案:** Palmier Pro MCP(`mcp__palmier-pro__*`)を実際に呼んだところ、`get_timeline`で`canGenerate: true`(サインイン/契約済み)、`list_models(type=audio)`で`elevenlabs-tts-v3`(ElevenLabs v3 TTS、21ボイス)など複数の音声/BGM/SFXモデルが、Palmier Pro自身の`generate_audio`から直接使えることを確認した。これを使えばHiggsfieldへのログインなしでナレーションが作れる、という案だった。

**ユーザーの決定: この案は採用しない。** 画像生成・音声生成(ElevenLabs)・動画生成(Seedance)は全てHiggsfield MCP経由に統一し、APIキー管理(OPENAI_API_KEYも含む)を一切行わない、という方針が明示された。理由は認証/課金の窓口をHiggsfield一本に絞りたいため。Palmier Pro側の`generate_audio`等の生成系ツールは、この設計では**使わない**(仕上げ系ツール `sync_audio` / `add_captions` / `apply_color` / `upscale_media` / `export_project` のみ使う)。

この結果、認証が必要な窓口は実質**Higgsfieldログイン1つ**(+ Palmier Proの仕上げ用サインイン)に絞られる。§4で詳細。

## 2b. 監査で見つかった穴(リファクタリング対象)

### (a) Higgsfield MCP経由の画像生成スクリプトが存在しない

`workspace/scripts/gpt-image-reference.sh`は`OPENAI_API_KEY`前提であり、§2の決定(APIキー不使用)と矛盾する。重量パスでは使わず、Higgsfield MCP経由の画像生成リクエストを準備する `workspace/scripts/higgsfield-image.sh` を使う。

**実装済み: `workspace/scripts/higgsfield-image.sh`を新規作成した。** `seedance-cost.sh`と同じパターン(`write_mcp_request_with_prompt`でMCPリクエストJSONを`workspace/mcp-requests/`に準備し、ホスト側のHiggsfield MCPツールで実行、`record-mcp-json.sh`に`image`種別を追加して結果を記録)を踏襲する。

**未検証・要確認: Higgsfield MCP側の実際の画像生成モデル名(ユーザーは"image2"と呼んでいる)、および入力画像(Blenderレンダー)を渡せるimg2img相当の機能があるか。** 今回のセッションではHiggsfield MCPツール自体が接続されていないため確認できなかった。Higgsfield MCPが接続された環境(別PC側)で、`higgsfield-status.sh`と同じ要領で対象モデルのmodel_get相当のリクエストを準備し、実行結果を見てから`higgsfield-image.sh`のモデル名・パラメータを確定すること。

**方針転換(2026-07-01、§2c参照): この画像生成ステップは必須ではなく任意になった。** `higgsfield-image.sh`自体は削除しない(使いたい時のための補助ツールとして残す)が、パイプラインの必須経路ではなくなったため、上記の未検証事項はブロッカーではなくなった。

### (b) Palmier Proの仕上げ生成系(アップスケール等)に、Seedanceと同等の承認/予算ゲートがない

生成そのものはHiggsfield MCPに統一したが、Palmier Proの`upscale_media`は依然として課金対象の生成系ツールであり、`generate_audio`等は使わないとしても`upscale_media`は仕上げ工程で使う想定(§3ステップ10)。現行の設計は Higgsfield/Seedance側の`APPROVED=1`+コスト見積フローしか定義しておらず、**Palmier Pro側の`upscale_media`呼び出しには承認なしで課金が発生しうる抜け穴が残る。**

**修正: `upscale_media`を呼ぶ前に、(1)`list_models`で対象モデルの仕様を提示、(2)実行する内容を一度ユーザーに自然言語で確認、を必須ステップとして`end-to-end-movie-pipeline.md`に明記する。**

### (c) 複数ショット/複数プロジェクトを想定したフォルダ規約がない

現行の`workspace/assets/reference-image-v1.png`、`workspace/prompts/seedance-9x16-v1.txt`のような命名は「現在進行中のプロジェクトは1つだけ」という前提の単数形("-v1")規約。重量パスは1プロジェクトで複数ショット(previs、絵コンテ、ナレーション、Seedance出力)を扱うため、このままではショット間でファイルが上書きされる。

**修正: 重量パス専用に `workspace/projects/<project_id>/shots/<shot_id>/` 配下へ `previs.blend`、`storyboard.png`、`narration.mp3`、`seedance_prompt.txt`、`seedance_output.mp4` を格納する規約を`end-to-end-movie-pipeline.md`に追加する。** 軽量パス(既存の単発CM運用)は現行の"-v1"命名のままでよく、変更不要。

### (d) BGM/SFX生成が実装計画に一切なかった

ユーザーから指摘を受けて判明。CODEX.md §0のゴール文には「ナレーション/BGM/SFX」と書いてあったが、`references/end-to-end-movie-pipeline.md`の実際のステップにはBGM/SFXが一つも存在しなかった(ナレーションだけ実装され、BGM/SFXは検討すらされていなかった)。

**ユーザー決定: BGM/SFXは唯一の例外としてPalmier Pro自身の生成ツールを使う。** 理由:
- Higgsfield MCPが音楽/SFX生成モデルを持っているかは未確認・前例なし(ElevenLabsとは違い裏付けが一切ない)。
- Palmier Proの`mirelo-sfx-v1.5-video-to-audio`(入力`video`)、`elevenlabs-music`(`durations`で尺指定可)、`lyria3-pro`、`minimax-music-v2.6`は`list_models(type=audio)`で実在を確認済み。
- `mirelo-sfx-v1.5-video-to-audio`は動画を直接入力に取るため、「動画のどこが面白いか・間はどこか」を人間やエージェントが指定しなくても、モデルが映像を見て効果音のタイミングを判断できる。これがユーザーの「動画の間や面白いところを把握できるか」という懸念への直接の答えになっている。

**修正: `references/end-to-end-movie-pipeline.md`にステップ7-9bとして、Seedance動画確定後・Palmier Pro仕上げ前にBGM/SFX生成を追加する(`WORKFLOW.md`§7-9bが正)。** `upscale_media`と同じ運用ルール(`list_models`でモデル仕様提示→ユーザー確認→実行、機械的な`APPROVED=1`ゲートはない)を適用する。

## 2c. 撤回済み方針: Blenderを主参照にする案

一時期、「Blenderレンダーを主参照にして、Seedanceのプロンプトだけで写実的に肉付けする」案を検討した。

これはリップスティックCMで実際に失敗した。低ポリ/仮マテリアル/viewport lightingがSeedance出力に残り、高級CM品質にならなかった。

**現在の決定: この案は使わない。**

- Blenderは`composition_only`。構図・カメラ・配置・スケールの正。
- BlenderレンダーはSeedanceの`IMAGE_FILE`/`start_image`/`end_image`にしない。
- Higgsfield MCP画像生成またはGPT Image相当で、写実storyboard/key visualを作る。
- その写実画像をBlender構図と横並びでレビューし、人間承認を取る。
- 承認済みの`photoreal_key_visual`/`approved_storyboard_frame`だけがSeedance primary imageになれる。

`WORKFLOW.md`、`references/image-to-video-handoff.md`、`references/end-to-end-movie-pipeline.md`、`workspace/scripts/validate-seedance-input.py`を正とする。

## 3. 改訂後のパイプライン(Codexが`references/end-to-end-movie-pipeline.md`に反映すること)

```
[自然言語ブリーフ]
   ↓
[Blender previs] ローカル、完全自動、外部API不要。構図・カメラ・配置の正
   ↓
承認ゲート1: 構図承認(Blenderレンダーを見せる。無料)
   ↓
[Higgsfield MCP: 画像生成] Blender構図から写実storyboard/key visualを作る
   ↓
承認ゲート2: 写実storyboard/key visual承認
   ↓
[Higgsfield MCP: ElevenLabsナレーション] workspace/scripts/elevenlabs-narration.sh(既存のまま)
   ↓
[Blender 本アニメーション最終化] 音声尺に合わせてカメラ/フレーム範囲確定
   ↓
[Higgsfield MCP: Seedance image-to-video] 承認済み写実画像だけをprimary imageにする
   ↓
承認ゲート3: 素材承認(コスト承認・ログイン/クレジット確認を含む)
   ↓
[任意・承認後: Palmier Pro BGM/SFX生成] mirelo-sfx-v1.5-video-to-audio / elevenlabs-music等(唯一のHiggsfield一本化の例外、§2b-d)
   ↓
[Palmier Pro: import_media → sync_audio → add_captions → apply_color → upscale_media → export_project]
   ↓
承認ゲート4: 最終書き出し前承認
```

セリフ確認ステップ(カメラ目線で喋るカットの有無)は既存の位置(絵コンテ承認の直後)のまま変更なし。認証が必要な生成系の窓口はHiggsfieldMCPひとつに統一されている(BGM/SFXのみPalmier Pro例外)。

## 4. 「外部ツールのUIを一切触らない」監査結果

| 項目 | 状態 | 理由 |
|---|---|---|
| Blender操作 | ✅ ゼロタッチ | `--background`実行、GUI不要 |
| 画像生成(絵コンテ) | ✅ ゼロタッチ(Higgsfield MCP経由) | APIキー不要。認証はHiggsfieldログインに統合 |
| ナレーション(ElevenLabs) | ✅ ゼロタッチ(Higgsfield MCP経由) | 同上 |
| Seedance動画生成 | ✅ ゼロタッチ(Higgsfield MCP経由) | 同上 |
| 字幕(caption) / 色 / アップスケール / 書き出し | ✅ ゼロタッチ | Palmier Pro MCPを直接呼ぶ。中身の精度チェックは人間の「判断」であってUI操作ではない |
| Higgsfieldログイン | ⚠️ 手動ログインが前提 | 認証情報を自動入力しない方針のため(`AGENTS.md`/`HERMES.md`)。画像・音声・動画すべてがこの1つのログインに依存する。動画ごとではなくセッション/Cookie失効ごとに発生。**意図的な穴であり、セキュリティ上ゼロにすべきではない。** |
| Palmier Proのサインイン/契約状態 | ⚠️ 前提条件 | `canGenerate:false`の場合は仕上げ系ツールが失敗する。現在のセッションでは`true`を確認済みだが、セッション切れ時は再度ユーザーがPalmier Proアプリでサインインする必要がある |
| 最終公開判断・権利確認・実在音声の同意確認 | 🔒 意図的に人間判断のまま | ハードルールで自動化禁止。UIを「操作」するのではなく「判断」するステップなので穴として扱わない |

**結論: 動画1本を作るたびに発生しうるUI操作は「Higgsfieldログイン(セッション切れ時のみ)」だけまで削減できる。認証窓口がHiggsfield1つに統一されたことで、以前の案(Palmier Pro併用)よりむしろ管理対象が減った。**

## 5. UI/UX の見直し(workspace/ui/*)— ユーザー決定済み

**ユーザーの決定: 「工場/トレーディング端末」風の見た目・世界観(CSS/レイアウト)は維持する。簡素化しない。** 装飾パネル(MarketFeedPanel、SystemPerformancePanel、TerminalLogTape等)を削る提案は不採用。承認専用の地味な画面への置き換えも行わない。

一方で、UIが表示する**中身(パイプライン段階の語彙、ゲートの内容)**は、今回確定した`WORKFLOW.md`のロジックと食い違っていた(古いkeiba-AI TikTok劇場プロジェクト向けの`script`/`voice`/`subtitles`/`palmier`等のID/文言が残っていた)。これは見た目ではなくロジックの話なので修正が必要、という整理でユーザーと合意した。

**対応済み(Claude Codeが実施、コミット参照): `workspace/ui/factory-futuristic.js`のみを修正。CSS/HTMLレイアウトは一切変更していない。**

- `renderPipeline()`のfallback配列を、WORKFLOW.md §7(重量パス7-1〜7-11)の10段階(routing / blender_previs / storyboard_image / gate_storyboard / narration / blender_final / seedance_video / gate_asset / palmier_finish / gate_final)に更新。
- `workflowDetail()`に上記10段階のcase節を追加(既存の`script`/`cost`/`seedance`等の古いcase節は、他プロジェクトのローカルstateファイルとの後方互換のため残した)。
- 「安全ゲート」パネルに、`WORKFLOW.md`§8のG1〜G10のfallback配列を追加(`appState.state.gates`が空のときに表示される)。
- 既存のCSSクラス(`pipeline-node`、`gate-mini-card`等)をそのまま再利用しているため、見た目は変わらない。

**未着手:** `workspace/ui/state/generation-state.json`(gitignore対象、ローカルのみ)側の実際のプロジェクト運用時に、上記10段階のIDに沿ったworkflow[]・gates[]を書き込むのはエージェント側の運用ルールとして徹底する(`GENERATION_FACTORY_LOGIC.md`の既存方針通り、実データのみ)。

## 6. Codexへの実装タスクと状態

**0番台は、以前のCodex実装(コミット`7711779`、旧方針ベース)の巻き戻し。最優先で対応すること。**

0-a. **対応済み:** `workspace/scripts/elevenlabs-narration.sh`を復元した。git履歴のコミット`b940bd0`時点の内容(Higgsfield MCP経由、`write_mcp_request_with_prompt`パターン、`approval_gate`でpending markerチェック)を使用。
0-b. **対応済み:** `workspace/scripts/record-mcp-json.sh`の`narration`種別を復元した。`narration`の出力先は`$LOG_DIR/narration-result.json`。
0-c. **対応済み:** `workspace/scripts/gpt-image-reference.sh`は重量パスの絵コンテ生成として使わない。ファイル自体(`edit --image`対応含む)は残し、`end-to-end-movie-pipeline.md`のステップ3から参照を外した。

1. **対応済み:** `workspace/scripts/higgsfield-image.sh`を新規作成した(§2b-a)。`seedance-cost.sh`と同じ`write_mcp_request_with_prompt`パターンでHiggsfield MCP画像生成リクエストを準備する。モデル名・img2img対応可否は接続後に確認してから確定する。
2. **対応済み:** `workspace/scripts/record-mcp-json.sh`に`image`種別を追加した。現在は`account|model|cost|job|narration|image`の6種別。
3. **対応済み:** `references/end-to-end-movie-pipeline.md`のステップ3を「Higgsfield MCP画像生成(`higgsfield-image.sh`)」、ステップ6を「Higgsfield MCP経由の`elevenlabs-narration.sh`」に書き換えた。
4. **対応済み:** §2b(b): `upscale_media`呼び出し前に「モデル仕様提示 → ユーザー確認」を必須にするルールを`end-to-end-movie-pipeline.md`に追記した。
5. **対応済み:** §2b(c): 重量パス用に`workspace/projects/<project_id>/shots/<shot_id>/`のフォルダ規約を`end-to-end-movie-pipeline.md`に追記した。軽量パスの既存命名は変更しない。
6. **決定・対応済み(§5参照): UIの見た目は簡素化しない、そのまま維持する。** 代わりに`workspace/ui/factory-futuristic.js`のパイプライン/ゲート表示ロジックをWORKFLOW.mdの語彙に合わせて修正済み(Claude Code実施、CSS/HTML変更なし)。
7. **未着手:** §7の「軽量パスもHiggsfield画像生成に切り替えるか」は、ユーザーに確認してから着手する(このドキュメントの決定は重量パスのみに適用する)。
8. **対応済み: 軽量パスにBlender previsを任意オプションとして追加する。** `WORKFLOW.md`§6のステップ1を正とする。実装内容:
   - `references/seedance-cm-workflow.md`(Image-To-Video Route)と`SKILL.md`のImage-To-Video Route、`references/image-to-video-handoff.md`に、参照画像を用意する前段として次の分岐を追加する。
   - `command -v blender`でBlenderが使える場合のみ、ユーザーに一度尋ねる:「Blenderを使うとこのクオリティが出ます。使用しますか?」
   - YESの場合: 重量パス(`references/end-to-end-movie-pipeline.md`のBlenderプリビズ手順、`workspace/blender/action_movie_previs.py`が土台)と同じ手法でBlenderプリビズを1枚レンダーし、そのレンダーをこの案件の参照画像として使う。
   - NOの場合、またはBlender未インストールの場合: 従来通り(ユーザー提供素材優先 → なければ`gpt-image-reference.sh`)。
   - 新しい承認ゲートは作らない。参照画像の承認は既存のRights Gate/参照素材承認にそのまま乗せる。
   - この変更は軽量パスの既存"-v1"命名やスクリプト(`seedance-cost.sh`/`seedance-generate.sh`)には影響しない。参照画像の出所が増えるだけ。
9. **未着手・ユーザー確定済み: BGM/SFX生成をPalmier Pro経由で追加する。** `WORKFLOW.md`§7-9bを正とする。実装内容:
   - `references/end-to-end-movie-pipeline.md`に、承認ゲート2(素材承認)の後・Palmier Pro仕上げの前に新ステップとして追加する。
   - SFXは`mirelo-sfx-v1.5-video-to-audio`にSeedance出力動画を渡す(video-to-audio、テキストでのタイミング指定は不要)。
   - BGMは`elevenlabs-music`(`durations`で尺指定)/`lyria3-pro`/`minimax-music-v2.6`のいずれかを、ブリーフの雰囲気指定+動画合計尺に合わせて使う。
   - 実行前に`list_models`でモデル仕様を提示し、費用発生をユーザーに自然言語で確認する(`upscale_media`と同じ運用ルール、§2b-b/§8のG8)。
   - ユーザーがBGM/SFXを希望しない場合はスキップする(必須ステップではない)。
   - Palmier Proの`import_media`/`sync_audio`のステップ説明に、BGM/SFXも取り込み対象として追記する。
10. **未着手・ユーザー確定済み: Higgsfield画像生成(image2)を必須から任意に格下げする。** `WORKFLOW.md`§2c/§7-3/§7-4を正とする。実装内容:
    - `references/end-to-end-movie-pipeline.md`のステップ3(絵コンテ生成)を「Blenderレンダー(7-2)がそのまま絵コンテ・主参照。Higgsfield画像生成は任意の補助トーン確認」に書き換える。
    - 承認ゲート1(絵コンテ承認)は、Blenderレンダーを見せて行う形に書き換える(Higgsfield画像生成の結果を承認の根拠にしない)。
    - ステップ8(Seedance生成)のプロンプト方針に「肉付け」の考え方(構図・配置はBlenderレンダーのまま保持し、写実的な質感・光はテキスト指示で引き出す)を追記する。
    - `workspace/briefs/ascension-line-workflow-runbook.md`の原則(主素材/補助参照の区別、禁止事項)を参照元として明記する。
    - `higgsfield-image.sh`は削除しない(任意で使う補助ツールとして残す)。
    - **注記(2026-07-01時点で判明): この方針(Blenderレンダーを直接start_imageにしてテキストの「肉付け」指示に頼る)は、リップスティックCMで実際に試して失敗した。** タスク11(写実キービジュアル生成)を必ず経由すること。「肉付け」記述はSeedanceへの動き付け指示としては有効だが、写実化そのものはテキストだけでは達成できない。

11. **最優先・スキャフォールド完了/実行が唯一の残タスク: リップスティックCMのリトライ。** ユーザーがこの作業をCodexに依頼済み。Codex側で`workspace/projects/lipstick-cm-30s/shots/*/`と`storyboard/00〜06`の企画・承認ゲート定義は既に完成している(2026-07-01、Claude Codeが棚卸し確認済み)。**残っているのは4枚の写実キービジュアルを実際に生成することだけ。**

    **2026-07-01追加(Claude Codeが実プロジェクトで統合テスト済み、FP-007参照): `visual-handoff.json`の`storyboard_prompt_path`/`output.prompt_path`が、未記入のテンプレート雛形(`shots/<shot_id>/gpt-image-storyboard-prompt.txt`)を指していて、具体的な写実プロンプト(`workspace/prompts/lipstick-cm/keyvisuals/final/*.prompt.txt`)を指していなかったバグを発見・修正済み。** 4ショット全ての`visual-handoff.json`を、実際に書き込んだ`final/*.prompt.txt`を指すよう修正した。**`workspace/scripts/prepare-storyboard-image-request.sh`(schema駆動の推奨実行入口)を、コストの発生しないリクエスト準備のみのモードで2ショット分(clip_01_start, clip_02_lips)実際に実行し、正しいプロンプトが読み込まれることを確認済み。** また`validate-seedance-input.py`が現在の(未承認)状態を正しくブロックすることも再確認済み。**なお、`final/*.prompt.txt`には`Status: proposal`のようなテキストマーカーは意図的に入れていない**(プロンプト本文に余計な地の文が混ざらないようにするため)。ゲートは`APPROVED=1`環境変数+人間による目視承認+`asset-manifest.json`の`approval_status`更新の3点で行う(テキストマーカーの削除ではない)。

    手順:
    1. `references/known-failure-patterns.md`(FP-001〜007)と`references/cm-creative-craft-knowledge.md`(特に§3・§5・§10、2026-07-01完成)を読む。同じ失敗を絶対に繰り返さないこと。
    2. `workspace/run/lipstick-cm-30s.permission.json`は作成済み(2026-07-01、Claude Code、`prepare_image_generation_request: true`、`execute_image_generation`/`execute_paid_generation`はまだ`false`)。実際にHiggsfield MCPツールがある環境で以下を実行してリクエストを準備する:
       ```
       APPROVED=1 PERMISSION_MANIFEST=workspace/run/lipstick-cm-30s.permission.json \
       bash workspace/scripts/prepare-storyboard-image-request.sh \
         workspace/projects/lipstick-cm-30s/shots/clip_01_start/visual-handoff.json
       ```
       (他3ショットも同様。`workspace/mcp-requests/higgsfield-image.request.json`に準備される。1ショットずつ処理し、実行のたびに次のステップに進む前に上書きされる点に注意)
    3. host提供のHiggsfield MCP画像生成ツールで準備済みリクエストを実行し、結果を`workspace/assets/references/lipstick-cm/keyvisuals/<shot>_key.png`に保存、`bash workspace/scripts/record-mcp-json.sh image <response.json>`で結果を記録する。
    4. 生成した4枚を、元のBlenderパネル(`workspace/assets/3d/renders/lipstick_cm_panel_0{1,2,3,4}*.png`)と並べてユーザーに見せる。**この承認を得るまで、次のSeedance見積もり・生成は一切行わない。**
    5. 承認後、各shotの`asset-manifest.json`/`storyboard-review.json`/`visual-handoff.json`の`approval_status`を`approved`に、`seedance_input_allowed`を`true`に更新する(`storyboard/06-seedance-handoff-after-approval.md`のゲート条件を満たすこと)。**併せて`workspace/run/lipstick-cm-30s.permission.json`の`prepare_seedance_cost_request`/`prepare_seedance_generation_request`も`true`に更新すること(2026-07-01、Claude Codeがシミュレーション実行で確認: asset-manifest側を承認済みにしても、この2フラグが`false`のままだと`seedance-cost.sh`は独立してブロックされる。2箇所とも更新が必要)。** その上で承認済みキービジュアルを`start_image`/`end_image`として`seedance-cost.sh`→`seedance-generate.sh`に渡す。生のBlenderレンダーには絶対に戻さない(`validate-seedance-input.py`が機械的にブロックする)。
    6. コスト承認と生成承認は別物として扱う(`CLAUDE.md`のSafety/Cost Gate参照)。
    7. 結果が今回も失敗なら、`references/known-failure-patterns.md`に新しいFPエントリを追記してから次を試す。成功なら、そのこと自体も同ファイルか案件のcondition mdに記録する(何が効いたかも財産になる)。**この成功こそが、このプロジェクト全体で唯一の「パイプラインが実際にチューニングできている」ことの証明になる。**

    **2026-07-01追加(Claude Code、FP-008): `workspace/prompts/lipstick-cm/{clip_01_0-15s,clip_02_15-30s}_9x16_seedance_{draft,final}.txt`は実際に失敗した回そのもののプロンプトだったため、SUPERSEDEDと明記した(FP-001/002/003を同時に含んでいた)。`seedance-conditions.md`/`brief.md`/`workspace/briefs/lipstick-cm-30s-script.md`もこれらを「現在の条件」として引用していたため、冒頭にSUPERSEDEDバナーを追加した。実際のFP-002合成参照画像(`workspace/assets/references/lipstick-cm/clip_02_product_plus_rina_lips_clean.png`)にも警告ファイルを追加済み。今後、失敗した回の生成条件ファイル・プロンプトを新規に作る場合も、postmortemを書くだけでなく、そのファイル自身に撤回の旨を明記すること(`final`という名前だけでは「承認済み」を意味しない)。**

    **2026-07-01追加(Claude Code、Codexの`workspace/learning/`システムを確認): `workspace/scripts/pre-generation-learning-check.py`のFP-003自動チェック(`[" ring", " rings", "particle", "particles", "line overlay", "dots"]`)は良い方向性だが、語彙リストが狭く、`macneo-pc-cm-15s`の実際のプロンプトにあった"electric arcs"/"electric energy"を検知できなかった(Claude Codeが手動で発見・修正、上記参照)。改善提案: 固定語彙リストではなく、`references/known-failure-patterns.md` FP-003の原則(光・エネルギーを「数えられる図形」として描写しない)に照らしたより広いチェック、または少なくとも`arc`/`arcs`/`bolt`/`spark`/`beam`をリストに追加することを推奨する。また`workspace/learning/failure-candidates.md`の`FP-CANDIDATE-007`は、`references/known-failure-patterns.md`側で既に`FP-007`(visual-handoff.jsonのprompt_path問題)を使っているため、昇格(`references/known-failure-patterns.md`へ移動)する際は次の空き番号(`FP-009`以降)を使うこと。2つのファイルが別々にFP番号を採番しているため、昇格時の衝突に注意。**

    **2026-07-01追加(Claude Code、上記の疑問を訂正): 「Model target: Seedance 2 via Palmier MCP」は矛盾ではなく正しい可能性が高いことが判明した。** Claude Codeのこのセッションで`mcp__palmier-pro__generate_video`のツール定義を確認したところ、`referenceImageMediaRefs`/`referenceVideoMediaRefs`/`referenceAudioMediaRefs`パラメータの説明に明示的に**「Seedance only」**と書かれていた。つまりSeedanceは、独立した「Higgsfield MCP」経由ではなく、**Palmier ProのMCP接続(`generate_video`ツール、`model`にSeedance系IDを指定)経由で実際に呼び出せる**可能性が高い。これは§2の「Higgsfield一本化」方針そのものの見直しが必要になりうる重要な発見であり、単なるmacneoファイルの誤記ではなかった。
    **ただし未解決: 実際に`mcp__palmier-pro__get_timeline`と`list_models(type=video)`を呼んだところ、両方とも`"Editor not available"`エラーになった(Claude Codeが2026-07-01に確認)。** これはPalmier Proのデスクトップアプリ自体がこのセッションの接続先で起動・サインインされていないことを意味する(ツール自体は存在するが使えない状態)。Codex側でも同じ2つの呼び出しを試し、`"Editor not available"`になるか、実際に動くか(＝Codex環境ではPalmier Proアプリがサインイン済みか)を確認すること。もしCodex側でPalmier Proが使える状態なら、**Higgsfield MCPの代わりにPalmier Pro経由でSeedance/画像生成を実行できる可能性があり、Track Bの実行手段が広がる。** 動くモデル名(`list_models`の結果)を`known-failure-patterns.md`かこのファイルに記録すること。

12. **対応済み(部分): マルチモーダル/複数参照画像への未対応を修正した(`references/known-failure-patterns.md`FP-004)。** ユーザー指摘: 「素材が結局1個しか入ってなかったり、マルチモーダルが強みなはずなのに全然活用できてない」。実装内容:
    - **完了:** `workspace/scripts/gpt-image-reference.sh`を拡張し、`GPT_IMAGE_SOURCE_IMAGES`(改行区切り)で複数の`--image`を渡せるようにした(`image_gen.py`のCLIの複数`--image`フラグ対応、`references/cli.md`確認済み)。既存の単数`GPT_IMAGE_SOURCE_IMAGE`は後方互換で残した。
    - **完了:** `workspace/scripts/higgsfield-image.sh`も同様に拡張し、`HIGGSFIELD_IMAGE_SOURCE_IMAGES`(`path:role`形式、改行区切り)で複数画像+役割をMCPリクエストの`image_N`/`image_N_role`フィールドとして渡せるようにした。両方dry-runで動作確認済み(Claude Code、2026-07-01)。
    - **完了:** リップスティックCMのClip 2(唇キービジュアル)を、事前合成ではなく「商品キービジュアル(`clip_01_end_key.png`)+唇クロップの2枚を役割指定して渡す」方式に書き換えた(`workspace/prompts/lipstick-cm/keyvisuals/clip_02_lips_key.txt`)。
    - **未着手・Codex専用(Claude Codeはこの環境にHiggsfield MCPツールがないため実行不可)。具体的な確認手順:**
      1. Higgsfield MCPの account/model一覧ツール(host提供、`higgsfield-status.sh`が準備するリクエストと同じ要領)を実行し、画像生成モデルの実際の名前(ユーザーが"image2"と呼んでいるもの)と、そのモデルが単一/複数の参照画像入力(img2img)を受け付けるパラメータ名を確認する。
      2. Seedance側のモデル仕様(model_get相当)を確認し、`start_image`と`end_image`を別々に指定できるか、複数参照画像(3枚以上)を渡せるかを確認する。パラメータ名が`start_image`/`end_image`でない場合は実際の名前を記録する。
      3. 確認結果を`references/known-failure-patterns.md`か本ファイルに追記する(何がAPIとして存在し、何が存在しないかを記録すること自体が価値。存在しない場合も「未対応と確認済み」と明記する)。
      4. 対応していれば`seedance-cost.sh`/`seedance-generate.sh`に`END_IMAGE_FILE`等の追加パラメータを実装し、`workspace/scripts/higgsfield-image.sh`の`HIGGSFIELD_IMAGE_SOURCE_IMAGES`(§6タスク12で実装済み)と同じ`path:role`形式を踏襲する。
      5. この確認は**課金を伴わない参照/一覧系ツール呼び出しのみ**で完結するはずで、実際のSeedance生成やコスト確定を伴わない。もし一覧系ツールが存在せず確認に課金が発生する場合は、先にユーザーに確認してから進めること。

## 7. 未確定・ユーザー判断が必要な点

- **Higgsfield MCPの画像生成モデル名・img2img(参照画像入力)対応可否は未検証。** Higgsfield MCPが接続された環境で最初に確認すること。
- 既存の軽量パス(単発CM、`gpt-image-reference.sh`使用)も同じくHiggsfield MCP画像生成に切り替えるかは未決定。今回の「APIキー不使用」方針は重量パスの議論の中で決まったもので、軽量パスに自動適用はしていない。
- Factory UI(`workspace/ui/*`)の「工場/トレーディング端末」世界観を残すか、承認専用の地味なUIに寄せるかは製品方針次第。
- Palmier Proの`mirelo-sfx-v1.5-video-to-audio`と`elevenlabs-music`等は`list_models`で存在確認のみ。実際に動画/テキストを渡して満足のいく結果が返るかは未実行。初回は試し生成で品質を見る。

## 8. X投稿を参考にした動画作成について

ユーザーから特定のX投稿(`https://x.com/ehuanglu/status/2072073069875855422`)のような動画を作りたいという要望があった。`references/higgsfield-mcp-demo-patterns.md`に「X Reference Summary: Liquid-Metal Desk VFX」として分析済み(スタイル参照のみ、素材自体は再利用しない)。

この案件用に以下を既に用意済み:

- `workspace/assets/reference-liquid-metal-desk-v1.jpg`(ユーザー自身のデスク実写、権利クリア)
- `workspace/prompts/liquid-metal-desk-v1.txt`(Seedance image-to-videoプロンプト、`Status: proposal`のまま未承認)

この案件はSeedance image-to-videoの既存ルート(軽量パス寄り)を使う想定で、画像生成(絵コンテ)ステップは使っていない。§2の画像生成プラットフォーム決定とは独立している。承認・予算確定後に`higgsfield-status.sh` → `seedance-cost.sh`と進める。
