# TikTok Ad Ops Workflow For Seedance / Higgsfield

Last updated: 2026-06-29

Use this reference when Seedance / Higgsfield creatives are intended for TikTok Ads. It connects creative planning, CV-first structure, Spark/Non-Spark choice, review risk, tracking, A/B testing, and post-launch learning.

This is not a standalone ad-operations skill. Keep it inside the `seedance` skill so TikTok performance feedback can return directly to the next script, prompt, cast choice, first frame, subtitles, CTA, and LP connection.

## 1. Scope And Stop Rules

This reference covers:

- TikTok 9:16 short ad structure
- Spark Ads / Non-Spark Ads creative decisions
- CV, CTR, awareness, save/comment objectives
- TikTok Creative Center / Top Ads structure analysis
- Pixel / Events API / standard event checklists
- A/B test planning
- post-launch KPI diagnosis
- review risk, Japanese legal expression risk, LP consistency, rights checks

This reference does not cover:

- TikTok Ads Manager login
- ad submission, publishing, pausing, deletion, budget, bidding, billing, or account permission changes unless a run-permission manifest explicitly allows them
- tag/API implementation itself
- legal review replacement
- ad approval guarantees

Stop and request a run-permission manifest for:

- ad publish/send, campaign creation, budget/bid/date/targeting changes, billing, account linking, Spark Ads authorization, outside posting, pinned comments, replies, or deletion
- high-risk categories: beauty, health, medical, pharmaceutical, supplements, diet, finance, investment, real estate, jobs, politics, religion, gambling, minors
- use of real people, creators, public figures, customer reviews, UGC posts, voice, music, logos, facilities, comments, or screenshots without rights confirmation
- AIGC, AI voice, AI avatars, or generated people when disclosure/labeling status is unclear

If the manifest explicitly allows one of these actions, execute only within its account, campaign, budget, time, action, and asset limits. Record the action in the iteration log before and after execution.

## 2. TikTok Intake Checklist

Before writing scripts or prompts, collect:

- product/service name
- product category and high-risk category status
- delivery country/region
- target viewer
- age restriction need
- objective: CV, CTR, awareness, save/comment, other
- primary KPI
- LP URL
- LP first-view promise
- offer, price, discount, deadline, conditions
- proof/evidence materials
- allowed assets
- blocked assets
- Spark Ads plan: yes/no/unknown
- Non-Spark Ads plan: yes/no/unknown
- Pixel status: unknown/yes/no
- Events API status: unknown/yes/no
- optimization event
- UTM naming
- AIGC disclosure need
- legal/ad review owner
- official spec check date

Template: `workspace/prompts/tiktok-ad-intake.md`

## 3. Spark Ads / Non-Spark Ads Decision

Spark Ads uses an existing organic TikTok post as the ad creative. Use it when:

- a strong organic post already exists
- the brand wants engagement to stay tied to the original post
- creator/UGC/social proof matters
- comments, likes, shares, profile visits, and follows should compound on the source post
- the poster and rights owner have approved paid usage scope

Use Non-Spark Ads when:

- the creative is ad-only
- drafts should not remain as organic posts
- AI-generated material, ad-only CTA, LP claims, and many variants need fast testing
- comment accumulation on an organic post is not the goal
- Spark authorization, posting, or account linking is not ready

Rules:

- For creator face, voice, or organic posts, verify usage authorization first.
- For AI-generated UGC style, avoid making generated people look like real customers giving real testimonials.
- For scaling a proven post, prefer Spark Ads.
- For CV testing many structures quickly, prefer Non-Spark Ads.
- Either route still needs LP, rights, review, and AIGC checks.

Template: `workspace/prompts/tiktok-spark-vs-nonspark.md`

## 4. Pixel / Events API / Standard Events Checklist

For CV campaigns, creative diagnosis is unreliable without tracking context.

Check:

