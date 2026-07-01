# 新作リップCM 30秒 最終台本 / 生成前見積

**SUPERSEDED(2026-07-01、Claude Code): この台本は実際に実行され270 creditsで失敗した計画そのもの(`workspace/projects/lipstick-cm-30s/review-20260701-seedance-failed.md`参照)。「Blender商品参照とRina口元クロップを1枚にまとめたクリーン参照」「`final/clip_0{1,2}_*_seedance_final.txt`」は`references/known-failure-patterns.md` FP-001/002/003/008で撤回済みと明記されている。そのまま再利用しないこと。現行プロセスは`storyboard/06-seedance-handoff-after-approval.md`と`CODEX.md`タスク11。**

## Status

- Status: 生成前見積完了。台本・参照画像・カメラ割りは承認済み。最終の有料生成は未承認。
- Do not run Higgsfield generation until model, count, cost, reference images, output paths, and final permission are shown to the user and approved.
- ブランド名・商品名は仮称(プレースホルダー)。実在ブランドの権利は一切使用しない(下記「権利確認メモ」参照)。

## Fixed Production Constraints

- video_use_case: `commercial`
- 商品: 新作リップスティック(仮称: **ROUGE NOIR** — 実在ブランドではない、要確定)
- Aspect ratios: 9:16(縦、SNSフィード用)を主、16:9(横、LP/ポートフォリオ用)を副
- Duration: 合計30秒 = 15秒クリップ x 2本
- Model: `seedance_2_0`
- Mode: image-to-video。参照画像は下記「参照画像プラン」で確定
- Resolution target: 低コスト本命は`1080p/high`。確認用ドラフトなら`720p/high`。`4k/high`は高額オプション
- Audio: 初回案は`generate_audio=false`(Seedance映像のみ)。BGM/ナレーションは後編集または承認後にHiggsfield MCP ElevenLabsで別途生成
- Commercial rights gate: 必須(高級ブランドの世界観を参照するため特に厳格に)

## 企画意図

Diorのような高級コスメCMの**空気感(静けさ、間、光の質感、スローモーション、余白の美学)**を参照しつつ、実在ブランドの商標・ロゴ・ネーミングは一切使わないオリジナルの新作リップCMを作る。「説明しすぎない」「言葉より質感で魅せる」高級感を軸にする。

## ターゲット

- 高級コスメ・美容に関心のある層
- ブランドの世界観・映像美で心を動かされる層
- SNSフィードでスクロールを止める「静かな強さ」を持つ映像を求める層

## ブランド世界観の参照方針(重要)

- 「Diorのような高級感」は**スタイル参照のみ**として扱う: 抑制された色数、マクロ撮影の質感、スローモーション、静寂と余白、上質な光(ゴールド/シャンパン系のリムライト)。
- Diorのロゴ・書体・実際のパッケージデザイン・実際の商品名は再現しない。
- ブランド名・商品名は本番前にユーザーが確定する。それまでは仮称`ROUGE NOIR`をプレースホルダーとして使う。

## 冒頭3秒のフック

暗い背景の中、伏せられたシルエットにわずかな光だけが差し込む。音もなく、動きもほぼない「間」から始める。高級コスメCM特有の「静けさで惹きつける」導入。

## フォーマット別の役割

### 9:16 縦動画

- 主用途: Instagram/X/TikTokフィード
- 構図: 中央に商品、上下に余白を大きく取る。画面内テキストは最小限(ブランド名のみ)
- 狙い: フィード上で「高級感で止まる」

### 16:9 横動画

- 主用途: LP埋め込み、ポートフォリオ
- 構図: 左右の余白を活かした横長の静物構図、奥行きのあるライティング
- 注意: 縦用プロンプトをそのまま流用しない

## 映像構成(2クリップ構成、各15秒)

| Time | Clip | Visual | On-screen Text | Audio |
|---:|---|---|---|---|
| 0-3s | Clip 1 | 暗い背景、伏せられた商品のシルエットにわずかな光。静止に近い間。 | なし | 無音/環境音のみ |
| 3-8s | Clip 1 | キャップがゆっくり持ち上がる。金属パーツのマクロ質感、ゴールドのリムライトが反射する。 | なし | 無音/環境音のみ |
| 8-15s | Clip 1 | 商品がゆっくり回転し全体像が見える。深みのある発色、艶のある表面。スローモーション。 | `ROUGE NOIR`(小さく、控えめに) | 無音/環境音のみ |
| 15-21s | Clip 2 | 商品ヒーローからRina Hayunの口元だけにマッチカット。顔全体や手持ちは見せず、唇に色が入る前の静かな寄り。 | なし | 無音/環境音のみ |
| 21-26s | Clip 2 | Rina Hayunの唇に深いルージュ色がのる瞬間のクローズアップ。艶と発色の説得力を見せる。 | なし | 無音/環境音のみ |
| 26-30s | Clip 2 | 引きのショットで商品全体とブランドタグ。静かな余韻で終わる。 | `ROUGE NOIR` + `{タグライン、要確定}` | 無音/環境音のみ |

## 参照画像プラン

このプロジェクトは**軽量パス+任意のBlender previsオプション**を使うことを推奨する(`WORKFLOW.md` §6参照)。

