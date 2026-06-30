# 天頂線 ASCENSION LINE Workflow Runbook

## 原則

この制作は「Blenderで作った3Dプリビズを主素材にして、Seedanceで映画的に肉付けし、後工程でナレーション・字幕・編集を完成させる」ワークフローです。

生成絵コンテは補助参照です。主素材ではありません。

有料生成は、生成対象・モデル・本数・秒数・参照素材・費用・出力先を表示し、ユーザーが直前に明示許可した場合だけ実行します。

状態JSONは記録であり、真実ではありません。実ファイル、生成payload、承認ログ、出力MP4を検証してから次工程へ進みます。

## 内部判定ブロック

UIではPhase 0-9で見せますが、内部の進行判定は次の5ブロックだけで行います。

1. Source Lock: Blenderが主素材、生成絵コンテが補助参照であることを固定する。
2. Clip Planning: Clipごとの役割、Blender上の対応範囲、保持する構造、足す映画要素、禁止事項を固定する。
3. Paid Generation Gate: 最終prompt、参照、費用、出力先、job保存先、payload hash、直前承認を確認する。
4. Review and Selection: 生成結果をBlender対Seedanceでレビューし、採用/保留/再生成/プロンプト修正を決める。
5. Post-production and Export: 採用MP4、ナレーション、字幕、Palmier、書き出し許可を確認する。

## 必須ゲート

### Gate A: Source Lock

- Blender `.blend` が存在する
- Blender render PNG が存在し、0 byteではない
- live capture が存在する、または不要理由が明記されている
- 主参照画像がBlender由来である
- 生成絵コンテは `support_reference_only`
- UI表示順が Blender -> Seedance output -> 補助絵コンテ
- Seedanceに残すBlender構造が言語化されている

### Gate B: Clip Intent

Clipごとに以下を持つ。

- 物語上の役割
- Blenderプリビズ上の対応範囲
- 主被写体
- continuity anchors
- cinematic enrichment targets
- forbidden changes
- 前後クリップとの接続
- 主参照画像
- 補助参照画像

### Gate C: Generation Payload

有料生成前に以下を表示する。

- Clip
- Model
- Duration
- Resolution
- Aspect ratio
- FPS, if available
- Bitrate
- `generate_audio=false`
- Primary reference
- Support reference
- Final prompt全文
- Negative constraints
- Estimated cost
- Output path
- Job JSON path
- Expected enrichment
- Known risks
- Approval hash

### Gate D: Paid Approval

- 承認は1回の生成にだけ有効
- 承認後に条件が変わったら無効
- 承認対象payload hashを保存
- 承認時刻を保存
- 実行後は承認を失効
- `APPROVED=1` は承認済みpayloadと一致する時だけ使う

### Gate E: Output Integrity

生成後すぐに確認する。

- result_url が保存されている
- local_path が保存されている
- MP4が存在し、0 byteではない
- 動画として読める
- 秒数が想定範囲内
- 解像度が想定値
- 音声トラックがない
- job json が保存されている
- 費用が保存されている

### Gate F: Blender-to-Seedance Review

以下をPass/Failで見る。

- Blender構造保持
- 灰色プリビズ感の除去
- 映画的肉付け
- ドローン保持
- 装甲バイク保持
- ネオン都市/高速道路保持
- 補助絵コンテに寄りすぎていない
- 読める文字なし
- 音声なし
- 前後接続

判断:

- Pass: `approved_for_edit`
- Minor issue: 編集補正メモつきで保持
- Major issue: プロンプト修正
- Structural failure: 追加生成を止めてプロンプトから直す

### Gate G: Post-production Readiness

- 採用済みMP4が必要数ある
- ナレーション音声がある
- SRT/VTT/JSONがある
- 字幕タイミングが音声に合う
- BGM/SFX方針がある
- Palmier MCPが使える
- 尺合わせ方針がある

### Gate H: Export Approval

- 最終尺
- 音声確認
- 字幕確認
- テロップ確認
- タイトル確認
- 権利/使用素材確認
- 書き出し解像度
- 書き出し形式
- ファイル名
- 出力先
- ユーザーの最終書き出し許可

