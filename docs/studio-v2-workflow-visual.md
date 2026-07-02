# Studio v2 Workflow Visual

このツールの正規制作ラインは Studio v2 です。v1 Factory UI / `workspace/` は凍結された参照・過去ログ扱いです。

## 全体フロー

```mermaid
flowchart TD
  A["1. 案件作成<br/>project.json / bible.json / permission.json"] --> B["2. 素材登録<br/>AssetRegistry + sha256 + rights"]
  B --> C["3. 構成・台本<br/>15s beats: hook / problem / demo / afterglow / cta"]
  C --> D["4. 絵コンテ / Key Visual<br/>Blenderは構図参照のみ"]
  D --> E{"人間承認<br/>approved storyboard?"}
  E -- "no" --> D
  E -- "yes" --> F["5. プロンプトcompile<br/>CM seeds / camera / look / FP rules"]
  F --> G{"6. validator gate<br/>素材・権利・FP・文字・Blender直渡し"}
  G -- "blocked" --> C
  G -- "pass" --> H{"7. permission.json<br/>明示許可・予算上限"}
  H -- "not allowed" --> I["停止<br/>人間がpermission編集"]
  H -- "allowed" --> J["8. 生成<br/>mock first / real Seedanceは人間起動"]
  J --> K["9. レビュー<br/>採用/棄却 + failure_tag + cost"]
  K --> L["10. Production Memory<br/>generations / failure_patterns / playbooks"]
  L --> M{"再生成?"}
  M -- "yes" --> N["retry playbook<br/>プロンプト差分生成"]
  N --> F
  M -- "no" --> O["11. 後編集<br/>音声 / SFX / 字幕 / Palmier"]
  O --> P{"公開承認"}
  P -- "no" --> O
  P -- "yes" --> Q["納品・公開<br/>人間のみ"]
```

## 入力できるもの / できないもの

```mermaid
flowchart LR
  BLD["Blender previs/render"] -->|composition only| KV["photoreal storyboard / key visual"]
  BLD -. "Seedance primary input 禁止" .-> BLOCK["BLOCKED"]
  USER["rights-confirmed user asset"] --> REG["AssetRegistry"]
  KV --> APPROVE["human approval"]
  REG --> VALIDATE["validator"]
  APPROVE --> VALIDATE
  VALIDATE --> SEEDANCE["Seedance primary image / prompt"]
```

## ゲート一覧

| Gate | 目的 | 止めるもの | 証拠 |
|---|---|---|---|
| AssetRegistry | 素材の出自と権利を固定 | 権利不明、実在顔、sha不一致 | `assets/registry.jsonl` |
| Storyboard approval | 画作りの正を人間確認 | 未承認Key Visual | `approvals.jsonl` |
| Contract validator | 既知失敗を生成前に止める | FP-001〜008、Blender直渡し、文字生成依存 | `studio/core/contract_validator.py` |
| Permission | 有料生成の最終ロック | 明示許可なし、予算超過 | `permission.json` |
| Review | 出力の採用/棄却を記録 | 薄い動画の再利用 | `ProductionMemory` |

## 15秒CMの標準ビート

```mermaid
timeline
  title 15s Product Ad Beats
  0-2s : hook : 無音でも止まる商品/変化/問題
  2-5s : problem : 欲しくなる文脈や小さな課題
  5-9s : demo : 商品ビューティ/機能/変化
  9-12s : afterglow : 質感・余韻・記憶
  12-15s : cta : ブランド名/CTA/最終商品記憶
```

## 運用ルール

- Codexは有料生成・MCP実行・外部投稿をしない。
- 本番生成は人間が `permission.json` を編集してから実行する。
- 初回は完成CMではなく、1ショット4〜5秒のスモークテストだけ。
- 字幕、正確な日本語テロップ、最終タイトルは後編集。
- 失敗は `failure_tag` としてMemoryに残し、次回compile/validator/retryへ戻す。