- Blenderで、円柱+円錐プリミティブでリップスティックの筒を組み、金属光沢マテリアル+ゴールドのリムライト+暗い背景で「高級感のある物撮り」を1枚レンダーする。procedural previsは質感の细かい説得力(金属反射、艶)を作るのに向いている。
- そのレンダーを参照画像として、Higgsfield Seedanceのimage-to-videoに渡す。
- Clip 2では、生成済み架空キャスト`Rina Hayun`の口元クロップ`workspace/assets/cast/generated_20260629/rina_hayun_lips_closeup.png`を唇/肌トーンの補助参照にする。全顔・手持ち・本人紹介風の見せ方はしない。
- Clip 2の実生成には、Blender商品参照とRina口元クロップを1枚にまとめたクリーン参照`workspace/assets/references/lipstick-cm/clip_02_product_plus_rina_lips_clean.png`を使う。
- Blenderを使わない場合は、`workspace/scripts/gpt-image-reference.sh`で抽象的な高級感のある物撮り風参照画像を生成する代替案もある。
- どちらの場合も、参照画像はユーザー承認(G2)を経てから使う。

## CTA

`{ブランド名}` — タグラインは商品確定後に決める(例: 静けさの中に、色気を。等、要確定)

## 画面内テキスト

候補(最終プロンプトでは最小限に絞る):

- `ROUGE NOIR`(仮称)
- `{タグライン、要確定}`

明るすぎる特売感・煽り文句は使わない。文字は少なく、間を活かす。

## ナレーション案

初回案は**ナレーションなし**を推奨(高級コスメCMは映像と質感で語るものが多いため)。

音声を使う場合の案(要確定・仮称ベース):

> ROUGE NOIR。静けさの中に、色気を。

音声を使う場合はSeedance映像のみ生成し(`generate_audio=false`)、承認後にHiggsfield MCP ElevenLabsで別途ナレーション生成、`workspace/scripts/elevenlabs-narration.sh`を使う。

## 権利確認メモ

- 「Diorのような高級感」はスタイル参照のみ。Diorのロゴ・商標・実際のパッケージ・実際のブランド名は一切使用しない。
- 商品名・ブランド名は仮称。本番前にユーザーが確定した名称に置き換える。
- ユーザー提供の実写素材はなし。全て生成素材(Blenderprevis or GPT Image)を使う。
- 実在モデル・実在人物の顔を模倣しない。手元・唇のクローズアップは特定人物と分からない構図にする。
- Rina Hayunは既存の架空AI生成キャスト。Clip 2では唇/肌トーンの補助参照に限定し、実在インフルエンサー、顧客、専門家、推薦者として扱わない。
- 商用公開前に、人間が商標・パッケージデザインの類似性を最終確認する。

## 最終生成パッケージ

### 使用する素材

- Blender主参照: `workspace/assets/3d/renders/lipstick_cm_previs.png`
- Blender .blend: `workspace/assets/3d/blend/lipstick_cm_previs.blend`
- カメラ割り: `workspace/assets/3d/renders/lipstick_cm_panel_01_silhouette.png`, `workspace/assets/3d/renders/lipstick_cm_panel_02_cap_macro.png`, `workspace/assets/3d/renders/lipstick_cm_panel_03_hero_vfx.png`, `workspace/assets/3d/renders/lipstick_cm_panel_04_negative_space_tag.png`
- Rina Hayun唇クロップ補助参照: `workspace/assets/cast/generated_20260629/rina_hayun_lips_closeup.png`
- Clip 2用クリーン合成参照: `workspace/assets/references/lipstick-cm/clip_02_product_plus_rina_lips_clean.png`
- 最終Seedanceプロンプト:
  - Clip 1: `workspace/prompts/lipstick-cm/final/clip_01_0-15s_9x16_seedance_final.txt`
  - Clip 2: `workspace/prompts/lipstick-cm/final/clip_02_15-30s_9x16_seedance_final.txt`

### 生成後に出るもの

- Clip 1動画: `workspace/outputs/lipstick-cm-30s/clip_01_9x16.mp4`
- Clip 2動画: `workspace/outputs/lipstick-cm-30s/clip_02_9x16.mp4`
- Clip 1ジョブログ: `workspace/logs/lipstick-cm-clip_01.json`
- Clip 2ジョブログ: `workspace/logs/lipstick-cm-clip_02.json`
- 後工程: Palmier ProでBGM/SFX、必要なら字幕/テロップ配置、最終30秒書き出し

## 生成予算メモ / Cost Estimate

- 見積日時: 2026-07-01
- Account credits before generation: 996.8
- Model: `seedance_2_0`
- Count: 2 clips
- Duration: 15s x 2 = 30s
- Aspect ratio: `9:16`
- Bitrate: `high`
- Seedance audio: `generate_audio=false`

| Option | Clip 1 | Clip 2 | Total | Remaining | 用途 |
|---|---:|---:|---:|---:|---|
| `4k/high` | 330 | 330 | 660 | 336.8 | 最高画質だが高額 |
| `1080p/high` | 135 | 135 | 270 | 726.8 | 推奨。品質と費用のバランス |
| `720p/high` | 67 | 67 | 134 | 862.8 | 安い確認用ドラフト |

推奨: `1080p/high`。高級CMとして見せる最低ラインを保ちながら、`4k/high`の660 creditsから270 creditsへ抑えられる。

音声/BGM/SFXはSeedanceでは生成しない。動画承認後、Palmier Pro後工程で別見積・別承認にする。

## NG表現

- 「Dior」等の実在ブランド名・ロゴ・トレードドレスの再現
- 実在モデル・著名人の顔の再現
- 「必ず売れる」「絶対流行る」等の誇大な販促表現
- 医薬品的効能を示唆する表現(肌質改善を保証する等)

## 納品チェック項目

- 動画が開ける
- 9:16(主)/16:9(副)の指定どおりである
- 合計尺が30秒(15秒 x 2)である
- ブランド名・商品名が仮称のままなら、その旨を納品メモに明記する
- 実在ブランドの商標・ロゴ・パッケージを模倣していない
- 画面内テキストが最小限で、間を活かした構成になっている
- 生成ログ、プロンプト、URL、ジョブ情報が残っている
- known limitationsが納品メモに書かれている(仮称ブランド名である旨を含む)
