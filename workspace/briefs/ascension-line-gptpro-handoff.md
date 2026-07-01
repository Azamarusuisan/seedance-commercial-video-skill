# GPT Pro Review Request: 制作ツールのワークフローは完璧か

以下をGPT Proに渡して、このツールのロジックに抜け漏れがないかレビューしてください。

```text
以下は、3Dアクション映画「天頂線 ASCENSION LINE」を制作するためのローカル制作ツールのワークフロー設計です。

この設計が「実制作で破綻しないか」「生成前ゲートとして十分か」「UIで現在地を把握できるか」「Blender主素材からSeedance肉付けへの流れが明確か」をレビューしてください。

特に見てほしいこと:
1. 抜けている工程はないか
2. 有料生成前の確認ゲートは十分か
3. Blenderを主素材として扱うロジックは明確か
4. 生成絵コンテを補助参照に留める設計になっているか
5. 音声、字幕、Palmier編集が後工程として正しく分離されているか
6. UIが「できている風」にならず、実ファイル・状態JSONと一致する設計か
7. 失敗時、レビュー時、再生成時の判断が足りているか
8. もっとシンプルにできる部分があるか

回答してほしい形式:
- 総合評価: 完璧 / ほぼ良い / 不足あり / 危険
- 致命的な抜け
- 追加すべきゲート
- UIで必ず見せるべき項目
- Seedance生成前に必ず止める条件
- 修正後の理想ワークフロー

---

目的:
Blender、Seedance、ナレーション、字幕、Palmier編集を一つの制作フローとして管理する。
UIは装飾ではなく、「今どこまでできているか」「次に何を確認すべきか」「有料生成してよい状態か」を見えるようにする進行管理ツール。

基本思想:
1. Blenderが主素材。
2. SeedanceはBlenderプリビズを映画的に肉付けする工程。
3. 生成絵コンテは補助参照。
4. 音声、字幕、効果音、タイトルはSeedanceではなく後工程。
5. 有料生成は、条件提示とユーザーの直前許可がある時だけ実行する。

主要ファイル:
- UI本体: workspace/ui/live-workflow.html
- UIロジック: workspace/ui/factory-futuristic.js
- UIスタイル: workspace/ui/factory-futuristic.css
- 状態JSON: workspace/ui/state/generation-state.json
- ワークフロー説明: workspace/briefs/ascension-line-workflow-runbook.md
- 生成前チェック: workspace/scripts/ascension-workflow-check.sh

状態管理の中心:
workspace/ui/state/generation-state.json

このJSONが現在地を持つ。
UIはこのJSONを読み、以下を表示する。
- current_work: 今の作業状態
- workflow_contract: 制作ルールと現在フェーズ
- pre_generation_checklist: 生成前に必要な確認
- jobs: 各Seedanceクリップの状態
- blender_to_seedance: Blender主素材からSeedance肉付けへのレビュー状態
- voice: ナレーション音声の状態
- subtitles: 字幕ファイルと配置状態
- palmier: Palmier Pro接続状態
- approval_contract: 有料生成許可ゲート

正しい工程:

Phase 0: ワークフロー固定
- Blender主素材
- Seedanceは肉付け
- 生成絵コンテは補助
- ナレーションのみ
- セリフなし
- 音声と字幕は後工程

Phase 1: Blender確認
- .blend と render png が存在するか
- UIでBlender主素材として見えるか
- Seedanceに残す構造が言語化されているか

Phase 2: 台本確認
- ナレーション本文があるか
- セリフなしで確定しているか
- 60秒/4クリップ構成になっているか

Phase 3: 字幕設計
- SRT/VTT/JSONがあるか
- Palmierで配置する前提になっているか
- Seedance内で字幕を生成しようとしていないか

Phase 4: 生成前レビュー
- 生成対象クリップ
- モデル
- 秒数
- 解像度
- アスペクト比
- ビットレート
- generate_audio=false
- 主参照画像
- 補助参照画像
- 推定費用
- 出力先
- 期待する肉付け内容
これをUIまたはテキストで表示する。

Phase 5: 有料生成
- ユーザーの直前許可がある場合だけ実行。
- APPROVED=1 はこの直前許可の後だけ使う。
- 生成後は result_url、local_path、job json、費用を必ず状態JSONに反映する。

Phase 6: Blender対Seedanceレビュー
- Seedance結果がBlender構造を保持しているか
- Blenderそのままの灰色プリビズ感が残っていないか
- 映画的な人物、質感、雨、火花、煙、光、カメラ演出が足されているか
- NGなら追加生成ではなく、まずプロンプトを直す

Phase 7: ナレーション音声
- 映像レビュー後に実行
- ElevenLabs/Higgsfield想定
- 音声生成も有料なので、条件提示と許可が必要

Phase 8: Palmier編集
- Seedance MP4
- ナレーション音声
- 字幕/テロップ
- 効果音/BGM
- タイトル
をタイムラインに置く。
Palmier MCPが Editor not available の場合はブロック扱い。

Phase 9: 書き出し
- 映像、音声、字幕、権利、表記のレビュー後
- 別途書き出し許可が必要

絶対に避けること:
- UIが「できている風」なのに実ファイルや状態JSONが追いついていない
- 生成絵コンテを主素材のように扱う
- Blenderが見えていないのに生成へ進む
- 音声や字幕が未実行なのに完成扱いにする
- 有料生成の直前許可なしに生成する
- result_urlやlocal_pathを保存し忘れる

UIで見せるべき順番:
1. 現在フェーズ
2. Blender主素材
3. Seedance肉付け結果
4. 補助絵コンテ
5. 台本/ナレーション状態
6. 字幕状態
7. Palmier接続状態
8. 生成許可ゲート

一言で言うと:
このツールは「Blenderを骨格にしてSeedanceで肉付けし、音声・字幕・編集まで進める制作ラインの状態管理UI」です。
最重要ロジックは、有料生成より前に、主素材・後工程・費用・許可を必ず見える化することです。
```
