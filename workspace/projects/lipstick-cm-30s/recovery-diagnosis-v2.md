# Recovery Diagnosis v2 — Lipstick CM

## 失敗原因

### 3DをそのままSeedanceに渡した

Blenderは構図の正であり、画作りの正ではない。
前回はBlenderの仮マテリアル、低ポリ感、viewport lighting、平たい板、安いCG感がSeedanceに継承された。

### 絵コンテ肉付け工程が欠落していた

本来は以下が必要だった。

```text
Blender panel
-> visual-handoff.json
-> GPT Image / Higgsfield image prompt
-> photoreal storyboard
-> human approval
-> Seedance
```

既存フローでは `Blender panel -> Seedance` に短絡していた。

### 参照素材を1枚に潰した

Clip 2で商品とRina唇参照を1枚に合成したため、貼り合わせ感が出た。
今後は商品ショット、唇ショット、最終packshotを別ショット/別キー画像として扱う。

### キャスト参照の扱いが弱かった

Rina Hayunは唇/肌トーン参照のみ。
全顔、手持ち、顧客証言、インフルエンサー風にしてはいけない。

### 音声/字幕/編集までのゲートが弱かった

失敗動画にBGM/SFX/字幕/Palmierを足しても根本解決にならない。
映像承認後に初めて音声/編集へ進む。

## 正しい修正方針

```text
Blender previs
  -> visual-handoff.json
  -> GPT Image / Higgsfield image storyboard prompt
  -> 8-panel photoreal storyboard board
  -> 4 core photoreal key visuals
  -> human approval
  -> Seedance cost request
  -> human approval of cost/model/output
  -> Seedance generation
  -> contact sheet / review
  -> human visual approval
  -> narration / BGM / SFX / subtitles / Palmier edit
  -> final review
  -> delivery / learning log
```

This file is project-specific evidence. The generic rule lives in `references/image-to-video-handoff.md`, `references/end-to-end-movie-pipeline.md`, `workspace/schemas/*`, and `workspace/scripts/validate-seedance-input.py`.