## 素材の役割

### 主素材: Blenderプリビズ

- BLEND: `workspace/assets/3d/blend/action_movie_previs.blend`
- Render: `workspace/assets/3d/renders/action_movie_previs.png`
- Live capture: `workspace/assets/3d/live/blender_screen_current.png`

役割:

- 画面構造の基準
- 追跡路、ネオン車線、ドローン、装甲バイク、都市ブロックの位置関係
- Seedanceに渡す一番重要な参照画像

評価基準:

- Seedance結果がBlenderプリビズの構造を保持している
- ただし、見た目はBlenderそのままではなく、映画的な人物・質感・光・アクションに肉付けされている

### 補助参照: 生成絵コンテ

- Contact sheet: `workspace/assets/storyboards/ascension_line/generated_storyboard_contact_sheet.png`
- Clip panels: `workspace/assets/storyboards/ascension_line/generated_clip_01_storyboard.png` など

役割:

- 最終映像のトーン確認
- カットの方向性確認
- 色、密度、画角、クライマックス感の参考

禁止:

- 補助参照を主素材として扱わない
- 生成絵コンテだけを根拠にSeedanceへ進めない

### 構図参考

- `workspace/assets/source_refs/seedance_4k_storyboard_structure_ref.jpg`

役割:

- 下段絵コンテ付きの見せ方、レビューカード構造の参考
- ロゴ、文字、既存フッテージはコピーしない

## 制作フェーズ

### Phase 0: ワークフロー合意

確認すること:

- 主素材はBlenderプリビズ
- 生成絵コンテは補助参照
- 台本はナレーションのみ
- キャラクター同士のセリフは作らない
- Seedance映像は無音で生成する
- 音声、字幕、効果音、タイトルは後工程で作る

完了条件:

- `generation-state.json` の `pre_generation_checklist.workflow_alignment` が `approved`
- ユーザーがこの流れに合意している

### Phase 1: Blenderプリビズ確認

確認すること:

- Blenderファイルが存在する
- レンダーPNGが存在する
- UIまたはローカル確認で、Blenderプリビズが見える
- どの画面要素をSeedanceに残すか言語化されている

完了条件:

- `action_movie_previs.blend` と `action_movie_previs.png` が存在
- UI上で「Blenderプリビズが主素材」と表示される
- ユーザーが「このBlenderを元に肉付けする」と確認済み

### Phase 2: 台本確認

現在の方針:

- ナレーションのみ
- セリフなし
- 60秒想定
- 4本 x 15秒

ファイル:

- `workspace/briefs/3d-action-movie-ascension-60s-script.md`
- `workspace/subtitles/ascension_line/narration.txt`

完了条件:

- ナレーション本文が確定
- 読み上げトーンが確定
- セリフなしが確定

未完了なら:

- 音声生成へ進まない
- 字幕焼き込みへ進まない

### Phase 3: 字幕・テロップ設計

ファイル:

- `workspace/subtitles/ascension_line/telop.srt`
- `workspace/subtitles/ascension_line/telop.vtt`
- `workspace/subtitles/ascension_line/caption-plan.json`

役割:

- Palmier Proで配置する字幕の下書き
- 最終タイミングはナレーション音声生成後に調整

完了条件:

- テロップ文言が承認済み
- ナレーション音声の尺に合わせてタイミング調整可能
- Palmier Proの編集タイムラインに置ける状態

未完了なら:

- 完成動画扱いにしない

### Phase 4: Seedance生成前レビュー

必ず確認すること:

- 生成対象クリップ
- モデル
- 秒数
- 解像度
- アスペクト比
- ビットレート
- `generate_audio=false`
- 参照画像
- 出力先
- 推定費用
- 残クレジット
- 今回の生成が新規生成か、再生成か
- 期待する改善点

今回の重要ルール:

- Blenderを主参照にする
- 「Blenderそのまま」になっている場合は、次のプロンプトで肉付け指示を強くする
- 500 credits超の一括実行は避ける
- 追加生成はユーザーの直前許可まで止める

完了条件:

