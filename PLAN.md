# AI映像工房「Studio」実装計画書 v2.0(統合版)

対象: ショート動画(TikTok/YouTube Shorts/Reels)〜 長尺CM 〜 短編・長編映画
利用モデル: Seedance 2.0(映像+音声同時生成)/ GPT Image 2.0(静止画・キーフレーム)/ ElevenLabs(ナレーション・セリフ)
補助ツール: Blender(MCP経由・任意)/ Premiere Pro(MCP/Codex経由・任意)/ ffmpeg(既定の組み立てエンジン)
運用者: 人間1名(CLIまたはUIからボタン・指示のみ。専門知識不要)

> **v2.0の由来**: v1.0(fable作成の最終構想)に、既存リポジトリ
> (seedance-commercial-video-skill)の実地監査で得た安全設計
> (fail-closedゲート、承認台帳、権利管理、既知失敗パターンFP-001〜008)を
> 統合したもの。各PRは本書の節番号に紐づける(§14)。
> 「OPEN-n」と記した項目は人間の回答待ち。回答が来るまで安全側の既定値で実装する。

---

## 0. 設計原則(全実装がこれに従う)

1. **人間は「発注者」と「審査員」だけをやる。** ブリーフを出す、候補を見て選ぶ/差し戻す。それ以外の全工程はエージェントが行う。
2. **状態が唯一の真実(State is the source of truth)。** すべてのプロジェクトは `project.json` と生成物ディレクトリで完全に再現可能。エージェントの「記憶」やドキュメント追記に依存しない。途中でプロセスが死んでも同じ場所から再開できる。
3. **契約駆動(Contract-first)。** 各ショットは生成前に「ショット契約(Shot Contract)」で定義され、生成物は契約に対して自動採点される。プロンプトは契約から機械的にコンパイルされる成果物であり、手書きの一点物ではない。
4. **fail-closed。** 判定材料が欠けている・矛盾している・スキーマ違反である場合、システムは常に「止まる」側に倒す。推測で先へ進む実装を書いてはならない。曖昧なら `manual_required` として人間に出す。
5. **有料実行の三条件。** 課金を伴うAPI呼び出しは (a) 対象ショット契約が `approved`、(b) permission.json の該当executeキーが `true`、(c) 予算残がある、の3条件をrunnerが機械検証した場合にのみ発生する。環境変数1個(旧 `APPROVED=1` 方式)では絶対に突破できない。
6. **承認は追記専用の台帳(approvals.jsonl)に記録される。** 各所のフラグはすべて台帳からの派生物。派生物を手で書き換える運用を禁止する。承認後に対象ファイルのハッシュが変わったら承認は自動失効する。
7. **採用フッテージ起点の連鎖。** 長尺は計画上のプロンプトを機械的に延長しない。クリップNが承認されたら、その実際の最終フレームと実際に起きた内容を記録し、クリップN+1はそこから書く。
8. **全生成を学習材料として記録する。** 成功も失敗も、プロンプト・参照・パラメータ・スコア・人間の裁定込みでProduction Memoryに保存。旧リポジトリの既知失敗パターン(FP-001〜008)を初期データとして取り込む(§7)。
9. **コストは常にガードされる。** プロジェクト単位・日単位の生成予算上限。上限接近で自動停止し人間に通知。全API呼び出しは冪等キー付きで二重課金を防ぐ。
10. **既定はffmpeg、プロツールは特殊効果専用。** Blender/Premiereは「その工程でしか出せない価値」がある場合のみ呼ばれるオプション工程。パイプラインの必須経路に置かない。
11. **UIはstateのread-only projection。** UIは状態を作らず、映すだけ。UIから発生する書き込みは「承認イベントの発行」と「ブリーフ入力」のみで、いずれもコアのコマンドを経由する。

---

## 1. 全体アーキテクチャ

