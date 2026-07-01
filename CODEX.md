# Codex Instructions — End-to-End Movie Pipeline 改訂設計書

Follow `AGENTS.md` and `workspace/agent-guides/cross-agent-runbook.md`.

このファイルは、Claude Codeとのディスカッションで固まった「自然言語の指示だけでCM・短編映画を作れるツール」の改訂設計書 兼 Codexへの実装計画。**このファイル自体はまだ実装していない設計書。** Codexがこの内容に沿って実装する。

## 0. ゴール

ユーザーがCLI(または最小限のチャットUI)に自然言語で指示するだけで、Blenderプリビズ → 絵コンテ → ナレーション/BGM/SFX → Seedance動画 → 字幕/仕上げ、まで一気通貫で回る。**ユーザーが外部ツール(Blender GUI、Higgsfield Web UI、ElevenLabs Web UI、Palmier Proの手動編集画面など)を直接操作する場面を最小化する。** 操作はすべてエージェント(Codex/Claude)がCLI/MCP経由で行い、ユーザーは自然言語での承認・判断のみ行う。

## 1. 現状(このセッションまでに実装済みのもの)

- `references/end-to-end-movie-pipeline.md`: 重量パス(11ステップ)の定義。**このファイルは今回の監査で古くなった箇所があるので、本設計書の内容で更新が必要(§3参照)。**
- `workspace/blender/action_movie_previs.py`: Blenderプリビズの雛形。プロジェクトごとにこれを土台に新規bpyスクリプトを書き、`blender --background --python` で無人実行する運用は既に確立済み。**変更不要。**
- `workspace/scripts/gpt-image-reference.sh`: GPT Image (`gpt-image-2`) で絵コンテ/参照画像を生成。**変更不要。**
- `workspace/scripts/seedance-cost.sh` / `seedance-generate.sh`: Higgsfield MCP経由のSeedance動画生成リクエスト準備。**変更不要。**
- `workspace/scripts/elevenlabs-narration.sh`: 前ターンで「HiggsfieldMCP経由のElevenLabs」として作成。**§2の理由により設計ミス。作り直しが必要。**
- `workspace/scripts/record-mcp-json.sh`: `narration`種別を追加済み。**§2の理由により`narration`種別は不要になる可能性が高い(下記参照)。**
- `workspace/ui/*`: 「工場/トレーディング端末」風の多パネルダッシュボード(Factory UI)。**§4でUI/UXの見直しを提案。**

## 2. 今回の監査で見つかった、最も重要な訂正

Palmier Pro MCP(`mcp__palmier-pro__*`)を実際に呼んで確認した事実:

- `get_timeline` → `canGenerate: true`(このPalmier Proアカウントは既にサインイン/契約済み)
- `list_models(type=audio)` → 以下がPalmier Pro自身の`generate_audio`ツールから直接使える:
  - `elevenlabs-tts-v3`(ElevenLabs v3 TTS、21ボイス、`voicesSample: ["Rachel","Aria","Roger"]`、デフォルト`Rachel`)
  - `gemini-3.1-flash-tts`(30ボイス)
  - `elevenlabs-music` / `lyria3-pro` / `minimax-music-v2.6`(BGM)
  - `mirelo-sfx-v1.5-video-to-audio`(動画からSFX生成)

**結論: ナレーション(ElevenLabs)もBGMもSFXも、Higgsfield MCPを経由せず、Palmier Proの`generate_audio`ツールをエージェントが直接呼ぶだけで完結する。** Higgsfieldへの手動ログイン(Hermes Chrome)が必要になるのは、パイプライン全体で**Seedance動画生成の1箇所だけ**になる。

これにより:
- `workspace/scripts/elevenlabs-narration.sh`(MCPリクエストJSONを準備してHiggsfield MCPで実行、という間接層)は不要。Palmier Proのツールは他のCLIツールのようにシェル経由でrequest jsonを作る必要がなく、エージェントが直接`mcp__palmier-pro__generate_audio`を呼べばよい。
- `record-mcp-json.sh`の`narration`種別も、Higgsfield MCP経由でなくなるなら本来不要(Palmier Pro側の結果は`get_media`/`get_timeline`で直接確認できるため、別途サニタイズ記録の仕組みを重複させる必要がない)。

