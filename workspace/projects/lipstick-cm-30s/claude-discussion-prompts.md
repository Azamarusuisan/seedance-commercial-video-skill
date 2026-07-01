# Claude Discussion Prompts — Lipstick CM Recovery

このファイルは、Claude Code / Claude / ChatGPT / Codexに渡して議論・監修・実作業を進めるためのプロンプト集。

対象リポジトリ:

`/Users/zettai/Downloads/seedance-commercial-video-skill`

対象案件:

`workspace/projects/lipstick-cm-30s/`

最新版のClaude再投入タスク:

`workspace/projects/lipstick-cm-30s/codex-to-claude-handoff-20260701.md`

## 0. 最初に渡す総合プロンプト

```text
あなたは高級コスメCM制作ワークフローの監修者兼実装者です。

対象は私が所有するローカルリポジトリ:
/Users/zettai/Downloads/seedance-commercial-video-skill

まず以下を必ず読んでください。

- CLAUDE.md
- WORKFLOW.md
- workspace/projects/lipstick-cm-30s/postmortem-20260701-blender-fleshout-mismatch.md
- workspace/projects/lipstick-cm-30s/review-20260701-seedance-failed.md
- workspace/projects/lipstick-cm-30s/seedance-conditions.md
- workspace/briefs/lipstick-cm-30s-script.md

背景:
新作リップCMで、Blenderプリビズを元にSeedance 2本を生成しましたが失敗しました。
失敗理由は、Blenderの低ポリ/ブロックアウト画像をSeedanceのstart_imageとして直接渡したため、生のBlender感が残りすぎたことです。
Clip 2も、商品とRina Hayunの唇クロップを1枚に合成して渡したため、商品カットと唇カットが貼り合わせに見えました。

ユーザーの本来の意図:
- Blenderは構図、商品形状、カメラ割り、動きの設計図。
- 最終映像はハイブランドCM級の写実CG。
- Blenderの板、低ポリ感、仮ライト、仮パーティクルをそのまま見せたいわけではない。
- Rina Hayunは唇クロップ補助参照のみ。全顔なし、手持ちなし、本人/インフルエンサー表現なし。
- Seedance前に、Blender絵コンテから肉付けされた写実キー画像を作り、見せて承認を取るべき。

あなたにしてほしいこと:
1. 今回の失敗原因を、制作ワークフローの観点で批判的にレビューしてください。
2. 「Blenderから肉付けする」とは実務上どういう工程なのか、正しい定義を出してください。
3. 次に作るべき写実キー画像の種類、枚数、用途を提案してください。
4. 追加の有料Seedance生成をせず、まず写実キー画像作成と承認までの作業計画を出してください。
5. 既存のWORKFLOW.mdやCLAUDE.mdに足りない注意点があれば修正案を出してください。

禁止:
- 追加の有料Seedance生成を始めない。
- 失敗MP4を採用しない。
- Palmier Pro仕上げ、音、字幕、書き出しに進まない。
- 「Blender画像をそのままSeedanceに渡せば肉付けできる」と再度主張しない。
- コスト承認と生成承認を混同しない。

出力:
- Diagnosis
- Correct definition of Blender flesh-out
- Proposed key visuals
- Revised workflow
- Concrete next actions
- Questions for user
```

## 1. 失敗レビューだけをさせるプロンプト

```text
以下の失敗テイクをレビューしてください。

対象:
- workspace/outputs/lipstick-cm-30s/clip_01_9x16.mp4
- workspace/outputs/lipstick-cm-30s/clip_02_9x16.mp4
- workspace/outputs/lipstick-cm-30s/review_frames/clip_01_contact.jpg
- workspace/outputs/lipstick-cm-30s/review_frames/clip_02_contact.jpg
- workspace/logs/lipstick-cm-clip_01.json
- workspace/logs/lipstick-cm-clip_02.json

評価基準:
- ハイブランドのリップCMとして成立しているか
- Blenderプリビズが「肉付け」されているか
- 生Blender感、板、低ポリ感、仮ライトが残っていないか
- Clip 2の口元カットが貼り合わせに見えないか
- Rina Hayunの使い方が「唇クロップ補助参照」に留まっているか
- 音や字幕を付ける価値がある素材か

前提:
この2本はすでにユーザーが「全然だめ」と判断しています。擁護ではなく、失敗の構造を明確にしてください。

出力:
- 採用可否
- 具体的に悪い箇所
- 原因
- 次に変えるべき参照画像設計
- 再生成前に満たすべきチェックリスト
```

## 2. 「Blender肉付け」の定義を詰めるプロンプト

```text
「Blenderから肉付けする」という工程を、AI動画生成ワークフローとして厳密に定義してください。

前提:
- Blenderはローカルで作ったプリビズ/絵コンテです。
- 目的は、Blenderの構図・カメラ・商品形状・動きの意図を守りつつ、最終映像はハイブランドCM級の写実CGにすることです。
- Blenderの低ポリ感や仮ステージを最終映像に残すことは失敗です。

議論してほしいこと:
1. Blenderが担うべき情報
2. Blenderが担うべきではない情報
3. Seedanceが担うべき情報
4. Seedanceに期待しすぎてはいけない情報
5. 写実キー画像が必要になる条件
6. start_image / end_image / multi-shot / separate clip の使い分け
7. 高級CMで失敗しやすい参照画像の渡し方

最終的に、WORKFLOW.mdに追記できるルールとしてまとめてください。
```

## 3. 写実キー画像の設計をさせるプロンプト

