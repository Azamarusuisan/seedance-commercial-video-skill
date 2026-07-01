# Known Failure Patterns (フィードバックループ台帳)

## これは何か

Seedance/Blenderの生成物は再学習(ファインチューニング)できない第三者モデル。なので「モデルを再学習する」フィードバックループは組めない。代わりに、**失敗のたびにここへ症状・原因・修正ルールを追記し、次の生成の前に必ずこのファイルを読んでチェックする**という運用で、実質的に同じ効果(同じ失敗を繰り返さない)を作る。

- 失敗ログを集める = このファイルへの追記(エラー分析)
- モデルを更新する = プロンプト/ワークフローのルールを更新する(このファイル+`WORKFLOW.md`)
- 推論前のガード = 次の生成前にこのファイルを読み、該当パターンがないか確認する(人間承認ゲートの一部として)

新しい失敗が起きたら、都度この形式でエントリを追加すること。既存エントリは消さない(パターンの蓄積が価値)。

## 生成前チェックリスト(必須)

Seedance生成(cost見積もりも含む)前に、このファイルの全エントリに目を通し、今回のプロンプト/参照画像が同じ失敗を踏んでいないか確認する。確認したことを`review.json`または案件のcondition mdに一行残す。

---

## FP-001: Blenderのブロックアウトをそのまま`start_image`に使うと、Seedanceがそれを「守るべき絵」として再現してしまう

- **症状**: 動画が写実的なCMではなく、3Dソフトのレンダーやプレビューのように見える。マテリアルが安っぽい・平坦・プラスチック調。
- **原因**: Blenderは構図・カメラ・商品形状の設計図であり、画作り(質感・光・素材)の参照ではない。低ポリ/仮ライトの画像を`start_image`に渡すと、Seedanceはその見た目自体を保持しようとする。
- **修正ルール**: Seedanceに渡す前に、必ず写実的な「キービジュアル」(photoreal key visual)を別途生成し、それを`start_image`/`end_image`にする。Blenderレンダーは構図確認・比較用にのみ残す。
- **機械的な強制(2026-07-01追加)**: これはもう「運用ルールとして覚えておく」だけではない。`workspace/scripts/validate-seedance-input.py`が、`workspace/scripts/seedance-cost.sh`/`seedance-generate.sh`から`IMAGE_FILE`を使うたびに自動で呼ばれる。`asset_kind=blender_previs`(または`role=composition_only`)なアセットマニフェストがあれば即ブロック。マニフェストがなくても、`workspace/assets/3d/renders/`等のBlenderらしきパスなら見出しヒューリスティックでブロックする。Blenderの直渡しは、エージェントが忘れてももう通らない。
- **出典**: `workspace/projects/lipstick-cm-30s/postmortem-20260701-blender-fleshout-mismatch.md`、`workspace/schemas/asset-manifest.schema.json`、`workspace/scripts/validate-seedance-input.py`

## FP-002: 商品参照と人物参照を1枚の画像に合成すると「貼り合わせ」に見える

- **症状**: カットが「別々の写真を並べただけ」に見える。光・質感・世界観が統一されていない。
- **原因**: 1枚の参照画像に無関係な2つの被写体(商品ブロックアウト+唇クロップ)を合成すると、Seedanceは両方を別々の視覚目標として文字通りに扱う。
- **修正ルール**: 被写体ごとに別のキービジュアル/別ショットとして設計する。1枚の画像に複数の無関係な参照を混在させない。同じ照明・世界観で一から作り直す(コラージュしない)。
- **出典**: `workspace/projects/lipstick-cm-30s/postmortem-20260701-blender-fleshout-mismatch.md`

## FP-003: 「orbit light rings」「floating particles」等のグラフィック風の言葉が、実写の光ではなく2Dの線・点として literal に描画される

- **症状**: 映像に、白や黒の細い線・丸・点が、モーショングラフィックスのUIパーツやテンプレートのように浮かんで見える。写真的な光のボケ・反射ではなく、平面的な図形に見える。
- **原因**: プロンプトで光や粒子を「rings(輪)」「particles(粒)」のように図形的・グラフィックデザイン的な語彙で描写すると、Seedanceはそれを実際に線画/点として描画することがある。写真的な効果を意図しているなら、写真・撮影の語彙で描写する必要がある。
- **修正ルール**: 光や空気感を表現する時は、図形的な名詞(ring, line, dot, particle)ではなく、撮影用語(bokeh, soft glints, volumetric haze, shallow depth of field, warm rim light, lens flare)を使う。「輪」「粒」を数えられるモノとして描写しない。
- **出典**: `workspace/outputs/lipstick-cm-30s/review_frames/clip_01_contact.jpg`、`clip_02_contact.jpg`の目視レビュー(2026-07-01、Claude Code)。この文書が初出。

