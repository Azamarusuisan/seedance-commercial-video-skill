# Codex Instructions — End-to-End Movie Pipeline 改訂設計書

Follow `AGENTS.md` and `workspace/agent-guides/cross-agent-runbook.md`.

## 実装ステータス(2026-07-01時点)

- 2026-07-01: 旧方針コミット`7711779`のズレを修正済み。`workspace/scripts/elevenlabs-narration.sh`をHiggsfield MCP経由として復元し、`record-mcp-json.sh`の`narration`種別を復元し、`image`種別を追加し、`workspace/scripts/higgsfield-image.sh`を追加した。
- 2026-07-01: `references/end-to-end-movie-pipeline.md`は、画像生成(絵コンテ)・音声生成(ElevenLabsナレーション)・動画生成(Seedance)をすべてHiggsfield MCP経由にする方針へ更新済み。重量パスでは`gpt-image-reference.sh`を使わない。
- 未検証: Higgsfield MCPの画像生成モデル名とimg2img(参照画像入力)対応可否。接続環境で最初に確認する。
- §5のUI簡素化は未着手。ユーザーに「Factory UIの世界観を残すか、承認専用UIへ寄せるか」を確認してから行う。
- 2026-07-01: `WORKFLOW.md`(全体フローの1〜100言語化)を新規作成し、ユーザーとすり合わせ済み。承認ゲート粒度・フォルダ規約・Palmier Pro仕上げ順は確定。軽量パスへBlender previsを任意オプションとして追加する方針も反映済み。
- 2026-07-01: **BGM/SFX生成が抜けていたことが判明し、Palmier Pro経由で追加する方針が確定(§2b-d、§6タスク9、未着手)。** Higgsfield一本化の唯一の例外。`WORKFLOW.md`§7-9bに詳細。
- 2026-07-01: **Higgsfield画像生成(image2)を必須から任意に格下げする方針が確定(§2c、§6タスク10、未着手)。** Blenderレンダーが絵コンテ・主参照を兼ねる。同リポジトリの`ascension-line-workflow-runbook.md`で既に検証済みの「Blender主素材・生成絵コンテは補助参照」原則を踏襲。上記7行目「画像生成…をHiggsfield MCP経由にする」は必須ステップとしては**古い**。画像生成は任意になった。

このファイルは、Claude Codeとのディスカッションで固まった「自然言語の指示だけでCM・短編映画を作れるツール」の改訂設計書 兼 Codexへの実装記録。実際のコード状態と食い違いが出た場合は、このファイルの最新の確定方針(§2以降)を正としてコードを合わせること。全体フローの完成形は`WORKFLOW.md`を参照(このファイルは実装タスクと決定の経緯、`WORKFLOW.md`は完成後の姿)。

**確定方針(ユーザー最終確認済み): 音声生成(ElevenLabsナレーション)・動画生成(Seedance)は全てHiggsfield MCP経由。APIキー(OPENAI_API_KEYを含む)は一切使わない。画像生成(絵コンテ)は任意。Blenderレンダーが主参照を兼ねるため必須ではない(§2c)。** Palmier Proは生成ではなく仕上げ工程(字幕・色・アップスケール・書き出し)専用、**ただしBGM/SFX生成(`generate_audio`)だけは唯一の例外としてPalmier Proを使う。** 軽量パスではBlender previsを任意オプションとして使える(§6タスク8)。

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

## 2c. 方針転換: Higgsfield画像生成(image2)は必須ではなく任意にする

ユーザーから「Blenderからimage2をかませる必要あるか」と問われ、既に同リポジトリの別プロジェクト`workspace/briefs/ascension-line-workflow-runbook.md`(3Dアクション映画`ascension_line`)で検証済みの原則があることが分かった:

> Blenderで作った3Dプリビズを主素材にして、Seedanceで映画的に肉付けする。生成絵コンテは補助参照です。主素材ではありません。

そのプロジェクトの明示的な禁止事項: 「補助参照を主素材として扱わない」「生成絵コンテだけを根拠にSeedanceへ進めない」。実際にClip 01/02はBlenderレンダーを主参照としてSeedance生成済みという実績もある。

**決定: この原則を`references/end-to-end-movie-pipeline.md`の重量パスにも適用する。**

- Blenderレンダー(7-2)が絵コンテを兼ねる。承認ゲート1はこのBlenderレンダーを見せて行う(無料、Higgsfield非依存)。
- Higgsfield MCP画像生成(`higgsfield-image.sh`)は**任意**。使う場合も「最終映像のトーン確認」用の補助参照に留め、Seedanceへの主参照として使わない。
- Seedanceへ渡す主参照画像はBlenderレンダーそのもの。プロンプトは「肉付け」方針(構図・配置は保持しつつ、写実的な質感・光をテキストで指示する)で書く。
- これにより、§2b(a)の「Higgsfield画像生成モデル名・img2img対応の未検証」はパイプラインのブロッカーではなくなる(任意機能の話になる)。

`WORKFLOW.md`の§1図・§2システム表・§7-3/7-4・§8ゲート表・§14既知の制約に反映済み。

## 3. 改訂後のパイプライン(Codexが`references/end-to-end-movie-pipeline.md`に反映すること)

```
[自然言語ブリーフ]
   ↓
[Blender previs] ローカル、完全自動、外部API不要。レンダーが絵コンテ=主参照を兼ねる(§2c)
   ↓
承認ゲート1: 絵コンテ承認(Blenderレンダーを見せる。無料)
   ↓
[任意] Higgsfield MCP: 画像生成 — トーン確認用の補助参照のみ、使わなくてよい(§2c)
   ↓
[Higgsfield MCP: ElevenLabsナレーション] workspace/scripts/elevenlabs-narration.sh(既存のまま)
   ↓
[Blender 本アニメーション最終化] 音声尺に合わせてカメラ/フレーム範囲確定
   ↓
[Higgsfield MCP: Seedance image-to-video]
   ↓
承認ゲート2: 素材承認(コスト承認・ログイン/クレジット確認を含む)
   ↓
[任意・承認後: Palmier Pro BGM/SFX生成] mirelo-sfx-v1.5-video-to-audio / elevenlabs-music等(唯一のHiggsfield一本化の例外、§2b-d)
   ↓
[Palmier Pro: import_media → sync_audio → add_captions → apply_color → upscale_media → export_project]
   ↓
承認ゲート3: 最終書き出し前承認
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