```text
新作リップCM「ROUGE NOIR」の写実キー画像設計をしてください。

読んでほしいファイル:
- workspace/briefs/lipstick-cm-30s-script.md
- workspace/projects/lipstick-cm-30s/seedance-conditions.md
- workspace/projects/lipstick-cm-30s/postmortem-20260701-blender-fleshout-mismatch.md

既存素材:
- Blender主参照: workspace/assets/3d/renders/lipstick_cm_previs.png
- Blenderパネル:
  - workspace/assets/3d/renders/lipstick_cm_panel_01_silhouette.png
  - workspace/assets/3d/renders/lipstick_cm_panel_02_cap_macro.png
  - workspace/assets/3d/renders/lipstick_cm_panel_03_hero_vfx.png
  - workspace/assets/3d/renders/lipstick_cm_panel_04_negative_space_tag.png
- Rina Hayun唇クロップ: workspace/assets/cast/generated_20260629/rina_hayun_lips_closeup.png

要件:
- ハイブランドのリップCM品質。
- Diorなど実在ブランドのロゴ、パッケージ、書体、トレードドレスはコピーしない。
- ROUGE NOIRは仮称の架空ブランド。
- Rina Hayunは唇/肌トーンの補助参照のみ。全顔なし、手持ちなし。
- Blenderの構図と商品形状は守る。
- ただしBlenderの板、低ポリ感、仮ステージは消す。

作ってほしいもの:
1. 必要なキー画像の枚数と役割
2. 各キー画像のプロンプト案
3. 各キー画像の参照素材
4. Seedanceへ渡す時のstart/end image設計
5. ユーザーに見せる承認用ボードの構成
6. 追加生成前のチェックリスト

まだ有料Seedance生成はしないでください。
```

## 4. Claude Codeに実作業を頼むプロンプト

```text
Claude Codeとして、このリポジトリ内で実作業してください。

目的:
失敗したリップCM Seedance生成を立て直すため、次の有料動画生成前に必要な「写実キー画像」工程を作ってください。

やってほしいこと:
1. CLAUDE.md / WORKFLOW.md / postmortem / review / seedance-conditions / 台本MDを読む。
2. 現在の失敗状態をUI stateと案件MDに反映する。
3. Blenderパネルごとに写実キー画像プロンプトを作成する。
4. 生成する場合は、動画ではなく画像だけ。実行前にモデル・費用・参照・出力先を提示して人間承認を取る。
5. 有料Seedance動画生成は絶対にしない。
6. できた成果物はGitに入れてpushする。

重要:
- raw Blender renderをSeedance start_imageに直接使う方針へ戻さない。
- 失敗MP4を仕上げ素材扱いしない。
- Clip 2の口元参照を商品と1枚に雑に合成しない。
- 口元キー画像は別ショットとして設計する。

期待成果物:
- workspace/projects/lipstick-cm-30s/key-visual-plan.md
- workspace/prompts/lipstick-cm/keyframes/*.txt
- 必要なら workspace/assets/references/lipstick-cm/ 以下に承認用ボード
- 更新された generation-state.json
- コミットとpush
```

## 5. ワークフロー監査プロンプト

```text
WORKFLOW.mdとCLAUDE.mdを監査してください。

観点:
- 今回の「Blenderを直接Seedance start_imageにして失敗した」問題が、今後再発しない書き方になっているか。
- 高級CM・写実CMでは、Blenderは構造参照、写実キー画像が画作り参照、Seedanceは動画化、という役割分担が明確か。
- 承認ゲートが足りているか。
- コスト承認と生成承認が分離されているか。
- BGM/SFX/Palmier Proへ進む条件が明確か。
- 失敗テイクを採用しないルールが明確か。

出力:
- 問題点
- 修正すべき文言
- 追加すべきルール
- そのまま使えるパッチ案
```

## 6. ユーザーに確認すべき質問を作るプロンプト

```text
次にユーザーへ確認すべき質問を、最大5つに絞って作ってください。

前提:
- 追加の有料動画生成は停止中。
- まず写実キー画像を作る必要がある。
- ユーザーはハイブランドCM品質を求めている。
- ユーザーはRina Hayunの唇だけを使いたい。
- 500 credits級の高額生成は避けたい。

質問は短く、制作判断に必要なものだけにしてください。
選択肢がある場合は、推奨案を先に書いてください。
```

## 7. そのままClaudeに送る短縮版

```text
このリポジトリのリップCM案件を引き継いでください。

必ず先に読んでください:
- CLAUDE.md
- WORKFLOW.md
- workspace/projects/lipstick-cm-30s/postmortem-20260701-blender-fleshout-mismatch.md
- workspace/projects/lipstick-cm-30s/review-20260701-seedance-failed.md
- workspace/projects/lipstick-cm-30s/seedance-conditions.md

状況:
1080p/highでSeedance 2本を生成したが失敗。raw Blenderをstart_imageにしたため、生Blender感が残り、Clip 2は口元だけ別素材の貼り合わせに見えた。

次にやること:
有料動画生成は止める。まずBlender絵コンテから写実キー画像を作る計画とプロンプトを作る。キー画像をユーザーに見せて承認を取る。

絶対にしないこと:
- raw Blender画像をそのままSeedance start_imageにしない。
- 失敗MP4を採用しない。
- Palmier Pro仕上げへ進めない。
- 追加Seedance生成をしない。

成果物:
- key visual plan
- keyframe prompts
- updated workflow/state notes
- git commit/push
```