## 2b. 2回目の監査パスで見つかった穴(リファクタリング対象)

ユーザーから「リファクタリング含めて穴のないようにしたい」と指摘を受け、実際にコマンドとMCPを叩いて再監査した結果、3つ具体的な穴が見つかった。

### (a) GPT Image: `generate`しか使っておらず、Blenderレンダーを画像として渡せていない

`python3 image_gen.py --help` を確認したところ、`generate`(テキストのみ)とは別に **`edit --image IMAGE [--mask MASK] [--input-fidelity ...]`** という真のimg2img/編集モードが存在する。しかし現行の `workspace/scripts/gpt-image-reference.sh` は `generate` サブコマンドしか呼んでいない。

`end-to-end-movie-pipeline.md` のステップ3「Blenderプリビズの構図を言語化したプロンプトを渡す」は、テキストで構図を説明するだけで、実際のBlenderレンダー画像を入力していない。これでは絵コンテがショットごとに構図・色調がブレる可能性があり、「Blenderの`.blend`をプロジェクトの正にして一貫性を保つ」という設計の前提が絵コンテの段階で崩れる。

**修正: 新しいスクリプト `workspace/scripts/gpt-image-storyboard.sh`(または`gpt-image-reference.sh`に`--image`対応を追加)を作り、`image_gen.py edit --image <Blenderレンダーpng> --prompt <スタイル指定>` を呼ぶようにする。** Blenderレンダーを実際の入力画像として渡すことで、絵コンテがBlenderの構図を継承する。

### (b) Palmier Proの有料生成に、Seedanceと同等の承認/予算ゲートがない

`generate_audio` / `generate_video` / `generate_image` / `upscale_media` はいずれも課金対象のはずだが、現行の設計(および`SKILL.md`のBudget Lock節)は Higgsfield/Seedance側の`APPROVED=1`+コスト見積フローしか定義していない。§2の訂正でナレーション/BGM/SFX生成をPalmier Pro側に寄せた結果、**Palmier Pro側の生成呼び出しには承認なしで課金が発生しうる抜け穴ができた。**

**修正: Palmier Proの`generate_*`/`upscale_media`を呼ぶ前に、(1)`list_models`で対象モデルの仕様を提示、(2)生成する内容(テキスト/秒数/ボイス)を一度ユーザーに自然言語で確認、を必須ステップとして`end-to-end-movie-pipeline.md`に明記する。** Higgsfieldのような機械的な`APPROVED=1`ゲートはPalmier Pro MCPには存在しないため、エージェント運用ルールとして「生成前に必ず一度確認を挟む」ことをドキュメント上のハードルールにする。

### (c) 複数ショット/複数プロジェクトを想定したフォルダ規約がない

現行の`workspace/assets/reference-image-v1.png`、`workspace/prompts/seedance-9x16-v1.txt`のような命名は「現在進行中のプロジェクトは1つだけ」という前提の単数形("-v1")規約。重量パスは1プロジェクトで複数ショット(previs、絵コンテ、ナレーション、Seedance出力)を扱うため、このままではショット間でファイルが上書きされる。

**修正: 重量パス専用に `workspace/projects/<project_id>/shots/<shot_id>/` 配下へ `previs.blend`、`storyboard.png`、`narration.mp3`、`seedance_prompt.txt`、`seedance_output.mp4` を格納する規約を`end-to-end-movie-pipeline.md`に追加する。** 軽量パス(既存の単発CM運用)は現行の"-v1"命名のままでよく、変更不要。

## 3. 改訂後のパイプライン(Codexが`references/end-to-end-movie-pipeline.md`に反映すること)

