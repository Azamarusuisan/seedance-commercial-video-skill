# CM/クリエイティブ制作 知識ベース

## これは何か

Seedance/GPT Image/Blenderへの指示が「なんとなく」になり、出力が毎回運任せ(ガチャ)になっている問題への対応。実際のCM映像・広告素材そのものはスクレイピングしない(著作権リスク、`references/higgsfield-mcp-demo-patterns.md`の既存方針と同じ)。代わりに、**著作権の対象にならない業界の一般的な制作原則**を言語化してここに蓄積し、プロンプトを書く前に必ず参照する。

`references/known-failure-patterns.md`との違い:
- `known-failure-patterns.md` = 実際に失敗した記録(事後・反応的)
- このファイル = 良い映像を作るための一般原則(事前・能動的)

両方を、プロンプトを書く前に参照する。

## 1. 構成の型(Structure)

### 尺別のビート配分

| 尺 | 配分の目安 |
|---|---|
| 15秒 | フック 0-3s / 価値提示 3-8s / 利用・証拠 8-12s / CTA 12-15s |
| 30秒 | フック 0-3s / 世界観確立 3-8s / 価値・利用シーン 8-22s / CTA 22-30s |
| 60秒 | フック 0-5s / 展開(起承転結) 5-50s / CTA 50-60s |

- **フックは最初の2-3秒で成立させる**。無音でも伝わる視覚的フック(顔、製品、コントラスト、意外性)を最優先にする。
- CTAは最後に置くが、「静かな余韻で終える」か「強く訴求して終える」かはブランドトーンで決める(高級ブランドは前者、直販/DRは後者)。
- **業界実測値(公開情報、2026-07-01調査): 30秒スポットのストーリーボードは通常8〜12パネル(8〜15キーフレーム)。平均カット長は2-3秒(30秒なら10-15カット)。ジャンルによりさらに短く(車のCMで0.9秒)/長く(製薬CMで3秒)なる。** カット数を決めるとき、この実測値をベースラインにする(ソース: Boords/StudioBinder等の広告制作解説サイト、構造の言及のみ、実映像はコピーしない)。

### 物語型(短編/story-scene)

- 起承転結、または「日常→異変→対応→変化後の日常」の型を使う。
- 複数ショットをまたぐ場合、各ショットの終わりが次のショットへの動機になっているか確認する(`references/tiktok-story-cast-workflow.md`の「継続的な因果関係」の原則と同じ)。

## 2. ショットの文法(Shot Grammar)

| ショットタイプ | 伝わること | 使い所 |
|---|---|---|
| 確立ショット(Establishing) | 場所・世界観 | 導入、シーン転換 |
| ヒーローショット(Hero) | 製品/主役の存在感 | クライマックス、CTA直前 |
| マクロ/ディテール(Macro) | 質感・信頼性・高級感 | 製品の説得力を作る中盤 |
| リアクション/カットアウェイ | 感情・証拠 | 利用シーン、体験の裏付け |
| POV/ハンドヘルド | 当事者性・リアリティ | UGC、体験談、カジュアルな訴求 |

### カメラワークが伝える感情

- **ゆっくりとしたプッシュイン**: 親密さ、重要な瞬間への集中
- **オービット(回り込み)**: 製品の全方位的な説得力、商品ショーケース
- **ロックオフ(固定)**: 静けさ、高級感、信頼感
- **ハンドヘルド/揺れ**: リアリティ、UGC感、親近感
- **速いカット/ズーム**: エネルギー、若さ、緊急性

高級ブランドCM(例: 化粧品)は「ロックオフ+ゆっくりプッシュイン+オービット」の組み合わせが多く、UGC/TikTok系は「ハンドヘルド+速いカット」が多い。**用途(video_use_case)に合わせてカメラワークの語彙を変える。**

## 3. 光と色(Lighting & Color)

### ムード別ライティング

| ムード | ライティングの型 |
|---|---|
| 高級感/静けさ | ロー・キー(暗め)、リムライト、限定的な光源、コントラスト強め |
| 親しみやすさ/日常 | ハイ・キー(明るめ)、柔らかい拡散光、影を弱める |
| 信頼性/企業/BtoB | 均一で柔らかい光、青白系の色温度 |
| エネルギー/若さ | 高コントラスト、彩度の高い色、時にネオン/カラーライト |