- Pixel installed: unknown/yes/no
- Events API installed: unknown/yes/no
- Pixel + Events API together: unknown/yes/no
- Web Conversions prerequisite confirmed
- event deduplication
- UTM
- LP speed
- form/purchase/reservation path
- privacy policy
- sensitive data restrictions
- technical owner
- check date

Common standard events to verify:

- `ViewContent`
- `Search`
- `AddToCart`
- `InitiateCheckout`
- `Purchase`
- `SubmitForm`
- `CompleteRegistration`
- `Contact`
- `Schedule`

Rules:

- If Pixel / Events API is unknown, do not make hard CVR or CPA conclusions.
- If standard events are missing, fix measurement before judging the creative.
- If the ad promise and LP first view do not match, fix LP consistency before making stronger ads.
- If final CV volume is too low, a middle event can be considered by a human operator.

Template: `workspace/prompts/tiktok-pixel-events-checklist.md`

## 5. CV-Focused 15s Structure

For CV, do not hide the product for the sake of story suspense. The viewer should understand who it is for, what it is, and why to act quickly.

| Time | Role | Content | Seedance note |
|---:|---|---|---|
| 0.0-1.5 | Stop scroll | unusual visual, problem, result, or use moment | specify the exact first frame |
| 1.5-3.0 | Product/category | show what the ad is about | include product/service/category/use scene |
| 3.0-5.0 | Specific problem | who has what issue | short subtitle in viewer language |
| 5.0-8.0 | Use/solution | show how it helps | include hand, screen, pack, app, or LP-aligned claim |
| 8.0-11.0 | Trust/reason | proof, feature, comparison point, offer | no unsupported guarantees |
| 11.0-13.0 | LP connection | repeat the promise the LP first view can answer | match LP language |
| 13.0-15.0 | CTA | one next action | clear CTA, one action only |

Hard rules:

- Show product/category/service within 3 seconds.
- Use one CTA type per 15s creative.
- Use a soft CTA around 5-8s and a final CTA around 13-15s when appropriate.
- Do not make claims the LP cannot prove.
- If first product appearance is after 8s, revise for CV campaigns.
- High completion rate alone is not a win if CTR/CVR/CPA are weak.

Template: `workspace/prompts/tiktok-cv-15s-script.md`

## 6. KPI Priority And Diagnosis

Do not use fixed universal benchmarks. Compare within the same campaign, same product, and same tracking setup.

For CV campaigns, inspect in this order:

1. Tracking health: Pixel, Events API, standard events, deduplication, UTM, LP path
2. 2-second view: first frame, hook, face/product, sound, subtitle
3. 6-second focused view: whether the promise continues
4. Product presentation timing
5. CTR: CTA, offer, clarity, product understanding
6. LP arrival and LP drop-off
7. CVR: LP, price, form, trust, audience fit
8. CPA
9. ROAS
10. Completion rate as a secondary signal

Diagnosis tags:

| Tag | Symptom | Next Seedance instruction |
|---|---|---|
| `HOOK_FIX` | weak 2s view | change first frame and hook; make 4 hook variants |
| `BODY_FIX` | 2s ok but 6s weak | speed up 1.5-6s and move product earlier |
| `PRODUCT_FIX` | view ok, CTR weak | change product scene, benefit, offer, CTA |
| `CTA_FIX` | product understood, clicks weak | use one CTA and show it mid/final |
| `LP_FIX` | CTR high, CVR weak | check LP first view, price, form, promise mismatch |
| `TRUST_FIX` | anxiety/comments hurt CV | add proof, usage, conditions; avoid guarantees |
| `COMPLIANCE_FIX` | review rejected/warned | fix claims, LP, rights, AIGC, category risk |
| `FATIGUE_FIX` | performance declined | keep winning structure; refresh first frame, person, sound, subtitle tempo |
| `KEEP_SCALE` | CPA/ROAS good | keep structure; make 3 variants of person/first frame/subtitle |