```
[自然言語ブリーフ]
   ↓
[Blender previs] ローカル、完全自動、Higgsfield/API不要
   ↓
[GPT Image 絵コンテ] gpt-image-2、OPENAI_API_KEYのみ必要
   ↓
承認ゲート1: 絵コンテ承認
   ↓
[Palmier Pro generate_audio] ナレーション(elevenlabs-tts-v3) / BGM / SFX
   ※ Higgsfieldログイン不要。既にcanGenerate:trueなら即実行可能
   ↓
[Blender 本アニメーション最終化] 音声尺に合わせてカメラ/フレーム範囲確定
   ↓
[Higgsfield MCP: Seedance image-to-video] ← パイプライン中で唯一Higgsfieldログインが必要な箇所
   ↓
承認ゲート2: 素材承認(コスト承認・ログイン/クレジット確認を含む)
   ↓
[Palmier Pro: import_media → sync_audio → add_captions → apply_color → upscale_media → export_project]
   ↓
承認ゲート3: 最終書き出し前承認
```

セリフ確認ステップ(カメラ目線で喋るカットの有無)は既存の位置(絵コンテ承認の直後)のまま変更なし。

## 4. 「外部ツールのUIを一切触らない」監査結果

| 項目 | 状態 | 理由 |
|---|---|---|
| Blender操作 | ✅ ゼロタッチ | `--background`実行、GUI不要 |
| GPT Image絵コンテ | ✅ ゼロタッチ | CLI+APIキー(env var)のみ |
| ナレーション/BGM/SFX | ✅ ゼロタッチ(今回の訂正で実現) | Palmier Pro `generate_audio` を直接呼ぶ |
| 字幕(caption) | ✅ ゼロタッチ | Palmier Pro `add_captions` を直接呼ぶ。中身の精度チェックは人間の「判断」であってUI操作ではない |
| 色/アップスケール/書き出し | ✅ ゼロタッチ | Palmier Pro MCPを直接呼ぶ |
| Seedance動画生成 | ⚠️ 手動ログインが前提 | Higgsfieldへの認証情報自動入力を方針として禁止しているため(`AGENTS.md`/`HERMES.md`)。動画ごとではなくセッション/Cookie失効ごとに発生。**意図的な穴であり、セキュリティ上ゼロにすべきではない。** |
| Palmier Proのサインイン/契約状態 | ⚠️ 前提条件 | `canGenerate:false`の場合は全生成ツールが失敗する。現在のセッションでは`true`を確認済みだが、セッション切れ時は再度ユーザーがPalmier Proアプリでサインインする必要がある |
| GPT Image APIキー発行 | ⚠️ 一回限りの環境セットアップ | OpenAIダッシュボードでの発行自体はUI操作だが、動画ごとの操作ではない |
| 最終公開判断・権利確認・実在音声の同意確認 | 🔒 意図的に人間判断のまま | ハードルールで自動化禁止。UIを「操作」するのではなく「判断」するステップなので穴として扱わない |

**結論: 動画1本を作るたびに発生しうるUI操作は「Higgsfieldログイン(セッション切れ時のみ)」だけまで削減できる。** それ以外は今回の設計変更(§2)で解消済み。

## 5. UI/UX の見直し(workspace/ui/*)

現状の`workspace/ui/live-workflow.html`ほかは「工場/トレーディング端末」風の多パネルダッシュボード(`MarketFeedPanel`、`SystemPerformancePanel`、`TerminalLogTape`等、`workspace/ui/GENERATION_FACTORY_LOGIC.md`参照)。ゴールが「自然言語だけで完結」である以上、このUIの役割は**承認ゲートで人間が見るべき最小限の証拠を見せて承認/却下を受け取ること**に絞るべきで、現状は装飾要素が目的に対して過剰。

Codexへの提案(優先度順):

1. **承認は会話(チャット)で完結できることを明記する。** UIを開かなくても「絵コンテ承認します」で次に進めるようにする。UIは補助であって必須経路にしない。
2. **`gates.html`を3つの承認ゲート(絵コンテ/素材/最終書き出し)専用のシンプルな画面に絞る。** 各ゲートで「見るべき成果物(絵コンテ画像、ナレーション音声、コスト見積、最終動画プレビュー)」と「承認/却下ボタン相当のコピー可能なテキスト」だけを出す。
3. **装飾パネル(MarketFeedPanel、SystemPerformancePanel、TerminalLogTape等)は優先度を下げる。** `GENERATION_FACTORY_LOGIC.md`の「レビューしてほしい論点」1番(KPIの実データ化)を先に片付け、mock演出は`MOCK_*_UI_ONLY`のまま最小限に留める。
4. 上記1〜3は着手前にユーザーに「今のFactory UIの見た目・世界観は残したいか、承認専用の地味な画面に寄せてよいか」を確認すること(製品方針の判断はユーザーマター)。

