# Generic AI Video Generation Logic

このファイルは、リップCMだけでなく全案件に適用する生成工場ロジックの正です。

## 0. Core Rule

Blenderは「完成画」ではない。
Blenderは構図、カメラ、空間配置、商品/人物の位置関係を決めるためのprevisである。

Seedanceへ渡す主画像は、Blender renderではなく、Blender previsを元に画像生成で写実化した承認済みstoryboard/key visualでなければならない。

## 1. Roles

| Layer | Role | Truth | Seedance primary input |
|---|---|---|---|
| Blender previs | `composition_only` | camera angle, framing, object placement, scale, continuity | no |
| Visual handoff | structured bridge | what to preserve / what to avoid | no |
| GPT Image / Higgsfield image | `visual_truth` | photoreal material, lighting, skin/product realism, commercial mood | candidate |
| Human approval | gate | this exact image may drive motion | yes after approved |
| Seedance | `motion_truth` | camera motion, action, timing, continuity | output video |
| Palmier/editor | post | audio, subtitles, color, final export | final assembly |

## 2. Canonical Flow

```text
Brief lock
  -> asset/rights/budget lock
  -> Blender previs, if composition is needed
  -> visual-handoff.json
  -> clean photoreal storyboard prompt
  -> image-generation request preparation
  -> photoreal storyboard/key visual
  -> human side-by-side approval
  -> asset-manifest.json with role=visual_truth
  -> learning-preflight.md
  -> Seedance cost request
  -> human cost approval
  -> Seedance generation request
  -> review/contact sheet
  -> learning update
  -> audio/subtitles/edit/export
```

## 3. What To Preserve From Blender

- camera angle
- lens/framing
- object placement
- scale relationship
- shot continuity
- rough motion intent

## 4. What Must Not Carry Over

- low-poly look
- viewport lighting
- temporary materials
- gray/flat background
- plastic shader
- cheap CG preview look
- graphic overlay artifacts from the previs

## 5. Asset Rules

Allowed Seedance primary image kinds:

- `photoreal_key_visual`
- `approved_storyboard_frame`
- `rights_confirmed_user_asset`
- `approved_product_reference`

Blocked Seedance primary image kinds:

- `blender_previs`
- `viewport_screenshot`
- `blender_render` with `role=composition_only`
- anything with `seedance_input_allowed=false`
- anything with `approval_status != approved`
- anything with unknown rights

The script-level enforcement is `workspace/scripts/validate-seedance-input.py`.

## 6. Permission Rule

Casual phrases like "進めて", "生成して", or `APPROVED=1` are not unlimited permission.

Seedance preparation requires:

- approved prompt
- approved visual_truth asset manifest
- learning preflight
- run-permission manifest
- budget cap
- max job count
- max retry count
- explicit allowed action

Paid execution requires a separate explicit approval and `execute_paid_generation=true` in the permission manifest.

## 7. Learning Loop

This tool does not fine-tune third-party models.
It learns by updating local production memory:

- `references/known-failure-patterns.md`
- `workspace/learning/prompt-rules.md`
- `workspace/learning/review-rubric.md`
- `workspace/learning/pattern-memory.jsonl`
- `workspace/learning/failure-candidates.md`
- per-shot `learning-preflight.md`
- per-shot `review.json`

Before generation, the system reads known failures and prompt rules.
After generation, the system records what failed, what worked, and what must change next time.

## 8. Universal Stop Conditions

Stop before paid generation when:

- Blender render is still the primary image
- photoreal storyboard/key visual is missing
- human approval is missing
- asset rights are unknown
- learning preflight is missing or false
- permission manifest is missing
- budget/max jobs/max retries are missing
- the same concept failed 3 times
- the same rejection appeared 2 times
- `workspace/run/HERMES_STOP` exists

## 9. Lipstick CM Is Only An Example

The lipstick CM failure proves the rule:

Blender blockout + prompt text did not become high-brand photoreal footage.
The output kept the raw 3D preview look.

Therefore every project must use the same abstract workflow:

Blender creates structure.
Image generation creates visual truth.
Seedance creates motion.
Editing creates audio, subtitles, and final delivery.
