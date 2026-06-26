# Seedance CM Workflow

## Required Inputs

Capture these before generation:

- Brand/service/product name
- Pronunciation guide, if needed
- One-line value proposition
- Target format: `16:9`, `9:16`, `1:1`, or another supported ratio
- Duration and number of variants
- Main reference assets:
  - model/person image
  - product images
  - app screenshots
  - logo or brand visuals
- Audio policy:
  - AI voice-over allowed or not
  - AI music allowed or not
  - in-video AI text allowed or not

## 15-Second Structure

Use this as the default short CM structure.

### 16:9

1. 0-3s: Establish the product/service and main subject.
2. 3-7s: Show the problem or transformation trigger.
3. 7-12s: Show the product/service result with visual proof.
4. 12-15s: End with brand/service name and one clear CTA or claim.

### 9:16

1. 0-2s: Immediate hook.
2. 2-6s: Fast transformation or benefit demonstration.
3. 6-11s: Main result, centered and readable.
4. 11-15s: Final brand/service moment.

## 30-Second Structure

For two 15-second clips that will be joined later:

- Clip A: hook, problem, transformation setup.
- Clip B: result, social proof or use cases, final brand/service moment.

Keep each clip self-contained enough to work alone.

## Prompt Template

```text
{ASPECT} commercial video for {BRAND_OR_SERVICE_NAME}.
Pronounce the name as "{PRONUNCIATION}".

Goal:
{ONE_LINE_VALUE_PROPOSITION}

References:
- Use the provided main reference as the primary subject or product anchor.
- Use additional references only as visual/product/app references.
- Do not imply unsupported official partnerships or guarantees.

Visual direction:
{STYLE_DIRECTION}

Timing:
0-3s: {BEAT_1}
3-7s: {BEAT_2}
7-12s: {BEAT_3}
12-15s: {BEAT_4}

In-video text:
Use only short, clean text:
1. "{TEXT_1}"
2. "{TEXT_2}"
3. "{BRAND_OR_SERVICE_NAME}"

Voice-over:
Include a {LANGUAGE} voice-over with this exact narration:
"{NARRATION}"

Audio:
{MUSIC_DIRECTION}

Quality and safety:
Realistic commercial footage. Clear subject. Stable face/object. No distorted anatomy, no unreadable long text, no unsupported claims, no unsafe or sexualized framing, no clutter.
```

## Variant Defaults

### Product / EC

- Style: clean studio, catalog-quality lighting, product cards, before/after usage.
- Text: short benefit + product/service name.
- Warning: do not imply exact product condition or guaranteed fit unless verified.

### App / SaaS

- Style: app panels, workflow transitions, dashboard moments, user outcome.
- Text: feature name + result.
- Warning: avoid fake metrics unless provided.

### Brand / Lifestyle

- Style: cinematic hero, environment, brand emotion.
- Text: tagline + brand name.
- Warning: keep claims soft unless substantiated.

## Retry Strategy

AI動画が崩れた場合、同じプロンプトを闇雲に再実行しない。原因を絞り、複雑さを下げてから再生成する。

1. 画面内テキストを減らす。
   - 長文字幕、複数行テロップ、小さい注釈を削る。
   - ブランド名、短いタグライン、1フレーズだけにする。
2. カメラワークをシンプルにする。
   - 激しい回転、急ズーム、複雑なトラッキングを避ける。
   - 固定カメラ、ゆっくりしたドリー、シンプルなパンへ寄せる。
3. 1本の動画に詰め込む要素を減らす。
   - 商品、UI、人物、ロゴ、テキスト、背景変化を同時に入れすぎない。
   - 重要な1〜2要素だけを残す。
4. 15秒動画が崩れる場合は、5秒〜8秒の短いクリップに分割する。
   - 変身前、変身中、完成カットなどに分ける。
   - 後編集でつなぐ前提にする。
5. 商品、人物、ロゴが崩れる場合は、参照画像を強化する。
   - 正面、詳細、ロゴ、UIスクリーンショットなど、必要な参照を追加する。
   - 参照が弱いものはプロンプトだけで補わない。
6. 顔や商品が2回以上崩れる場合は、AI生成だけで完結させない。
   - 手動編集、別素材、別構成、実写素材、静止画モーション化を提案する。
7. 原因が不明な場合は、プロンプトを複雑にしない。
   - 構図、動き、テキスト、参照素材数を単純化する。

再生成は原則2回までにする。3回目以降はユーザー確認、予算確認、または構成見直しを行う。

## Delivery Package

1案件ごとに、以下を整理して納品または共有する。

- `final/`
  - final MP4 files
  - aspect ratio and durationが分かるファイル名
- `prompts/`
  - 実際に使ったprompt files
  - バリエーションごとの差分
- `references/`
  - reference asset list
  - 使用素材の出所、権利状態、用途
- `jobs/`
  - generation settings
  - job JSON
  - result URLs
  - cost estimate, when available
- `notes/`
  - revision notes
  - usage notes
  - known limitations

`known limitations`には、必要に応じて以下を記載する。

- AI生成動画のため、極小文字、完全なロゴ再現、完全な人物一致は保証できない。
- 重要な法的表現、医療表現、金融表現、価格表記、キャンペーン条件は人間が確認する。
- 最終公開前に、クライアント側で内容、権利、表記を確認する。
- 権利が不明な素材を含む場合は、内部確認用ドラフトであり、商用公開用ではない。

## Quality Checklist

Before final response, verify:

- Job completed and result URL is saved.
- MP4 was downloaded when practical.
- Duration is close to requested duration.
- Aspect ratio matches target.
- Generated text is acceptable for a draft.
- Voice-over pronunciation was explicitly specified.
- No brand/project-specific defaults leaked into the prompt.
- If quality is weak, recommend a second pass with stronger references or fewer on-screen text requirements.
- Delivery package or delivery notes are prepared.
- Rights and budget notes are recorded.