## 7. Format Rules

### UGC Style

Safe direction:

- "usage image"
- "example scene"
- "staff introduction"
- "ad recreation"
- real reviews only with source, permission, quote scope, and edit notes
- check PR/ad disclosure when needed

Avoid:

- fake usage periods
- fake friends/customers
- fake reviews, names, age, occupation, symptoms
- "not an ad" / "not sponsored"
- fake expert, doctor, influencer, or celebrity endorsements
- generated people giving real-customer testimonials

### Travel / Beauty Vlog

- Use beauty/travel to stop scroll, but make the viewer action the protagonist.
- Put product/category/service in subtitles or visuals by 3s.
- Include product/app/reservation/use scene by 6-9s.
- Verify real location, facility, logo, music, price, availability, and campaign terms.
- Do not exploit appearance anxiety for beauty, health, or finance categories.

### Story Ads

For CV, compress the story:

```text
0.0-1.5 incident or curiosity
1.5-3.0 product/service appears
3.0-6.0 protagonist problem
6.0-9.0 use/choice moment
9.0-12.0 reason to choose
12.0-15.0 CTA
```

## 8. High-Risk Expression Rules

Avoid unless evidence, scope, required disclaimers, and human review are complete.

Common:

- 100%, must, absolute, guaranteed, anyone, complete, permanent, instant, immediately
- No.1, best, cheapest, only, officially certified without source/scope/period/body
- refund/effect/satisfaction guarantee without terms
- everyone buys it, doctor approved, celebrity loves it without proof/permission
- false UI, fake play buttons, fake diagnosis, fake notifications
- prices, discounts, deadlines, benefits absent from LP

Beauty / cosmetics / aesthetic:

- spots disappear, wrinkles disappear, acne is cured, pores vanish, rejuvenates, regenerates skin, activates cells, medical-grade, surgery-grade, guaranteed painless, guaranteed no side effects

Health / supplements / diet:

- cures disease, prevents disease, lowers blood sugar, improves hypertension, boosts immunity, detox, changes constitution, lose weight just by drinking, no rebound, anyone can lose weight

Finance / investment:

- guaranteed profit, principal guaranteed, no loss, no risk, passive income guaranteed, anyone can make monthly income, instant money, guaranteed approval, debt disappears, guaranteed yield

UGC/testimonials:

- fake reviews, fake customers, fake sales, fake awards, "not sponsored," generated person presenting as a real buyer

## 9. Creative Center / Top Ads Analysis Schema

Use Top Ads as structure inspiration, not asset source. Do not copy captions, footage, people, music, logos, or editing.

Save:

- source ID
- check date
- URL/reference name
- region
- industry
- objective
- sort mode
- ad format: Spark, Non-Spark, unknown
- duration
- first frame: face, product, hand, text, screen recording, location
- 0-2s hook line
- hook type: problem, surprise, result, comparison, demo, story
- product presentation second
- brand presentation second
- CTA
- comment prompt
- subtitle volume and position
- audio type
- cut speed
- viewer emotion
- LP promise match
- review risk
- extracted winning structure
- elements not to copy
- next Seedance application

Templates:

- `workspace/prompts/tiktok-top-ads-analysis.csv`
- `workspace/prompts/tiktok-top-ads-analysis.md`

## 10. A/B Test Planning

Principles:

- Test one main variable at a time.
- For CV, do not decide by CTR alone.
- Hold inconclusive results when sample size is insufficient.
- Keep targeting, objective, budget, period, LP, CTA, and optimization event as fixed as practical when testing creatives.
- Feed winning elements, not whole copies, back into Seedance.

Priority order:

1. Hook: 0.0-1.5s
2. First subject: face, hand, product, screen
3. Product presentation timing: 1.5s, 3s, 5s
4. CTA wording
5. LP promise
6. Proof type: demo, how-to, comparison point, review quote with rights

Template: `workspace/prompts/tiktok-ab-test-plan.csv`