### 高級化粧品・香水プロダクトの具体技法(公開情報、2026-07-01調査)

- **バックライト(逆光)**: 透明/半透明の容器(香水瓶等)を内側から光らせ、輪郭・液体の色・ガラスの反射を強調する。「内側から光る」感覚が高級感を生む。
- **グラデーションライト**: 強さの違う複数のバックライトを組み合わせ、透明な被写体に光のグラデーションを作ると奥行きが出る。
- **コントラスト比**: 一般的な美容系ビジュアルはコントラスト比2:1程度(柔らかい)。ドラマチックな高級路線は4:1〜5:1以上(影をしっかり作る)。
- **ビューティーディッシュ**: ソフトボックスよりやや硬めで、かつ均一に回り込む光質。美容/化粧品の定番光源。
- **反射コントロール**: ガラス・金属パッケージの反射を制御するため、ディフュージョンテント・偏光フィルター・黒フラグ(反射除去板)を使う。プロンプトでは「controlled reflections」「no harsh hotspots」のように書くと近い効果を狙える。
- ソース: 製品/コスメ撮影解説記事(cybertizemedia, skylum等)。技法名・原則のみの引用、画像はコピーしない。

### 色調戦略

- 使う色数を絞る(高級感なら1-2色+ニュートラル)。色が多いほど安っぽく見えやすい。
- ブランドカラーが1色ある場合、それを「差し色」として1箇所に集中させると効果的(例: 暖色のリムライトだけ製品に当てる)。

## 4. 構図(Composition)

- 三分割法(rule of thirds): 主題を中央からずらして配置すると奥行きが出る。ただし商品ヒーローショットは中央配置(パックショット)が定番。
- 余白(negative space): 高級感を出す場合、余白を大きく取り、情報を詰め込みすぎない。
- 奥行きレイヤー: 前景・被写体・背景の3層を意識すると、AI生成でも「平坦な絵」になりにくい。

## 5. Seedance/GPT Image向けプロンプト語彙(AIモデル特有の知識)

これは`references/known-failure-patterns.md`のFP-003から発展させたもの。**AIモデルは言葉を字面通りに解釈する。**

### 安定する語彙(推奨)

- 光・空気感: `bokeh`、`soft glints`、`volumetric haze`、`lens flare`、`warm rim light`、`shallow depth of field`
- 質感: `photoreal`、`physically-plausible reflections`、`visible micro-texture`、`brushed/polished metal`
- カメラの動き: `slow push-in`、`orbit`、`locked-off`、`handheld sway`(具体的な動詞+速度感)

### 不安定になりやすい語彙(避ける、FP-003)

- 図形的な名詞を「数えられるモノ」として書く: `ring`、`particle`、`line`、`dot` → 2Dグラフィックとして literal に描画されるリスクがある
- 抽象的すぎる形容詞だけの指示: `beautiful`、`amazing`、`cinematic`(単体では効果が薄い。具体的な光源・カメラ距離・素材とセットで書く)
- 「Blenderの安っぽさをなくして」のような**否定形だけの指示**: 何を足すべきかを明示しないと、モデルは何を変えればいいか分からない。「何を残し、何を足すか」を両方明記する(`workspace/prompts/templates/gpt-image-from-blender-previs.txt`のパターン)

### プロンプトの基本構造(推奨テンプレート)

1. 保持するもの(構図・配置・カメラ距離)
2. 置き換えるもの(質感・光・素材、写真的な語彙で)
3. 避けるもの(図形語彙、CGっぽさ、実在ブランドの模倣等)
4. 承認基準(何が写っていれば合格か)

## 6. 編集リズム・トランジション(Editing Rhythm & Transitions)

Why it matters:
- リズムは単なるカット尺の話ではなく、視聴者の注意・理解・感情をコントロールする編集の中核機能(著名編集者Walter Murchの「編集における感情の優先順位」の原則)。
- 「平均カット尺」という基準速度からの意図的な逸脱そのものが演出になる。