- ユーザーが「この条件で生成して」と明示
- `APPROVED=1` はその直後の実行だけに使う

### Phase 5: Seedance映像生成

生成方針:

- Seedanceは映像だけ
- 音声は生成しない
- 字幕もSeedance内に入れない
- 後編集のため、画面下部に字幕安全領域を残す

生成後に必ず記録するもの:

- result_url
- local_path
- job_id
- model
- prompt_file
- reference_image
- duration
- resolution
- aspect_ratio
- consumed credits

保存先:

- `workspace/outputs/clip_01.mp4`
- `workspace/outputs/clip_02.mp4`
- `workspace/logs/job-clip_01.json`
- `workspace/logs/job-clip_02.json`

完了条件:

- MP4がローカルに保存されている
- ffprobeで開ける
- `generation-state.json` の `jobs[]` に反映されている
- UIで動画として確認できる

### Phase 6: Blender対Seedanceレビュー

見ること:

- Blenderの構造が残っているか
- 映像が映画的に肉付けされているか
- 灰色ブロックやプリビズ感が残りすぎていないか
- 追跡、人物、ドローン、装甲バイクの読みやすさ
- 15秒の中で意味が通るか

判定:

- OK: 次のClipまたは音声工程へ進む
- NG: プロンプトを直して再生成候補にする
- 保留: UIに「レビュー中」と表示し、追加生成しない

現在:

- Clip 01/02は生成済み
- Clip 03/04は停止中
- Clip 01/02は「Blenderそのまま感」がレビュー対象

### Phase 7: ナレーション音声

前提:

- ユーザーが映像レビューで進行OKを出している
- ナレーション本文が確定している
- 声、トーン、費用、出力先を提示済み

生成方針:

- Higgsfield ElevenLabs
- 日本語
- 低く、映画的、抑制されたトーン
- 映像生成とは別ジョブ

未実行のまま完成扱いにしない。

### Phase 8: Palmier Pro編集

役割:

- Seedance MP4配置
- ナレーション音声配置
- 字幕・テロップ配置
- 効果音、BGM、タイトル
- 最終レビュー

現在のブロック:

- Palmier MCP: `Editor not available`

完了条件:

- Palmier Proで編集プロジェクト/タイムラインが開いている
- MCPまたは手動で素材配置ができる
- 字幕配置まで確認済み

### Phase 9: 書き出し・公開

前提:

- 映像OK
- 音声OK
- 字幕OK
- 権利・表記OK
- ユーザーの最終書き出し許可あり

公開は別許可。

## 現在地

2026-06-30時点:

- Blenderプリビズ: 作成済み
- 生成絵コンテ: 作成済み、補助参照として使用OK
- 台本: ナレーションのみで作成済み
- セリフ: なしで確定
- 字幕ファイル: SRT/VTT/JSON作成済み
- Seedance: Clip 01/02のみ生成済み
- Seedance Clip 03/04: 停止中
- 音声: 未生成
- 字幕配置: 未実行
- Palmier: Editor not available
- 次工程: Blender対Seedanceレビュー、必要ならプロンプト修正

現在のブロッカー:

- Clip 01/02のBlender対Seedanceレビューが未完了
- Clip 03/04の生成payloadが未承認
- ナレーション音声が未生成
- Palmier MCPが `Editor not available`

## バージョン管理

生成結果は上書きしません。

- 初回: `clip_01_v001.mp4`
- 再生成: `clip_01_v002.mp4`
- 採用版: `selected_version`

現在の既存ファイル `workspace/outputs/clip_01.mp4` と `clip_02.mp4` は `v001` として扱います。

各バージョンには、status, result_url, local_path, prompt_file, job_json, review_decision, rejection_reason を残します。

## 生成してよい条件

次のすべてが揃ったときだけ生成する。

1. 対象クリップが明確
2. 主参照がBlenderプリビズである
3. 補助参照の使い方が明確
4. プロンプトが「肉付け」方針になっている
5. モデル、秒数、解像度、費用、出力先が表示済み
6. ユーザーが直前に明示許可
7. 実行ログと保存先の反映先が決まっている

この条件が欠けた場合は生成しない。
