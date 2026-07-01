# Codex Instructions — End-to-End Movie Pipeline 改訂設計書

Follow `AGENTS.md` and `workspace/agent-guides/cross-agent-runbook.md`.

## 実装ステータス(2026-07-01時点)

- 2026-07-01: 旧方針コミット`7711779`のズレを修正済み。`workspace/scripts/elevenlabs-narration.sh`をHiggsfield MCP経由として復元し、`record-mcp-json.sh`の`narration`種別を復元し、`image`種別を追加し、`workspace/scripts/higgsfield-image.sh`を追加した。
- 2026-07-01: `references/end-to-end-movie-pipeline.md`は、画像生成(絵コンテ)・音声生成(ElevenLabsナレーション)・動画生成(Seedance)をすべてHiggsfield MCP経由にする方針へ更新済み。重量パスでは`gpt-image-reference.sh`を使わない。
- 未検証: Higgsfield MCPの画像生成モデル名とimg2img(参照画像入力)対応可否。接続環境で最初に確認する。
- §5のUI簡素化は未着手。ユーザーに「Factory UIの世界観を残すか、承認専用UIへ寄せるか」を確認してから行う。

このファイルは、Claude Codeとのディスカッションで固まった「自然言語の指示だけでCM・短編映画を作れるツール」の改訂設計書 兼 Codexへの実装記録。実際のコード状態と食い違いが出た場合は、このファイルの最新の確定方針(§2以降)を正としてコードを合わせること。

**確定方針(ユーザー最終確認済み): 画像生成(絵コンテ)・音声生成(ElevenLabsナレーション)・動画生成(Seedance)は全てHiggsfield MCP経由。APIキー(OPENAI_API_KEYを含む)は一切使わない。** Palmier Proは生成ではなく仕上げ工程(字幕・色・アップスケール・書き出し)専用。

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

### (b) Palmier Proの仕上げ生成系(アップスケール等)に、Seedanceと同等の承認/予算ゲートがない

生成そのものはHiggsfield MCPに統一したが、Palmier Proの`upscale_media`は依然として課金対象の生成系ツールであり、`generate_audio`等は使わないとしても`upscale_media`は仕上げ工程で使う想定(§3ステップ10)。現行の設計は Higgsfield/Seedance側の`APPROVED=1`+コスト見積フローしか定義しておらず、**Palmier Pro側の`upscale_media`呼び出しには承認なしで課金が発生しうる抜け穴が残る。**

**修正: `upscale_media`を呼ぶ前に、(1)`list_models`で対象モデルの仕様を提示、(2)実行する内容を一度ユーザーに自然言語で確認、を必須ステップとして`end-to-end-movie-pipeline.md`に明記する。**

### (c) 複数ショット/複数プロジェクトを想定したフォルダ規約がない

現行の`workspace/assets/reference-image-v1.png`、`workspace/prompts/seedance-9x16-v1.txt`のような命名は「現在進行中のプロジェクトは1つだけ」という前提の単数形("-v1")規約。重量パスは1プロジェクトで複数ショット(previs、絵コンテ、ナレーション、Seedance出力)を扱うため、このままではショット間でファイルが上書きされる。

**修正: 重量パス専用に `workspace/projects/<project_id>/shots/<shot_id>/` 配下へ `previs.blend`、`storyboard.png`、`narration.mp3`、`seedance_prompt.txt`、`seedance_output.mp4` を格納する規約を`end-to-end-movie-pipeline.md`に追加する。** 軽量パス(既存の単発CM運用)は現行の"-v1"命名のままでよく、変更不要。

## 3. 改訂後のパイプライン(Codexが`references/end-to-end-movie-pipeline.md`に反映すること)

```
[自然言語ブリーフ]
   ↓
[Blender previs] ローカル、完全自動、外部API不要
   ↓
[Higgsfield MCP: 画像生成(絵コンテ)] モデル名・img2img対応は要確認(§2b-a)
   ↓
承認ゲート1: 絵コンテ承認
   ↓
[Higgsfield MCP: ElevenLabsナレーション] workspace/scripts/elevenlabs-narration.sh(既存のまま)
   ↓
[Blender 本アニメーション最終化] 音声尺に合わせてカメラ/フレーム範囲確定
   ↓
[Higgsfield MCP: Seedance image-to-video]
   ↓
承認ゲート2: 素材承認(コスト承認・ログイン/クレジット確認を含む)
   ↓
[Palmier Pro: import_media → sync_audio → add_captions → apply_color → upscale_media → export_project]
   ↓
承認ゲート3: 最終書き出し前承認
```

