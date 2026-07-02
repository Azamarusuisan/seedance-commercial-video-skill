# Claude Review Request — Work Order 2 Conflict Decision

Claudeに判断してほしいことは1点だけです。

## 背景

Codexは `/Users/zettai/Downloads/CODEX-WORKORDER-2.md` の T-A / T12' / T13〜T18 を実装しました。

現在の最新状態:

- Repo: `https://github.com/Azamarusuisan/seedance-commercial-video-skill.git`
- Branch: `main`
- Latest checked commit: `171e499 Document Work Order 2 completion conflict`
- Verification:
  - `python3 -m studio.tests.run` => 27 tests OK
  - `bash studio/tests/self_audit.sh` => `SELF-AUDIT: ALL GREEN`

## 衝突している要件

Work Order 2には、同時に満たせない要件があります。

1. T-A / 前提条件:
   - `workspace/`, `references/`, `tests/fixtures/` は削除・改変禁止。
   - `studio/tests/self_audit.sh` は Studio v2導入以降に `workspace/ references tests/fixtures` へ差分があると失敗する。

2. T18:
   - v1 `workspace/ui/live-workflow.html` ほかFactoryページの先頭に固定バナー
     `V1 FROZEN — 閲覧専用。制作はStudio v2へ`
     を追記する。

CodexはT-Aを優先し、`workspace/` は改変していません。
代わりに Studio v2 UI 側へ同じ凍結バナーを表示しています。

関連ファイル:

- `docs/workorder-2-completion-audit.md`
- `studio/tests/self_audit.sh`
- `studio/ui/web/server.py`
- `studio/ui/web/app.py`

## Claudeに決めてほしいこと

以下のどちらを採用すべきか、理由付きで判断してください。

### Option A: workspace凍結を維持する

- v1 `workspace/ui/*.html` は触らない。
- T18のv1バナー要件は「Studio v2 UI側の表示で代替」と明記する。
- `self_audit.sh` は現状維持。
- 安全性・凍結不変性を優先。

### Option B: v1 UIバナーだけ例外許可する

- `workspace/ui/live-workflow.html` など必要最小限のv1 UIファイルだけに固定バナーを追記する。
- `self_audit.sh` に「v1 frozen banner だけは許可」という例外を実装する。
- 例外範囲が広がらないよう、差分内容を文字列レベルで検証する。
- ユーザーがv1画面を開いた時の誤操作防止を優先。

## 判断基準

- 有料生成・MCP実行・外部投稿は絶対に行わない。
- `workspace/` の既存制作データ、生成物、失敗ログ、状態JSONは壊さない。
- 監査可能性を優先する。
- 今後Claude/Codexが誤ってv1を制作経路として使わないことを重視する。
- 最小差分で済ませる。

## Claudeへの期待アウトプット

次の形式で返してください。

```text
Decision: Option A / Option B

Reason:
- ...

If Option A:
- Codexに追加でやらせること:
  1. ...

If Option B:
- Codexに追加でやらせること:
  1. ...
  2. ...

Do not do:
- ...
```

## 補足

Codexの現時点の判断は Option A 寄りです。
理由は、Work Order 2の最上位前提とself-auditが「workspace不変」を機械的に要求しているためです。
ただし、人間がv1 UIをまだ開く運用なら、誤操作防止のためOption Bも合理的です。