```
┌────────────────────────────────────────────────────┐
│  UI層: CLI (studio コマンド) / Web UI (レビュー画面)   │
└────────────────┬───────────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────────┐
│  Orchestrator(監督エージェント)                      │
│  - プロジェクト状態機械の遷移管理                       │
│  - 各専門エージェントへのタスク発行                     │
│  - 予算・リトライ・承認ゲート制御(§4a ゲートエンジン)   │
└──┬──────┬──────┬──────┬──────┬──────┬──────────────┘
   │      │      │      │      │      │
 脚本   絵コンテ  素材   映像   音声   編集
 Agent  Agent   Agent  Agent  Agent  Agent
 (LLM)  (LLM+   (GPT   (Seed  (11    (ffmpeg/
        GPTImg) Image) ance)  Labs)  Blender/PPro)
   │      │      │      │      │      │
┌──▼──────▼──────▼──────▼──────▼──────▼──────────────┐
│  基盤サービス                                        │
│  - Gate Engine(承認台帳・permission・予算の機械検証)   │
│  - Job Queue(直列/並列実行、リトライ、タイムアウト、    │
│    冪等キー)                                         │
│  - Asset Registry(全素材のハッシュ・権利・来歴管理)    │
│  - Production Memory(学習DB: SQLite + ベクトル検索)   │
│  - Provider Adapter(Seedance/GPT Image/11Labsの      │
│    API差異を吸収。提供面を切替可能に)                   │
│  - QC Engine(技術検査 + VLM審美評価)                  │
└────────────────────────────────────────────────────┘
```

技術選定: Python に統一(旧リポジトリのvalidateロジック移植が容易なため)。DBはSQLite+ローカル完結の埋め込み検索。サーバー常駐不要、CLI起動で全部動く。Web UIはレビュー専用の軽量なもの(FastAPI + 静的HTML)。

### 1a. リポジトリ方針(v1との関係)