## FP-004: ツールが複数画像入力に対応しているのに、スクリプトが1枚しか渡せず、無理な事前合成に頼ってしまう

- **症状**: 参照素材を1枚の画像に手動で合成してから渡す羽目になり、その合成が不自然(FP-002のような貼り合わせ)になる。あるいは、本来複数の参照(商品/人物/構図違い)を活かせるはずが、結局1枚しか使われず情報量が落ちる。
- **原因**: ツール自体はマルチモーダル・複数参照画像に対応していることが多いが、それをラップするシェルスクリプトが単一の`image=`/`--image`パラメータしか実装していないため、使う側が「1枚に収めないといけない」と誤解する。具体例: `workspace/scripts/gpt-image-reference.sh`は`--image`を1つしか渡せないが、`image_gen.py`のCLI(`references/cli.md`)は「For multi-image edits, pass repeated `--image` flags. Their order is meaningful, so describe each image by index and role in the prompt.」と明記しており、複数画像+役割指定に対応している。`seedance-cost.sh`/`seedance-generate.sh`も`image=`単数のみで、Higgsfield MCP側が`start_image`/`end_image`や複数参照に対応しているかは未確認のまま。
- **修正ルール**: 新しい参照画像の渡し方を実装する前に、**ラップ先のツール本来のAPI/CLIが複数画像・マルチモーダル入力に対応していないか必ず確認する。** 対応していれば、事前合成で1枚に潰すのではなく、複数画像をそのまま渡し、プロンプト側で各画像の役割(index/role)を明記する。スクリプトが単一画像しかサポートしていないという理由だけで設計を単純化しない。
- **出典**: `${CODEX_HOME}/skills/.system/imagegen/references/cli.md`(2026-07-01、Claude Codeが確認)、ユーザー指摘「素材が結局1個しか入ってなかったり、マルチモーダルが強みなはずなのに全然活用できてない」。
- **修正状況**: 対応済み(2026-07-01、Claude Code)。`gpt-image-reference.sh`(`GPT_IMAGE_SOURCE_IMAGES`)と`higgsfield-image.sh`(`HIGGSFIELD_IMAGE_SOURCE_IMAGES`、`path:role`形式)の両方に複数画像対応を実装、dry-runで確認済み。Seedance側(`start_image`/`end_image`対応)はHiggsfield MCP接続環境での確認が未着手(`CODEX.md`§6タスク12)。

## FP-005: UI/ドキュメントの文言がBlenderを「主素材」であるかのように見せてしまう

- **症状**: `IMAGE_FILE=workspace/assets/3d/renders/xxx_previs.png`のような使い方が、UIやドキュメント上「これが正しい主参照だ」と読める書き方になっている。結果、エージェントも人間も「Blenderレンダーをそのまま使ってよい」と誤解する。
- **原因**: アセットに`asset_kind`(blender_previs/photoreal_key_visualなど)、`role`(composition_only/visual_truth)、`approval_status`が明示されておらず、UI(`workspace/ui/factory-futuristic.js`)や各種`references/*.md`が「Blenderプリビズ = 素材」という並びで表示・記述していた。
- **修正ルール**: Blenderに関する表示・記述は必ず「構図参照専用、Seedance入力不可」であることを明記する。UI文言は`構図参照: Blender Previs / Seedance入力不可`のように、役割と禁止事項をセットで書く。`主素材`という言葉をBlenderに使わない。
- **出典**: `CLAUDE.md`(2026-07-01、UI Update指示)。

---

## 新規エントリのテンプレート

```markdown
## FP-XXX: [一言で症状]

- **症状**: [何が画面/映像に出ているか]
- **原因**: [なぜそうなったか]
- **修正ルール**: [次回どう書けば防げるか、具体的に]
- **出典**: [postmortemファイルパス、または目視レビューの記録]
```
