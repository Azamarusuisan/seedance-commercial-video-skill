# CM Brief

## Status

- Status: proposal v1.
- Approval status: not approved for Higgsfield generation yet.
- Do not run Higgsfield generation until this brief, image reference, and final prompt are approved by the user.

## Fixed Production Constraints

- Service: 競馬AI
- Reading/pronunciation: けいばエーアイ
- Aspect ratio: 9:16
- Duration: 15秒想定
- Output count: 1
- Retry ceiling: 2
- Model: seedance_2_0 by default
- Mode: image-to-video using a generated abstract reference image
- Audio: TBD. Initial recommendation is no AI voice.
- Commercial rights gate: required before generation

## 企画意図

Xのタイムラインで、競馬AIの利用シーンを「AIでここまで綺麗なCMを作れるのか」と感じる映像にする。実在素材や権利不明素材は使わず、未来的な競馬データ分析、光のレーストラック、AIパネル、疾走感で魅せる。

目的は的中や収益を保証することではなく、「フジ AI開発」のAI制作力、AI開発感、映像品質を印象づけること。

## ターゲット

- Xの競馬ユーザー
- 競馬予想やデータ分析に興味があるユーザー
- AI活用やAI開発に反応するユーザー
- ショート動画で驚きのあるビジュアルに反応するユーザー

## 冒頭3秒のフック

暗いタイムライン上に、光でできた競馬場とAI分析パネルが立ち上がり、中央に「競馬AI」が大きく現れる。最初の印象は「競馬AIってこんなに綺麗に見せられるのか」。

## 映像構成

1. 0-3秒: 未来的な競馬場と光のトラック。大きく「競馬AI」。
2. 3-7秒: AIデータパネル、波形、レース分析の抽象表示が馬のシルエットを囲む。
3. 7-11秒: 利用シーンとして、Xで見た人が思わず止まるような縦型CM表現。競馬データが美しい映像へ変わる。
4. 11-15秒: 「フジ AI開発」を強く見せて締める。

## CTA

フジ AI開発

## 画面内テキスト

候補:

- 競馬AI
- AIで、競馬を美しく
- 予想を、データで見る
- フジ AI開発

最終プロンプトでは短く絞る。的中保証、利益保証、勝率表現は入れない。

## ナレーション案

初回案は音声なしを推奨。

音声を使う場合の案:

> 競馬AI。AIで、競馬をもっと美しく。フジ AI開発。

## 参照画像メモ

- Current local reference: `workspace/assets/reference-keiba-ai-v1.png`
- Source: built-in `image_gen` output copied from `/Users/stork/.codex/generated_images/...`
- Status: usable as discussion reference.
- Caveat: If the user specifically requires OpenAI Image API / GPT Image generation, regenerate after `OPENAI_API_KEY` is available in the environment.

## 権利確認メモ

- ユーザー提供素材はなし。
- Web画像、第三者素材、有名人、既存キャラクター、第三者ブランドロゴは無断利用しない。
- 実在競馬場、実在馬、実在騎手、実在レース名の再現は避ける。
- 競馬AIは的中保証や利益保証に見えない表現にする。
- 商用公開前に、人間が権利、商標、表記、利用規約を確認する。

## 生成予算メモ

- 予算上限: TBD
- 予算が不明な場合の最小構成: 9:16、15秒、1080p、音声なし、1本。
- 再生成は最大2回まで。
- Higgsfield MCPが接続された環境で、生成前にコスト見積もりを取得する。

## NG表現

- 的中保証、勝率保証、回収率保証、利益保証
- 必ず勝てる、絶対儲かる、勝率No.1
- 根拠のないNo.1、唯一、世界初、公式提携
- 実在競馬場、実在馬、実在騎手、第三者ブランドの無断模倣
- 投資助言や金融商品に見える断定

## 納品チェック項目

- 動画が開ける
- 9:16である
- 尺が指定どおりである
- 「競馬AI」「フジ AI開発」の表記が正しい
- 画面内テキストが短い
- 的中保証、利益保証、誇大広告表現がない
- 権利不明素材が混ざっていない
- 生成ログ、プロンプト、URL、ジョブ情報が残っている
- known limitationsが納品メモに書かれている