Principles:
- ベースとなるカット速度(尺別の平均カット尺は§1参照)からどれだけ逸脱するかでリズムを作る。速い/遅いは絶対値ではなく基準との差分で感じられる。
- **ジャンプカット**: 同一ショット内で時間を飛ばす編集。時間の圧縮、緊張感、コメディ効果、心理状態の強調に使う。継続編集の原則をあえて破る「見える編集」。
- **マッチカット**: 形状・動き・色・構図の類似性で2ショットをつなぐ。グラフィックマッチ(視覚的類似)、オーディオマッチ(音の継続)、J/Lカット(音が前後のショットにはみ出す)の3種類がある。連続性・時間経過・テーマ的つながりを作る。
- **モンタージュ**(Eisensteinの並置理論): 機能説明、使用手順、感情変化、Before/Afterの圧縮表現に向く。
- 継続編集(編集を隠す)とジャンプカット/スマッシュカット(編集を見せる)は目的が逆。どちらを選ぶかは演出意図で決める。

Prompt implications:
- Seedance内で複雑な編集(マルチカット、精密なタイミング)を1回の生成に詰め込まない。ショット単位で生成し、編集はPalmier Proの後工程に任せる。
- 正確なカット割りが必要な場合は、シーンを複数の短尺クリップに分けて生成し、後で繋ぐ。
- AI生成特有の「カット間の不連続感」を隠すため、Blender構図/プロンプトの段階でマッチカット的な連続性(形状・動き・色の一致)を意識して設計する。

Avoid:
- 1クリップに複数の複雑なトランジションを詰め込む指示。
- 「派手な編集で」のような抽象的すぎる指示(具体的な技法名を指定する)。

Source notes:
- Walter Murchの「感情優先」原則、Eisensteinのモンタージュ理論の言及(StudioBinder, Avid resource center)。
- マッチカット/ジャンプカットの定義・使い分け(Adobe, StudioBinder, MasterClass, Backstage)。技法名・原則のみ、具体的な映画/CM名の映像は参照していない。

## 7. 音響・音楽・SFXの基礎(Sound, Music & SFX Fundamentals)

Why it matters:
- 音は映像の後付け装飾ではなく、注意・感情・記憶・タイミングを作る設計要素。ブランドの「音の識別性」(sonic branding)は視覚と同じくらい記憶に残る。

Principles:
- **CMにおける音の役割**: フック、ムード形成、トランジションの接着、製品の質感(タクタイル感)、ブランド記憶、CTAの後押し。
- **BGMの構成は尺で変わる**: 15秒は立ち上がりが早く展開が短い。30秒はhook→development→payoff→end tagの4部構成。60秒はセクションごとに変化をつけ、呼吸(静けさ)を作る。
- **SFXの目的別分類**: whoosh(高速移動・トランジションの推進力)、riser(緊張の高まり、ピークをカット/タイトルに合わせる)、impact(着地点を作る、金属音やパーカッシブな音)。
- **SFXのタイミング**: whooshの長さはトランジションの長さに合わせる(カットが0.5秒ならwhooshも400-500ms程度が目安)。riserのピークは視覚的な重要瞬間(カット、タイトル出現)に正確に合わせる。
- **高級感の音作り**: 音数を減らす、静けさ・余白を使う、低域を安定させる、乾いたクリック音/金属的な質感。過剰な効果音は安っぽく聞こえやすい。
- 音楽が感情に与える要素: テンポ、楽器編成、リズム密度、無音(silence)、緊張と解放(tension/release)。

Prompt implications:
- Seedanceにナレーションや正確なCTA音声を生成させない。BGM/SFX/ナレーション/字幕は最終編集(Palmier Pro)で同期するのが基本方針(既存の`generate_audio=false`方針と一致)。
- 音声生成・BGM生成は、映像承認後の別ゲートとして扱う(既存のPalmier Pro `upscale_media`承認と同じ運用ルール、`WORKFLOW.md`§7-9b参照)。
- 高級ブランド案件では「音数を減らす」指示をBGM/SFXプロンプトに明記する。

Avoid:
- 「かっこいいBGMをつけて」のような抽象的指示(テンポ・楽器編成・展開を具体的に指定する)。
- 過剰な効果音の指示(高級感を狙う場合は特に)。
- 音楽・声・SEの権利確認を怠ること(既存曲風、特定アーティスト風、実在人物の声真似は避ける)。