## 6. Codexへの実装タスク(優先順)

1. `workspace/scripts/elevenlabs-narration.sh` を削除し、`references/end-to-end-movie-pipeline.md` のステップ6を「Palmier Pro `generate_audio`(`elevenlabs-tts-v3`など)をエージェントが直接呼ぶ」という記述に書き換える。BGM/SFXもこのステップで扱えることを追記する。
2. `workspace/scripts/record-mcp-json.sh` の`narration`種別を削除する(Palmier Pro結果は`get_media`/`get_timeline`で確認できるため重複した記録経路は不要)。
3. `references/end-to-end-movie-pipeline.md` の「前提」セクションから「ElevenLabsはHiggsfield MCP経由」の記述を削除し、「Higgsfieldが必要なのはSeedance生成のみ」と明記する。「Known limitations」の課金箇所の記述も合わせて更新する。
4. `SKILL.md` / `AGENTS.md` の該当参照文言に大きな変更は不要だが、`end-to-end-movie-pipeline.md`のリンク先説明文がHiggsfield ElevenLabsに言及していないか確認し、あれば整合させる。
5. §2b(a): `workspace/scripts/gpt-image-reference.sh`に`edit --image`対応を追加(または新規`gpt-image-storyboard.sh`を作成)し、Blenderレンダーを実際に入力画像として渡すよう`end-to-end-movie-pipeline.md`ステップ3を書き換える。
6. §2b(b): Palmier Pro `generate_*`/`upscale_media`呼び出し前に「モデル仕様提示 → ユーザー確認」を必須にするルールを`end-to-end-movie-pipeline.md`に追記する。
7. §2b(c): 重量パス用に`workspace/projects/<project_id>/shots/<shot_id>/`のフォルダ規約を`end-to-end-movie-pipeline.md`に追記する。軽量パスの既存命名は変更しない。
8. §5のUI簡素化は、ユーザーに方針確認したうえで着手する(先に実装しない)。

## 7. 未確定・ユーザー判断が必要な点

- Palmier Proの`elevenlabs-tts-v3`は、Higgsfield経由で想定していたElevenLabsと品質・ボイスラインナップが同一か未検証。実際にナレーションを1本生成して聴き比べる必要があるかもしれない。
- Factory UI(`workspace/ui/*`)の「工場/トレーディング端末」世界観を残すか、承認専用の地味なUIに寄せるかは製品方針次第。
- `image_gen.py edit`の`--input-fidelity`がBlenderの手続き型プリミティブレンダー(写実的でない、単純な形状)に対してどこまで構図を保持できるかは未検証。実際に1枚試して品質を見る必要がある。

## 8. X投稿を参考にした動画作成について

ユーザーから特定のX投稿(`https://x.com/ehuanglu/status/2072073069875855422`)のような動画を作りたいという要望があった。`references/higgsfield-mcp-demo-patterns.md`に既に「X投稿はスタイル/構造の参照として扱い、素材自体は権利確認なしに最終物へ使わない」という手順が確立済みなので、新しいルールは不要。ただし以下は未完了:

- WebFetchは402 Payment Requiredで失敗(X側が未認証アクセスをブロック)。Safari操作用のツールはなく、Chrome自動化ツールを使うとこのリポジトリの`Browser Contract`(`workspace/agent-guides/cross-agent-runbook.md`)が禁止する「サインイン済み個人ブラウザ」に触れることになるため使用を見送った。
- ユーザーから投稿内容(スクリーンショット、動画ファイル、または尺・演出の説明)を直接受け取り次第、`higgsfield-mcp-demo-patterns.md`の書式(post text / output style / creative pattern / reusable lesson)で追記する。