セリフ確認ステップ(カメラ目線で喋るカットの有無)は既存の位置(絵コンテ承認の直後)のまま変更なし。認証が必要な生成系の窓口はHiggsfieldMCPひとつに統一されている。

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

## 5. UI/UX の見直し(workspace/ui/*)

現状の`workspace/ui/live-workflow.html`ほかは「工場/トレーディング端末」風の多パネルダッシュボード(`MarketFeedPanel`、`SystemPerformancePanel`、`TerminalLogTape`等、`workspace/ui/GENERATION_FACTORY_LOGIC.md`参照)。ゴールが「自然言語だけで完結」である以上、このUIの役割は**承認ゲートで人間が見るべき最小限の証拠を見せて承認/却下を受け取ること**に絞るべきで、現状は装飾要素が目的に対して過剰。

Codexへの提案(優先度順):

1. **承認は会話(チャット)で完結できることを明記する。** UIを開かなくても「絵コンテ承認します」で次に進めるようにする。UIは補助であって必須経路にしない。
2. **`gates.html`を3つの承認ゲート(絵コンテ/素材/最終書き出し)専用のシンプルな画面に絞る。** 各ゲートで「見るべき成果物(絵コンテ画像、ナレーション音声、コスト見積、最終動画プレビュー)」と「承認/却下ボタン相当のコピー可能なテキスト」だけを出す。
3. **装飾パネル(MarketFeedPanel、SystemPerformancePanel、TerminalLogTape等)は優先度を下げる。** `GENERATION_FACTORY_LOGIC.md`の「レビューしてほしい論点」1番(KPIの実データ化)を先に片付け、mock演出は`MOCK_*_UI_ONLY`のまま最小限に留める。
4. 上記1〜3は着手前にユーザーに「今のFactory UIの見た目・世界観は残したいか、承認専用の地味な画面に寄せてよいか」を確認すること(製品方針の判断はユーザーマター)。

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
6. **未着手:** §5のUI簡素化は、ユーザーに方針確認したうえで着手する(先に実装しない)。
7. **未着手:** §7の「軽量パスもHiggsfield画像生成に切り替えるか」は、ユーザーに確認してから着手する(このドキュメントの決定は重量パスのみに適用する)。

## 7. 未確定・ユーザー判断が必要な点

- **Higgsfield MCPの画像生成モデル名・img2img(参照画像入力)対応可否は未検証。** Higgsfield MCPが接続された環境で最初に確認すること。
- 既存の軽量パス(単発CM、`gpt-image-reference.sh`使用)も同じくHiggsfield MCP画像生成に切り替えるかは未決定。今回の「APIキー不使用」方針は重量パスの議論の中で決まったもので、軽量パスに自動適用はしていない。
- Factory UI(`workspace/ui/*`)の「工場/トレーディング端末」世界観を残すか、承認専用の地味なUIに寄せるかは製品方針次第。

## 8. X投稿を参考にした動画作成について

ユーザーから特定のX投稿(`https://x.com/ehuanglu/status/2072073069875855422`)のような動画を作りたいという要望があった。`references/higgsfield-mcp-demo-patterns.md`に「X Reference Summary: Liquid-Metal Desk VFX」として分析済み(スタイル参照のみ、素材自体は再利用しない)。

この案件用に以下を既に用意済み:

- `workspace/assets/reference-liquid-metal-desk-v1.jpg`(ユーザー自身のデスク実写、権利クリア)
- `workspace/prompts/liquid-metal-desk-v1.txt`(Seedance image-to-videoプロンプト、`Status: proposal`のまま未承認)

この案件はSeedance image-to-videoの既存ルート(軽量パス寄り)を使う想定で、画像生成(絵コンテ)ステップは使っていない。§2の画像生成プラットフォーム決定とは独立している。承認・予算確定後に`higgsfield-status.sh` → `seedance-cost.sh`と進める。