Source notes:
- 広告向けサウンドデザイナーへのインタビュー記事(asoundeffect.com、prosoundeffects.com)、sonic brandingの考え方(Medium/H:12 Studio記事)。
- whoosh/riser/impactの実務的な使い方・タイミング(soundstripe.com, krotosaudio.com等の音響ライブラリ解説記事)。

## 8. プラットフォーム別の視聴文法(Platform-Specific Viewing Grammar)

Why it matters:
- 同じ映像でも、TikTok/YouTube Shorts/Instagram Reels/LP埋め込みでは視聴条件(音声のデフォルト、UIによる画面遮蔽、視聴意図)が違う。アスペクト比だけ変えて使い回すと効果が落ちる。
- 広告運用の詳細(入稿仕様、Pixel、Spark Ads等)はここでは扱わない。`references/tiktok-ad-ops-workflow.md`に委ねる。ここは**クリエイティブ文法**に限定する。

Principles(2026-07-01確認、変わりうる数値は都度確認すること):

**TikTok**(公式: ads.tiktok.com/help/article/creative-best-practices):
- 最初の3秒で提案内容を示す。広告想起の90%は最初の6秒で決まる。
- hook → body → closeの3部構成。
- pattern interrupt(意外な映像、大胆な発言、好奇心のギャップ)でスクロールを止める。
- **サウンドオフでも伝わるテキストオーバーレイが必須**(5-10語/秒が目安)。フィード消費の多くはサウンドオフ。
- 縦型9:16、720P以上、UIセーフゾーン内に収める。

**YouTube Shorts**(業界解説記事ベース、公式の一次情報は限定的):
- 最初の1-3秒がフック。視聴完了率がアルゴリズムの主要な順位シグナル。
- 冒頭15秒でフックがないと保持率が下がりやすい。
- 15-35秒程度が良好なパフォーマンス帯とされる(要検証、変わりうる)。

**Instagram Reels**(公式: creators.instagram.com/blog):
- 上部・下部の帯(プロフィール表示、キャプション/アクションボタン)がUIで隠れるため、CTA・テキスト・見せたいものは中央に配置する。
- **デフォルトで音声ありで再生される(TikTokと異なる)**。音声込みのReelsは無音版よりエンゲージメントが高いというデータがある。
- 字幕は視聴完了率を上げるため、音声ありが前提でも必須。
- 最初の3秒で継続視聴が判断される。

**LP埋め込み動画**(業界解説記事ベース):
- 自動再生する場合は必ずミュートにする(ブラウザ制約上も必須)。
- **ミュート前提の設計**: ナレーション/効果音なしで映像だけで意味が伝わる構成にする。
- 序盤(10秒前後)・中盤(60秒前後)で離脱が発生しやすいというデータがあり、30-90秒程度に収めるのが目安。
- 動画がCTAと競合しないようにする(動画に見入って離脱されるなら、CTAをより近くに配置)。
- 動画はページ速度(LCP)への影響が大きいことにも留意する。

Prompt implications:
- `video_use_case=social-post`でプラットフォームが決まっている場合、該当項目をブリーフに明記する。
- TikTok広告運用の詳細(Pixel、Spark Ads、入稿仕様等)は`references/tiktok-ad-ops-workflow.md`に委ねる。
- Instagram Reelsは音声ありがデフォルトなので、TikTokと同じ「サウンドオフ前提」の設計をそのまま流用しない。

Avoid:
- 1つのプラットフォーム向けに作った映像を、アスペクト比だけ変えて他プラットフォームにそのまま流用すること。
- LP埋め込み動画にナレーション必須の構成をそのまま使うこと(自動再生はミュート前提)。

Source notes:
- TikTok公式クリエイティブベストプラクティス(ads.tiktok.com/help、2026-07-01確認)。
- Instagram Reels公式情報(creators.instagram.com/blog、2026-07-01確認)。
- YouTube Shortsは公式仕様ではなく業界解説記事ベース(opus.pro等、2026-07-01確認、数値は変わりうる)。
- LP動画のUX/CRO解説(unbounce.com等、2026-07-01確認)。

## 9. 参照素材がある場合の分析手順(スクレイピング代替)