## 11. Post-Launch Learning

Collect:

- campaign, ad group, creative ID/name
- delivery period and spend
- impressions, reach, CPM
- 2s view, 6s focused view
- 25/50/75/100% views
- CTR, CPC, LP arrival
- CV, CVR, CPA, ROAS
- saves, comments, shares, negative reactions
- review status/rejection reason
- LP/tracking changes
- comment themes

Then assign one diagnosis tag and write the next Seedance brief:

```markdown
Goal: CV
Diagnosis tag: {{HOOK_FIX / BODY_FIX / PRODUCT_FIX / CTA_FIX / LP_FIX / KEEP_SCALE}}
Keep:
- {{winning hook type}}
- {{winning product timing}}
- {{winning CTA}}
Change:
- {{first frame / person / product timing / CTA / subtitles / LP promise}}
Constraints:
- product/category within 3s
- one CTA type
- no fake testimonials
- no beauty/health/finance guarantees
- check AIGC disclosure
Output:
1. four 2s hooks
2. 15s script
3. Seedance visual prompt
4. subtitle/telop plan
5. NG expression check
6. A/B registration row
```

Templates:

- `workspace/prompts/tiktok-post-launch-learning.csv`
- `workspace/prompts/tiktok-seedance-feedback-prompt.md`

## 12. Human Approval Gate

Before upload/publish, either human approval or a valid run-permission manifest must confirm:

- ad send/publish/campaign/budget/bid/date/targeting/billing/account actions are explicitly allowed, or AI stops before them
- product name, price, discount, deadline, conditions match LP
- LP first view answers the ad promise
- proof, No.1, satisfaction, reviews, ranking, awards, expert claims have evidence
- generated people do not present fake real-world testimonials
- AIGC/AI voice/generated avatar disclosure need is checked
- rights for face, logo, music, facility, post, review, comment, screenshot are checked
- subtitle, voice, on-screen text, and CTA have no NG expressions
- key text/logos are inside safe zones
- Pixel / Events API / standard events / UTM are checked
- mobile LP, form/purchase/reservation path, privacy policy, terms/disclaimers work

Template: `workspace/prompts/tiktok-preflight-human-approval.md`

## 13. Source Log

Do not hard-code changing specs without a check date. Use official sources before launch.

| Source ID | Source | Use | Checked |
|---|---|---|---|
| TT-SRC-001 | TikTok Business Help Center: TikTok Auction In-Feed Ads | Spark/Non-Spark specs, safe zone | 2026-06-29 |
| TT-SRC-002 | TikTok Business Help Center: Creative best practices for performance ads | 9:16, 720p, first 3s, hook, CTA, creative refresh | 2026-06-29 |
| TT-SRC-003 | TikTok Business Help Center: About Events API | Pixel + Events API, web conversions prerequisite | 2026-06-29 |
| TT-SRC-004 | TikTok Business Help Center: Standard Events and Parameters | event names and privacy constraints | 2026-06-29 |
| TT-SRC-005 | TikTok Business Help Center: Advertising Policies | policy areas and high-risk categories | 2026-06-29 |
| TT-SRC-006 | TikTok Advertising Policies: Misleading and false content | exaggerated claims, LP mismatch, clickbait, AIGC, identity misuse | 2026-06-29 |
| TT-SRC-007 | TikTok Business Help Center: Split Testing | split test setup and schedule/key metric | 2026-06-29 |
| TT-SRC-008 | TikTok Creative Center: Top Ads | structure analysis input | 2026-06-29 |
| JP-SRC-001 | Consumer Affairs Agency:景品表示法 | misleading representation and stealth marketing risk | 2026-06-29 |
| JP-SRC-002 | MHLW:医薬品等の広告規制 | pharma/medical ad risk | 2026-06-29 |
| JP-SRC-003 | FSA: financial advertising guidance | finance/investment ad risk | 2026-06-29 |
