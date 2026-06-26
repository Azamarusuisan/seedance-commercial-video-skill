---
name: seedance
description: Create short commercial videos with Higgsfield Seedance from a service/product brief, model reference, product references, screenshots, or brand assets. Use when Codex needs to plan prompts, generate PC/mobile variants, estimate cost, submit Seedance jobs, track outputs, or package reusable CM-generation workflow for fashion, EC, app, SaaS, product, or brand promotion videos.
---

# Seedance Commercial Video

## Overview

Use this skill to produce short CM-style videos with Higgsfield Seedance while keeping the workflow reusable across brands and projects. Treat every brand name, pronunciation, product name, person, and claim as user-provided input; do not bake project-specific defaults into the skill.

## Workflow

1. Lock the brief:
   - service/product name
   - required pronunciation, if any
   - target audience
   - deliverables: aspect ratio, duration, count
   - maximum budget, maximum jobs, and maximum retry count
   - whether AI voice-over and AI in-video text are allowed
   - required references: model, products, screenshots, brand assets
2. Gather references from local/project files first. Use web assets only when explicitly allowed.
3. Write one prompt per output. Do not reuse a 16:9 prompt unchanged for 9:16.
4. Keep Seedance responsible for cinematic video. Keep in-video text short: one phrase per beat.
5. Preflight:
   - `higgsfield account status --json`
   - `higgsfield model get seedance_2_0 --json`
   - `higgsfield generate cost seedance_2_0 ... --json`
6. Generate:
   - Use `seedance_2_0` by default unless the user chooses another model.
   - Prefer `--resolution 4k` and `--bitrate_mode high` when the user prioritizes quality and credits allow.
   - Use `--generate_audio true` only when AI narration/music is wanted.
7. Track every artifact:
   - prompt file
   - reference file list
   - model and parameters
   - job JSON
   - result URL
   - downloaded MP4 path
8. Verify before final:
   - output opens and has expected duration/aspect
   - brand/service pronunciation is correct in prompt
   - text is short enough to be plausible
   - reference person/object is not badly distorted
   - visual does not imply unsupported claims

## Commercial Rights Gate

商用CMとして扱う場合は、生成前に素材の権利状態を確認する。AIだけで法務判断を完結させない。

- ユーザーが提供した画像、動画、ロゴ、人物素材、商品素材、スクリーンショットを優先する。
- Web上の画像や第三者素材を、商用CMの最終成果物へ無断利用しない。
- 人物写真、店舗写真、商品写真、ロゴ、UIスクリーンショットは、ユーザーが商用利用権を持っている前提が必要。
- 権利が不明な素材を使う場合、その出力は「内部確認用ドラフト」として扱い、最終納品物とは分ける。
- 有名人、既存ブランド、他社広告、映画、アニメ、ゲームなどのIPを無断で模倣しない。
- 商標、著作権、肖像権、パブリシティ権のリスクがある場合は、別素材、抽象表現、汎用モデル、架空ブランド表現などの代替案を作る。
- 最終公開前の権利確認は、クライアントまたは権利確認担当者が行う。

## Budget Lock

動画生成は費用が膨らみやすいため、生成前に予算と回数を固定する。

- 生成前に、最大予算、最大ジョブ数、最大再生成回数を確認する。
- 予算が不明な場合は、最小構成で進める。例: 1本、短尺、低めの解像度、音声なし、少ないバリエーション。
- 予算を超える生成を勝手に実行しない。
- 品質改善目的でも、無制限に再生成しない。
- 予算オーバー時は、本数、秒数、解像度、音声、バリエーション数を減らす。
- 再生成は原則2回まで。3回目以降はユーザー確認、構成見直し、素材見直し、または手動編集案へ切り替える。
- 見積もりが可能な場合は、生成前に`higgsfield generate cost ... --json`で確認し、結果を記録する。

## Acceptance Criteria

納品OK/NGは以下で判定する。重要項目が満たせない場合は、納品せず再生成、手動修正、構成見直しの対象にする。

