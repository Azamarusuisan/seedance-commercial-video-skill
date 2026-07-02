# Codex Work Order — Stage 0 + P0(PLAN.md v2.0 準拠)

各タスクは 1タスク=1PR。PR descriptionに「PLAN.md §x.y」を明記。
テストなしのPRはマージ不可。実装順は本書の番号順(依存関係を成す)。

## 全PR共通の安全規則(違反したら即停止)
- 有料生成・Higgsfield/Seedance/Palmier/ElevenLabsの実行・外部投稿をタスク内で行わない。プロバイダはモックで検証する(実生成の統合テストは人間が起動)。
- `workspace/` `references/` `tests/fixtures/` の既存ファイルを削除・移動・改変しない(Stage 0の告知追記を除く)。
- APIキー・Cookie・Token・一時URL・応答生JSONをコミットしない。`studio/projects/` と応答ログはgitignore。
- 仕様と現状が食い違ったら推測で進めず、停止して差分報告。
- fail-closed: 判定不能はblocked/manual_required。バイパス用環境変数を実装しない。

---

## T0(Stage 0): v1凍結 — PLAN.md §13
- 変更: ルートの CLAUDE.md / CODEX.md / AGENTS.md / HERMES.md / OPENCREW.md 先頭に凍結告知ブロックを追記(削除はしない)。`.gitignore` に `studio/projects/` を追加。
- 追加: PLAN.md(v2.0本文)、本作業書を docs/ へ。
- 受け入れ: `rg "v1凍結|workspace/ 経路.*禁止" *.md` が5ファイルでヒット。既存ファイルの削除ゼロ(`git status` に deleted なし)。
- 注意: workspace/run/*.permission.json の値は**変更しない**(人間作業)。

## T1: スキーマ一式 — §3
- 追加: `studio/schemas/`(project / shot_contract / asset_registry_record / approvals_event / permission / bible)+ `studio/schemas/validate.py`(汎用スキーマ検証)。
- テスト: 正常系・必須欠落・型違い・不正state値の各fixture。
- 受け入れ: `pytest studio/tests/test_schemas.py` 全PASS。§3のJSON例がそのまま正常系fixtureとして通る。

## T2: Asset Registry — §3.3, §2a
- 追加: `studio/core/registry.py`(登録=sha256計算+追記、照会、sha再検証)。顔検出はまずスタブ(`real_face` を人間入力+後で検出器差し込み可能なインタフェース)。
- 規則実装: rights_status=unknown または real_face=true → seedance_upload_allowed=false を強制。blender_render の種別記録。
- 受け入れ: unknown素材を登録→upload_allowed=falseになるテスト。sha不一致検出テスト。

## T3: approvals.jsonl + `studio approve` — §3.4
- 追加: `studio/core/approvals.py`(追記専用。編集・削除APIを作らない)、CLIサブコマンド approve / revoke。
- 受け入れ: approve→照会→revoke の往復テスト。既存行の改変を試みるAPIが存在しないこと(コードレビュー項目)。target_sha256記録。

## T4: permission読み取り — §3.5
- 追加: `studio/core/permission.py`(読み取り専用。**書き込み関数を実装しない**)。
- 受け入れ: ファイル欠落・キー欠落・false・予算欄欠落の全ケースでblocked理由を返すテスト。書き込みAPI不在をテストで担保(モジュールにwrite系シンボルがないことをassert)。

## T5: Gate Engine — §4a
- 追加: `studio/core/gates.py`(G_brief〜G_publishの判定。入力はproject/contract/registry/approvals/permission)。G_publishは常にmanual_required。
- 受け入れ: 各ゲートのpass/blocked/manual_requiredを網羅するテーブル駆動テスト。上流blocked時に下流未評価。sha変更でstale approval失効。

## T6: 契約バリデータ — §4b
- 追加: `studio/core/contract_validator.py`。§4bの6項目。FP照合はまず静的ルール(図形エフェクト語リスト+Blenderロール制限+文字要求検出)で実装し、Memory接続はP1。
- 移植: v1 `workspace/scripts/validate-seedance-input.py` のBlender検出ロジックと `tests/fixtures/` を流用(コピーして使用。原本は不変)。
- 受け入れ: v1のblender fixtureがrole=identityで**必ず**落ち、role=composition+experimental=trueで通るテスト。"electric arcs" を含むactionで警告。実在顔素材参照でblocked。

## T7: 状態機械+Job Queue+予算ガード — §3.1, §5
- 追加: `studio/core/state_machine.py`(status遷移はGate Engine経由のみ)、`studio/core/jobs.py`(直列/並列、リトライ上限、冪等キー、タイムアウト)、`studio/core/budget.py`(80%警告/100%停止、日次上限)。
- 受け入れ: 冪等キー重複で二重実行されないテスト。予算100%で全ジョブ停止テスト。同一failure_tag 2回で停止テスト(§5停止則)。

## T8: Provider Adapter(モック先行)— §1, §11-3
- 追加: `studio/providers/base.py`(共通IF: estimate / generate / poll / fetch)、`mock.py`(決定的なダミー応答+ダミーmp4/png生成)、`seedance.py` / `gpt_image.py` / `elevenlabs.py` の骨格(OPEN-2確定まで実呼び出し部はNotImplemented+api-status.md)。
- 受け入れ: モックでestimate→authorize→generate→取得が通る統合テスト。実プロバイダのキー未設定時に明確なエラー。

## T9: プロンプトコンパイラ — §4 Phase D-1
- 追加: `studio/agents/compiler.py`(契約+bible → @構文プロンプト。参照上限規則§2a-4、ネガティブ既定: watermark/subtitles/captions)。
- 受け入れ: §3.2の例からゴールデンファイル一致のコンパイル結果。バリデータ不合格の契約はコンパイル拒否。

## T10: ffmpegアセンブリ — §4 Phase E
- 追加: `studio/assembly/`(結合、字幕焼き込み、-14 LUFS正規化、9:16/16:9/1:1書き出し、frame_last抽出)。
- 受け入れ: モック生成のダミーmp4群から完パケが出るテスト(ffprobeで尺・音声・解像度検証)。

## T11: CLI一気通貫 — §8
- 追加: `studio/ui/cli/`(new / status / validate / approve / estimate / generate / review / assemble / cost)。
- 受け入れ: **モックプロバイダで** `studio new → approve(①) → estimate → approve(authorize) → generate → review採用(③) → assemble → approve(④)` が1本通るE2Eテスト。permission全falseだとgenerateがblockedになるE2Eテスト。

## T12: 統合テスト(人間実施)— §12-4
- 人間がOPEN-2の経路を確定し実キーを設定、`studio new` から実生成で15〜30秒縦型広告を1本作る。記録をProduction Memory形式のJSONで保存(DB本体はP1)。
- Codexの作業: 手順書 `docs/first-run.md` の作成のみ。実行は人間。

---

## First Codex Prompt(これをそのまま貼る)

```
あなたはこのリポジトリの実装係です。ルートの PLAN.md(v2.0)と docs/CODEX-WORKORDER.md に従います。

安全規則(絶対厳守):
- 有料生成、Seedance/GPT Image/ElevenLabs/Higgsfield/Palmierの実行、外部投稿は一切しない。プロバイダ検証はモックのみ。
- workspace/ と references/ と tests/fixtures/ の既存ファイルを削除・移動・改変しない(T0の告知「追記」を除く)。
- APIキー・トークン・一時URL・応答生JSONをコミットしない。
- 仕様と現状が食い違ったら推測せず停止して報告。fail-closedで実装し、ゲートをバイパスする環境変数やフラグを作らない。

最初のタスク: まず fact-check、その後 T0 のみを実施してください。

Fact-check(結果を docs/factcheck-<日付>.md にコミット):
1. git status && git log --oneline origin/main..HEAD(ローカル先行分の有無)
2. rg --files | sort で全体像を把握
3. 次の存在確認: workspace/scripts/validate-seedance-input.py、tests/fixtures/(blender系fixture)、references/known-failure-patterns.md、ルートの CLAUDE.md/CODEX.md/AGENTS.md/HERMES.md/OPENCREW.md
4. workspace/run/*.permission.json を読み、実行系フラグの現在値を一覧化(変更はしない)

T0(1PR): PLAN.md §13 のとおり。
- 5つのエージェントMDの先頭に v1凍結告知ブロックを「追記」(既存本文は不変)
- .gitignore に studio/projects/ を追加
- PLAN.md と docs/CODEX-WORKORDER.md をコミット
受け入れ条件: rg "v1凍結" *.md が5ファイルでヒット / git status に deleted が1件もない / 追記以外の差分がない。

T0のPRを出したら停止し、fact-checkで判明した「PLAN.mdの前提との食い違い」を箇条書きで報告してください。人間の確認後に T1(schemas)へ進みます。
```