ユーザーから「このCMのような感じにしたい」という具体的な参照がある場合:

1. 実際の映像・画像ファイルはダウンロード・保存しない。
2. `references/higgsfield-mcp-demo-patterns.md`と同じ形式で、以下だけを言語化して記録する:
   - 構成(尺・ビート配分)
   - ショットの文法(何ショット目に何が来るか)
   - 光・色の型
   - カメラワーク
   - 再現時の注意点(実際の素材はコピーしない)
3. このファイルの該当セクションに、新しい型として追記する(汎用的に使えるパターンとして一般化する)。

## 関連ファイル

| 目的 | ファイル |
|---|---|
| 実際の失敗記録(事後) | `references/known-failure-patterns.md` |
| 過去の参照分析の実例 | `references/higgsfield-mcp-demo-patterns.md` |
| Blender→写実キービジュアルのプロンプト雛形 | `workspace/prompts/templates/gpt-image-from-blender-previs.txt` |
| 用途別の構成ガイド(既存) | `SKILL.md` の Use-Case Prompt Guidance |

## 調査済みソース(ログイン不要・公開情報のみ、2026-07-01)

素材そのものはコピーしていない。構造・技法・数値の言及のみを言語化して上記に反映。

- Cannes Lions 2025 Grand Prix / Luxury Lions受賞作の傾向(LBBOnline, The Drum, Medium記事経由)
- 高級化粧品・香水の商品撮影ライティング技法(cybertizemedia.com, skylum.com等)
- TVCMストーリーボードの構造・カット尺の実測値(Boords, StudioBinder等の広告制作解説サイト)

新しい参照を追加する場合も、この形式(構造だけメモ、素材はコピーしない、ソースを明記)を守ること。

## Source Log Additions(2026-07-01、Phase 1: 編集リズム/音響/プラットフォーム文法)

| Source ID | Source | Type | Topic | Extracted principle | Checked |
|---|---|---|---|---|---|
| CRAFT-EDIT-001 | studiobinder.com, avid.com (Walter Murch editing principles) | editor interview / industry technical article | editing rhythm | 感情優先の編集原則、基準カット速度からの逸脱でリズムを作る | 2026-07-01 |
| CRAFT-EDIT-002 | adobe.com, studiobinder.com, masterclass.com, backstage.com | industry technical article | match cut / jump cut | マッチカット3種(graphic/audio/J-L)、ジャンプカットの意図的な継続性破壊 | 2026-07-01 |
| CRAFT-SOUND-001 | asoundeffect.com, prosoundeffects.com (sound designer interviews) | sound designer interview | advertising sound design / sonic branding | 音がブランド記憶・感情・タイミングを作る設計要素であること | 2026-07-01 |
| CRAFT-SOUND-002 | soundstripe.com, krotosaudio.com | industry technical article | whoosh / riser / impact SFX | SFXのタイミング合わせ(riserのピークを視覚的瞬間に合わせる等)の実務原則 | 2026-07-01 |
| CRAFT-PLATFORM-001 | ads.tiktok.com/help/article/creative-best-practices | **official platform guide** | TikTok creative grammar | 最初の3秒、hook/body/close、サウンドオフ前提のテキスト設計 | 2026-07-01 |
| CRAFT-PLATFORM-002 | creators.instagram.com/blog | **official platform guide** | Instagram Reels creative grammar | 音声ありがデフォルト、UI遮蔽エリア(上下250px相当)を避ける配置 | 2026-07-01 |
| CRAFT-PLATFORM-003 | opus.pro (YouTube Shorts分析記事) | industry technical article(非公式、数値は変わりうる) | YouTube Shorts retention | 冒頭1-3秒のフックと視聴完了率の関係 | 2026-07-01 |
| CRAFT-PLATFORM-004 | unbounce.com | industry technical article | LP埋め込み動画のUX/CRO | ミュート前提設計、自動再生の離脱データ、CTAとの競合回避 | 2026-07-01 |

公式ソースが確認できたもの: TikTok(CRAFT-PLATFORM-001)、Instagram Reels(CRAFT-PLATFORM-002)。YouTube ShortsとLP埋め込み動画は公式一次情報が見つからず、業界解説記事ベース(要再確認の対象として明記)。