- 指定されたアスペクト比、秒数、本数がブリーフと一致している。
- 店舗名、商品名、サービス名、読み方が間違っていない。
- ナレーションがある場合、読み方、イントネーション、言語、トーンの指定がプロンプトまたは制作メモに明記されている。
- 画面内テキストが長すぎず、潰れず、ドラフトとして読める。
- ロゴ、人物、商品、UIが大きく破綻していない。
- 根拠のない売上保証、医療・法律・金融的な断定、虚偽の実績、架空の提携表現がない。
- 最終MP4を実際に開ける。
- 出力ファイルの保存先、生成設定、ジョブ情報、成果物URLが記録されている。
- 重要なブランド要素が間違っている場合は納品せず、再生成または修正対象にする。
- AI生成動画としての限界、確認事項、使用上の注意が納品メモに残っている。

## Commercial Safety Rules

商用CMでは、誤認や権利リスクにつながる表現を避ける。

Do not generate or approve:

- 売上保証。
- 「必ず儲かる」「絶対集客できる」などの断定。
- 根拠のないNo.1表記、業界最高、世界初、唯一などの優位性表現。
- 架空の口コミ、架空の受賞歴、架空の掲載実績。
- 実在企業との提携を匂わせる表現。
- 医療、美容、金融、法律などで誤認を招く効果保証。
- 第三者ブランド、有名人、キャラクター、映画、アニメ、ゲーム等の無断利用。
- 実際の商品、価格、キャンペーン条件、在庫、納期と違う表示。
- AI生成であることを隠したまま、実写証拠や実物保証のように見せる表現。

必要な主張がある場合は、ユーザーから根拠資料を受け取り、最終公開前に人間が確認する。

## CLI Pattern

```bash
higgsfield generate cost seedance_2_0 \
  --prompt "$(cat prompts/variant.txt)" \
  --image ./assets/reference.png \
  --aspect_ratio 16:9 \
  --duration 15 \
  --resolution 4k \
  --bitrate_mode high \
  --generate_audio true \
  --mode std \
  --json
```

```bash
higgsfield generate create seedance_2_0 \
  --prompt "$(cat prompts/variant.txt)" \
  --image ./assets/reference.png \
  --aspect_ratio 16:9 \
  --duration 15 \
  --resolution 4k \
  --bitrate_mode high \
  --generate_audio true \
  --mode std \
  --json \
  --wait \
  --wait-timeout 60m \
  --wait-interval 10s
```

When passing multiple media references, first verify the CLI/media schema with a low-cost test or current model documentation. If a multi-reference path fails, fall back to one strong visual reference plus explicit product/service description in the prompt.

## Prompt Rules

- Always include the required pronunciation when the service/product name has a non-obvious reading.
- Use concise in-video text. Prefer 1-8 characters for logos and 5-14 Japanese characters for caption cards.
- For voice-over, write exact narration and specify language, tone, and pronunciation.
- Separate PC and mobile composition:
  - PC/16:9: wider layout, product/app panels, clearer service explanation.
  - Mobile/9:16: centered subject, faster hook, fewer words, stronger final brand moment.
- Do not claim exact fit, exact product condition, medical/legal/financial outcomes, or official partnership unless the user provided that basis.
- For people: preserve broad identity, expression, and natural face quality without promising perfect likeness.
- For products: preserve color/material/shape as a goal, but label generated footage as reference if used commercially.

## Delivery Package

案件ごとに、成果物と制作情報を同じフォルダまたは同じ納品メモに整理する。

- final MP4 files
- prompt files
- reference asset list
- generation settings
- cost estimate, when available
- job JSON
- result URLs
- revision notes
- usage notes
- known limitations

`known limitations`には、必要に応じて以下を明記する。

- AI生成動画のため、極小文字、完全なロゴ再現、完全な人物一致は保証できない。
- 重要な法的表現、医療表現、金融表現、価格表記、キャンペーン条件は人間が確認する。
- 最終公開前に、クライアント側で内容、権利、表記を確認する。

## Reference

Read `references/seedance-cm-workflow.md` before writing final prompts or generating multi-variant CM jobs.

## Final Checklist

- [ ] Brief confirmed
- [ ] Rights confirmed
- [ ] Budget confirmed
- [ ] Aspect ratio confirmed
- [ ] Duration confirmed
- [ ] Brand name checked
- [ ] Voiceover pronunciation checked
- [ ] On-screen text readable
- [ ] Claims are safe
- [ ] Final MP4 opened successfully
- [ ] Output paths recorded
- [ ] Delivery package created
- [ ] Known limitations documented