- **同一リポジトリで続行する。** ルートに `studio/`(v2、本計画の実装)を新設。既存 `workspace/`(v1)は**凍結**し、読み取り専用の遺産+学習ソースとして保持する。
- 凍結の意味: v1の生成画像・状態JSON・ログ・失敗記録・fixturesは**一切削除・移動・改変しない**。v1経路(workspace/scripts/*)での**新規有料生成を禁止**する(§13 Stage 0)。
- v1から昇格して使い続けるもの: `references/known-failure-patterns.md`(FP台帳の正)、tests/fixtures、cast/brand情報(Asset Registryへ変換登録)。
- OPEN-1: v2稼働までの間にv1で生成を継続する必要があるか。**既定=継続しない(完全凍結)。** 継続する場合のみ、監査書P0(Palmier経路ゲート化・validate fail-closed化)をv1に先行適用する。

---

## 2. モデル・ツールの役割マトリクス(曖昧さ排除)

| 工程 | 担当 | 何をする | 何をさせない |
|---|---|---|---|
| 企画・脚本・ショット分割 | LLM(監督Agent) | ブリーフ→脚本→ショット契約群 | 映像生成プロンプトの直書き(契約からコンパイル) |
| キャラ・商品・世界観の参照画像 | GPT Image 2.0 | キャラシート、商品ヒーローカット、キーフレーム、ファースト/ラストフレーム | 動画そのもの |
| 映像+同期音声 | Seedance 2.0 | 1クリップ4〜15秒。参照は画像最大9・動画最大3・音声最大3(計12)を@構文でロール指定。セリフのリップシンクはここ | 15秒超の一発生成/ナレーション主担当/**映像内の正確な文字表示(テロップ・法定表記・ロゴ内文字はポスプロで焼く)** |
| ナレーション・セリフ音声(独立トラック) | ElevenLabs | VO、キャラボイスの統一、多言語展開 | BGM |
| 組み立て・テロップ・書き出し | ffmpeg(既定) | 結合、字幕焼き込み、ラウドネス正規化、縦横比別書き出し | — |
| 3D・特殊ショット | Blender MCP(任意) | 商品3Dターンテーブル、ロゴアニメ、Seedance参照用素材 | 通常ショットの制作 |
| 人間の最終仕上げ | Premiere Pro(任意) | OTIO/FCP XML書き出しの受け皿 | 自動処理の必須経路 |

**Premiereに関する立場**: 既定経路は「ffmpegで完パケ」。Premiereはタイムライン書き出し先に留める。これで「猿でもできる」と「プロが触れる」を両立する。

### 2a. 参照ロール規則(v1の実弾失敗から昇格した安全規則)

Shot Contractの各参照スロットには `role` を必須で宣言する。役割は `identity / product / style / composition / first_frame / last_frame / motion / audio` のいずれか。Registryの `asset_kind` と `role` の組み合わせでバリデータが機械判定する:

1. **Blenderレンダー・ビューポートは `role=composition` または `motion`(参照動画)のみ許可。** `identity / style / first_frame` への割り当ては**恒久禁止**(FP-002: CG質感が最終映像を汚染した実績)。composition利用も当面は `experimental: true` フラグ必須とし、結果をProduction Memoryで検証してから常設化を判断する。
2. **実在人物の顔を含む素材は参照アップロード禁止。** Registry登録時に顔検出を行い、`real_face: true` の素材は `seedance_upload_allowed=false` に固定する(モデル側も2026年2月以降実在顔を拒否するため、事前に工場側で止める)。人物が必要な場合はGPT Image 2.0で架空人物のキャラシートを生成し、それをidentity参照にする(キャラクターバイブル方式)。プリセット仮想人物(asset://ID)対応はアダプタのオプション。
3. **権利不明素材(`rights_status: unknown`)は参照にもタイムラインにも入れない。** 参照素材は自作・権利クリア済み・AI生成のみ(v1のG3/G10ルールを継承)。
4. **参照は最大12スロットだが、既定コンパイラは画像3〜5+動画0〜2に制限する。** 全スロット使用は制約過多で品質が落ちるため、超過はプレイブックの根拠がある場合のみ。

---

## 3. データモデル(Codexに最初に実装させるもの)

### 3.1 project.json(プロジェクト状態機械)
```json
{
  "id": "prj_20260702_001",
  "type": "short_ad | long_ad | short_film | feature_film",
  "status": "briefing | scripting | preproduction | production | assembly | qc | review | published | archived",
  "brief": { "product": "...", "target": "...", "platform": ["tiktok","youtube"],
             "duration_sec": 30, "aspect": "9:16", "language": "ja",
             "must_include": [], "must_avoid": [], "reference_urls": [] },
  "budget": { "cap_usd": 20, "daily_cap_usd": 10, "spent_usd": 7.42, "generations": 14 },
  "audio_policy": { "dialogue": "seedance_native", "narration": "elevenlabs", "bgm": "licensed_track | seedance_native" },
  "bible_ref": "bible.json",
  "shots": ["shot_001", "shot_002"],
  "timeline": "timeline.json",
  "created_at": "...", "updated_at": "..."
}
```
`status` の遷移はGate Engineのみが行う(§4a)。手書き変更はバリデーションで検出し拒否する。

### 3.2 ショット契約(shot_XXX/contract.json)— 本システムの心臓部
```json
{
  "shot_id": "shot_003",
  "narrative_function": "商品の使用シーン。前ショットの疑問に答える",
  "duration_sec": 8,
  "continuity": {
    "starts_from": "shot_002/takes/take_004/frame_last.png",
    "characters_present": ["char_A"],
    "props_state": { "コーヒーカップ": "半分減っている" },
    "time_of_day": "朝", "location": "loc_kitchen"
  },
  "camera": "slow dolly-in, eye level, 35mm相当",
  "action": "char_Aがカップを置き、カメラに笑いかける",
  "audio": { "dialogue": [{"char":"char_A","line":"これ、ほんとに楽。"}],
             "vo": null, "bgm_policy": "前ショットから継続", "sfx": ["カップを置く音"] },
  "references": [
    {"slot":"@Image1","asset_id":"reg_0142","role":"identity"},
    {"slot":"@Image2","asset_id":"reg_0087","role":"style"},
    {"slot":"@Image3","asset_id":"reg_0201","role":"first_frame"}
  ],
  "acceptance_criteria": [
    "char_Aの顔・服装が参照と一致", "商品ロゴが判読可能",
    "口の動きがセリフと同期", "ウォーターマーク・字幕の混入なし"
  ],
  "state": "draft | validated | approved | estimating | authorized | generating | evaluating | needs_retry | accepted | rejected",
  "takes": [ { "take": 1, "prompt_compiled": "...", "provider": "...",
               "idempotency_key": "...", "cost_usd": 0.9, "qc_score": {},
               "human_verdict": "rejected", "failure_tags": ["face_drift"],
               "video": "take_001.mp4" } ]
}
```
v1.0からの変更点: `references[].asset` の生パス指定を廃止し、**Asset Registryの `asset_id` 参照に統一**(承認・権利・顔チェック済みの素材しか指せない)。`state` に `validated / approved / estimating / authorized` を追加(ゲート状態機械、§4a)。

### 3.3 Asset Registry(assets/registry.jsonl)— v1のasset-manifestの後継
1素材=1レコードの追記型JSONL+実ファイル。必須フィールド:
```json
{ "asset_id": "reg_0142", "path": "assets/char_A/sheet_front.png",
  "sha256": "...", "asset_kind": "generated_charsheet | product_photo | brand_asset | blender_render | adopted_frame | audio | external_licensed",
  "origin": { "provider": "gpt-image-2.0", "prompt_ref": "...", "imported_from": null },
  "rights_status": "company_owned | ai_generated | licensed | unknown",
  "real_face": false,
  "seedance_upload_allowed": true,
  "registered_at": "..." }
```
規則: `rights_status=unknown` または `real_face=true` は登録時に自動で `seedance_upload_allowed=false`。`blender_render` は §2a-1 のロール制限が適用される。sha256はRegistryが唯一の照合点(契約承認後に実体が変わったら承認失効)。

### 3.4 approvals.jsonl(人間判断の台帳、追記専用)
```json
{ "at": "...", "gate": "G3_storyboard", "project": "prj_...", "target": "shot_003",
  "target_sha256": "...", "verdict": "approved | rejected | revoked",
  "by": "human", "note": "コマ4のカメラを寄りに", "event_id": "apv_00031" }
```
書き込みは `studio approve` コマンドのみ。**過去行の編集・削除は禁止**(取り消しはrevokedイベントの追記)。契約やproject.jsonの承認系フラグはすべて本台帳からGate Engineが導出する。

### 3.5 permission.json(有料実行ゲート、人間のみ編集)
```json
{ "project": "prj_...",
  "execute": { "gpt_image": true, "seedance_estimate": true,
               "seedance_generate": false, "elevenlabs": false,
               "palmier_or_upscale": false, "publish": false },
  "budget": { "cap_usd": 20, "daily_cap_usd": 10, "max_takes_per_shot": 3, "max_parallel": 2 },
  "edited_by": "human_only" }
```
エージェント・スクリプトはこのファイルを**読むだけ**。書き込みをコードから行った時点でバグとして扱う(テストで監視)。`publish` は恒久的に人間承認+手動操作(§4 Phase F)。

### 3.6 作品バイブル(bible.json)— 長尺の一貫性の要
キャラクター(参照画像セット=Registry asset_id群、声のID=ElevenLabs voice_id、話し方、禁止事項)、ロケーション、小道具、カラーグレード、アスペクト比、テロップのフォント・スタイル、ブランド規定(ロゴ使用ルール、NG表現、法定表記の要否)を一元定義。**全ショット契約はバイブルを参照してコンパイルされる。** キャラクターは§2a-2に従い全員「AI生成の架空人物」として定義する。映画モードではこれに加えて幕構成・シーンリスト・感情曲線を持つ `screenplay.json` を上位に置く。

### 3.7 Production Memory(学習DB)
```
generations(id, project_id, shot_id, take, model, provider,
            prompt_text, reference_manifest, params,
            qc_scores_json, human_verdict, failure_tags,
            cost_usd, latency_sec, created_at)
playbooks(id, situation, recipe, evidence_generation_ids, win_rate, updated_at)
failure_patterns(fp_id, title, trigger, rule, origin, status)   -- FP台帳(§7)
platform_results(project_id, platform, views, avg_watch_time,
                 completion_rate, likes, posted_at, fetched_at)
embeddings(generation_id, vector)
```
`failure_patterns` はv1の `references/known-failure-patterns.md`(FP-001〜008)を初期データとして取り込み、**FP採番はこのテーブルが唯一の台帳**とする。候補は `status=candidate` で入り、人間承認で `active` に昇格する。

---

## 4. パイプライン詳細(状態機械)

### Phase A: ブリーフィング(人間の唯一の入力)
CLI: `studio new` → 対話で6問だけ聞く(何の動画/長さ/プラットフォーム/雰囲気/絶対入れるもの/予算)。または `studio new --brief brief.yaml`。**おじいさんモード**: Web UIで「商品写真をドロップ→3つの質問に答える→作成ボタン」。ドロップされた写真はその場でRegistry登録(顔検出・権利質問1つ付き)。

### Phase B: 企画・脚本(監督Agent)
1. Production Memoryから類似ブリーフの成功事例を検索し、勝ちパターンを取り込む(初回はFP台帳の禁止則のみ適用)
2. プラットフォーム別の設計規則を適用(TikTok: 冒頭2秒のフック必須、9:16、テロップ大きめ、15〜34秒 / YouTube: 16:9 or Shorts 9:16)
3. 脚本 → ショット分割 → 各ショット契約のドラフト生成 → **契約バリデータ**(§4b)を通過したもののみ提示可能
4. **承認ゲート①(G_storyboard)**: 絵コンテ(GPT Image 2.0で各ショット1枚のキーフレーム)+脚本を人間に提示。「OK / このコマを直せ / 全部やり直し」の3択。OKは `studio approve` でapprovals.jsonlに記録

### Phase C: プリプロダクション(素材Agent)
- バイブルに基づきキャラシート(正面・側面・表情)、商品ヒーローカット、ロケーションプレートをGPT Image 2.0で生成し、**全件Registry登録**(sha256・origin・rights自動記入)
- 必要ならBlender MCPで3D素材をレンダリングし、`asset_kind=blender_render` として登録(§2a-1のロール制限が自動適用)
- ElevenLabsでキャラごとのvoice_idを確定し、テスト音声を人間が一度だけ確認(**承認ゲート②(G_voice)、任意**)

### Phase D: プロダクション(映像Agent)— コアループ
各ショットについて:
1. 契約(state=approved) → プロンプトコンパイル(@構文、タイムスタンプ分解、ネガティブ指定、Memoryからのfew-shot注入)
2. **コスト見積 → 予算検証 → state=authorized**(permission.execute.seedance_generate=true かつ予算残ありの場合のみ。§0-5の三条件)
3. Seedance 2.0で生成(既定1テイク。予算に余裕があればN=2並列。冪等キー必須)
4. **自動QC**(§6)でスコアリング → 閾値未満は failure_tag を付けて自動リトライ(プレイブック経由の修正。max_takes_per_shot上限)
5. 閾値以上のテイクを人間に提示(**承認ゲート③(G_take)**: 「採用/リトライ/契約修正」)
6. 採用時: 最終フレームを抽出し `frame_last.png` をRegistry登録(`asset_kind=adopted_frame`)、「実際に起きたこと」をVLMで記述して継続性台帳に記録 → 次ショットの契約を実績ベースで確定

### Phase E: アセンブリ(編集Agent)
1. ffmpegで結合(トランジション、リタイム)
2. ナレーション(ElevenLabs)を敷き、Seedanceネイティブ音声とダッキング処理でミックス
3. テロップ・字幕焼き込み(バイブルのスタイル定義、libass。**映像内文字はすべてここで焼く**)
4. ラウドネス正規化(配信向け -14 LUFS 基準)
5. プラットフォーム別に書き出し(9:16 / 16:9 / 1:1)
6. 任意: OTIO/FCP XMLでタイムライン書き出し(Premiere受け皿)

### Phase F: 最終QCと公開
- 全編の自動QC(音切れ、黒フレーム、ロゴ判読、禁止表現、権利unknown素材の混入スキャン)
- **承認ゲート④(G_final)**: 完パケを人間が視聴して承認
- **公開は恒久的に手動**(permission.execute.publish は本計画の全フェーズでfalse固定)。将来の自動投稿(P5)は本書の改訂と人間の明示判断を経てのみ解禁

### 長尺・映画モード(type = short_film / feature_film)
- 上位に `screenplay.json`(幕→シーケンス→シーン→ショット)を持つ階層分解。シーン単位でPhase D〜Eを回す
- 継続性台帳(continuity ledger)がシーンをまたいで衣装・小道具・時間帯・傷やメイク等を追跡
- シーン単位ダイジェストでレビュー(ショット単位承認は映画では破綻する)
- 音楽は別途音楽素材の管理レイヤ(ライセンス管理必須、Registryの `external_licensed` で権利追跡)

### 4a. ゲートエンジン仕様(v1監査のG1〜G14をv2状態機械に写像)

判定はGate Engineのみが行い、結果を project.json / contract.json のstateに反映する。**判定材料の欠損は常に blocked または manual_required**。UIはこの結果を表示するだけ。

| ゲート | 対象 | pass条件 | blocked時のUI文言(例) |
|---|---|---|---|
| G_brief | project | brief必須項目が埋まり人間が確定 | 「ブリーフが未確定です」 |
| G_assets | shot | 全参照がRegistry登録済み+sha256一致 | 「未登録の参照素材があります」 |
| G_rights | shot | 全参照が rights_status≠unknown かつ real_face=false | 「権利不明/実在顔の素材は使えません: <id>」 |
| G_storyboard | shot群 | 絵コンテ+契約に人間approvedイベント | 「絵コンテが承認待ちです」 |
| G_voice | project | (任意)voice確定イベント | — |
| G_estimate | shot | 見積記録あり+予算cap内 | 「見積未実施/予算超過」 |
| G_authorize | shot | approvals台帳のG_take前提+permission.execute.seedance_generate=true+予算残 | 「最終生成許可がありません(人間の承認が必要)」 |
| G_take | take | QC閾値超え+人間の採用イベント | 「テイクが採用待ちです」 |
| G_final | project | 完パケの人間承認イベント | 「最終確認が未実施です」 |
| G_publish | project | **常にmanual。自動passなし** | 「公開は本システムの外で人間が行います」 |

共通規則: 上流ゲート未passなら下流は評価しない。承認済み対象のsha256が変わったら該当承認は自動失効(stale approval)。

### 4b. 契約バリデータ(v1 validate-seedance-input.pyの後継。fail-closed)

生成リクエストのコンパイル前に必ず実行され、以下を機械検証する:
1. スキーマ適合(必須項目・型・state遷移の正当性)
2. 全 `references[].asset_id` がRegistryに存在し `seedance_upload_allowed=true`
3. §2a のロール規則(blender_render → composition/motionのみ、実在顔ゼロ、権利unknownゼロ)
4. 参照スロット数の上限(9/3/3)と既定制限(§2a-4)
5. FP台帳との照合(§7の生成前チェック): 図形的エフェクト語(arc/bolt/spark/beam/ray/streak/orb等+可算図形名詞×発光文脈の原則警告)、映像内の正確な文字要求の混入、その他activeなFPルール
6. 尺(4〜15秒)・解像度・アスペクトのモデル制約
不合格は理由付きでblocked。**バイパス用の環境変数は実装しない。**

---

## 5. リトライ・コスト制御

- リトライ方針: failure_tag → 対策の対応表(プレイブック)を必ず経由。例: `face_drift` → identity参照を1枚追加+preserve identity指定 / `motion_chaos` → アクション記述を1動作に減らす / `text_artifact` → ネガティブに watermark, subtitles, captions を追加
- **停止則(v1の実弾教訓を統合)**: 同一ショットで同じfailure_tagのreject 2回 → そのショットを自動停止し人間へ(プロンプト微修正の堂々巡り防止)。同一ショット3テイク失敗 → 契約自体を疑い停止。同一コンセプト(類似契約)で3プロジェクト連続失敗 → コンセプト再検討をmanual_requiredに
- 予算: プロジェクト上限・1日上限の二重ガード。80%到達で警告、100%で全ジョブ停止
- すべてのAPI呼び出しは冪等キー付きで記録し、二重課金を防ぐ。応答の生JSON・一時URL・トークンはgit管理外(ローカルログのみ)

## 6. 品質管理(QC Engine)

**技術QC(決定的・無料)**: ffprobeで解像度/fps/尺/音声トラック検査、黒フレーム・フリーズ検出、ラウドネス測定、最終フレーム抽出。

**審美QC(VLMベース)**: フレームサンプリングし、VLMに契約のacceptance_criteriaをルーブリックとして採点させる(各基準0-5点+根拠)。人物同一性は参照画像とのペア比較。**VLM採点は人間裁定と定期的に突き合わせて較正する**(§7-4)。閾値は「人間に見せる価値があるか」のフィルタであって最終判断ではない。

## 7. 学習ループ(Production Memory)— 本システムの差別化点

1. **記録**: 全テイクを§3.7スキーマで保存。人間の採用/棄却と理由(ワンタップでfailure_tag選択)が教師信号。**プロセス起因の失敗(UI誤解・ドキュメント誤読・運用ミス)も `category=process` として同じ台帳に記録する**(v1のFP-007/008型の失敗を映像失敗と同格に扱う)
2. **検索**: 新しい契約の埋め込みで類似の過去成功テイクを検索し、プロンプト構造・参照構成をコンパイラに注入(few-shot)
3. **蒸留**: 週次バッチ(`studio learn`)でLLMが直近テイクを分析しプレイブック更新(証拠ID付き)
4. **較正**: VLM採点と人間裁定の不一致事例を集め、採点プロンプトを更新
5. **実績還流**: 公開後のTikTok/YouTube指標(視聴維持率・完了率)を取り込み、承認済み作品内の優劣を学習
6. **過去資産の取り込み**: `studio import <path>` で旧リポジトリ(workspace/、references/)のプロンプト・生成物・失敗記録を遡及登録。**FP-001〜008は最初のimportで `failure_patterns` テーブルへ移し、契約バリデータ(§4b-5)が即日参照する**
7. **昇格規則**: 新失敗はまず `candidate`。人間承認(approvals.jsonlイベント)で `active` 昇格し、バリデータ・プレイブックに効き始める。candidateのまま同型が3回起きたら昇格提案を自動発行

## 8. UI仕様

**CLI**(開発者): `studio new / status / validate / approve / estimate / generate / review / retry <shot> / assemble / learn / import / cost`
**Web UI**(おじいさんモード): ①作る(写真ドロップ+3質問)②見る(承認ゲートのカード表示、採用/やり直しの2ボタン)③できたのを保存 — の3画面のみ。専門用語を出さない。**全表示はproject.json等からの導出で、UI独自の状態ファイルを持たない**(v1の手書きUI stateの反省)。デモ/プレースホルダ表示には必ず「DEMO」バッジ。

## 9. リポジトリ構成(Codexへの発注単位)

```
(既存ルート)
├── PLAN.md                  # 本書。全PRが節番号を紐づける
├── references/              # v1由来のFP台帳ほか(削除禁止、importの原本)
├── workspace/               # v1(凍結。読み取り専用の遺産)
├── tests/                   # v1 fixtures(流用)+ v2テスト
└── studio/                  # v2本体
    ├── core/                # 状態機械、Gate Engine、Job Queue、予算ガード
    ├── agents/              # director, storyboard, asset, video, voice, editor
    ├── providers/           # seedance, gpt_image, elevenlabs の各Adapter(+mock)
    ├── qc/                  # technical.py, aesthetic.py
    ├── memory/              # production_memory.py, playbooks, embeddings, import_v1.py
    ├── assembly/            # ffmpeg_pipeline, subtitles, loudness, otio_export
    ├── integrations/        # blender_mcp, premiere_export(任意層)
    ├── ui/                  # cli/, web/
    ├── schemas/             # 全JSONスキーマ(§3)。最初の実装物
    └── projects/            # 実プロジェクトデータ(gitignore。生JSON応答・一時URLも不追跡)
```

## 10. フェーズ計画(各フェーズ単体で価値が出る)

- **Stage 0(即日)**: v1凍結+安全宣言(§13)。PLAN.mdコミット
- **P0(2週間相当)**: schemas + Gate Engine + 状態機械 + アダプタ(モック込み)+ ffmpeg組み立て + CLI。**課金ゼロのdry-runで契約→承認→模擬生成→組み立てが一気通貫**した後、実プロバイダで15〜30秒縦型広告1本
- **P1**: QC Engine(技術+VLM)+ リトライプレイブック + Production Memory記録開始 + v1 import + Web UIレビュー画面
- **P2**: 学習ループ稼働(studio learn、類似検索注入、較正)+ プラットフォーム実績取り込み
- **P3**: 長尺モード(screenplay階層、継続性台帳、シーン単位レビュー)→ 3〜10分の短編
- **P4**: 映画モード(音楽ライセンス管理、章単位並列化、Blender/Premiere連携本格化)
- **P5**: 自動公開・A/Bテスト(本書改訂+人間の明示解禁が前提)

## 11. リスク台帳

1. **実在人物の顔**: モデル側が実在顔参照を拒否する。工場側でもRegistry登録時に検出・封鎖(§2a-2)。実在人物・有名人の顔を使う機能は作らない
2. **IP・著作権**: 参照素材は自作・権利クリア済み・AI生成のみをバリデーションで強制(§2a-3)
3. **プロバイダ依存・APIベータ**: Seedance提供面は仕様・価格・制約が頻繁に変わり、API直はベータ品質。Adapter層で吸収し、検証日付付きの `providers/api-status.md` を保守。**アダプタのモックを先に作り、コアはモックで完成させる**
4. **コスト暴走**: §5二重ガード+冪等キーは省略不可。リトライ無限化が最大の破産要因
5. **Premiere/Blender自動化の脆さ**: 主経路に置かない。落ちても本体は完走する
6. **VLM採点の過信**: 較正を怠ると「機械が良いと言った駄作」を量産する
7. **一人開発の継続性**: §12。前回の実際の死因である可能性が最も高い
8. **手動同期の再発(v1の死因)**: 状態のコピーを2箇所に持った瞬間に負ける。派生はすべてコードが作る。「ドキュメントに追記して運用でカバー」を発見したらそれ自体をprocess failureとして記録する
9. **MCP直呼びの残余リスク**: エージェントがアダプタを迂回してMCPツールを直接叩く経路は、リポジトリ内だけでは100%封じられない。permission検証+冪等キー台帳との突合で逸脱を検出可能にし、**最終防壁はMCPホスト側のツールallowlist**(有料実行系ツールはStudioのrunnerセッションにのみ許可する運用を推奨)

## 12. Codexへの発注方法(前回の失敗を繰り返さないために)

1. **1タスク=1PR=数百行以内**。「パイプライン作って」ではなく「schemas/shot_contract のバリデータとテストを書け」の粒度
2. **全タスクに受け入れ条件と自動テストを必須化**。テストが通らないPRはマージしない。プロバイダAdapterはモック応答のテストを先に書く
3. **schemas → core(Gate Engine含む)→ providers(mock)→ assembly → agents → qc → memory → ui の順**。UIから作り始めない
4. **毎フェーズ末に「実際に1本動画を作る」統合テスト**を人間が実施し、その記録をProduction Memoryに入れる
5. 本書を `PLAN.md` として置き、各PRのdescriptionに実装した節番号を明記(計画と実装の乖離を機械検出)
6. **安全規則(全PR共通)**: 有料生成・外部投稿はCodexのタスク内で実行しない(統合テストの実生成は人間が起動する)。既存 `workspace/` `references/` の削除・改変禁止。APIキー・トークン・一時URLのコミット禁止。前提と実コードが食い違ったら停止して報告
7. 着手前fact-check必須: `git status` / `git log origin/main..HEAD` / `rg --files` で現状を確認してから書く

## 13. Stage 0: v1凍結宣言(最初のPR)

1. ルートの CLAUDE.md / CODEX.md / AGENTS.md / HERMES.md / OPENCREW.md の先頭に凍結告知を追記: 「workspace/ 経路(v1)での新規有料生成・MCP実行を禁止する。v2(studio/)がPLAN.mdに従い後継する。v1の全ファイルは学習資産として保存され、削除・改変禁止」
2. workspace/run/ 配下の全permission manifestの実行系フラグを人間がfalseに設定(人間作業。Codexは変更しない)
3. PLAN.md(本書)をコミット
4. OPEN-1が「v1で生成継続」の場合のみ: 監査書P0(Palmierゲート・validate fail-closed)をv1に先行適用する追加PRを起こす

## 14. OPEN項目(人間の回答待ち。回答までの既定値で実装)

- **OPEN-1**: v2完成までv1で生成するか → 既定: しない(完全凍結)
- **OPEN-2**: Seedanceのアクセス経路(WaveSpeed / fal / BytePlus / Dreamina / Higgsfield継続)と月予算 → 既定: アダプタはmock+1実装(経路確定後に差し込み)。budget既定値 cap_usd=20/プロジェクト、daily=10
- **OPEN-3**: 人物が出るCMを作るか → 既定: 作る前提でキャラクターバイブル(架空人物方式)をP0スキーマに含める(実装コスト小)
- **OPEN-4**: 「パリみあプロ」=Premiere Proとして扱う(相違があれば訂正を)

---
*v2.0 — 2026-07-02。v1.0(fable)+ 既存リポジトリ監査(Claude)の統合版。*
