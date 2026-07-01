const PAGE_API = "/api/factory-data";
const PAGE_STATE_PATH = "state/generation-state.json";
const PAGE_LIBRARY_PATH = "state/asset-library.json";

const PAGE_NAV = [
  { id: "factory", label: "ダッシュボード", href: "live-workflow.html", note: "全体管制" },
  { id: "generation-review", label: "生成レビュー", href: "generation-review.html", note: "承認判断" },
  { id: "storyboard", label: "絵コンテ", href: "storyboard.html", note: "画像確認" },
  { id: "studio-lines", label: "制作ライン", href: "studio-lines.html", note: "工程フロー" },
  { id: "assets", label: "素材", href: "assets.html", note: "入力可否" },
  { id: "cast-library", label: "演者（キャスト）", href: "cast-library.html", note: "権利範囲" },
  { id: "script", label: "台本", href: "script.html", note: "秒割り" },
  { id: "jobs", label: "ジョブ", href: "jobs.html", note: "生成キュー" },
  { id: "gates", label: "ゲート", href: "gates.html", note: "承認停止" },
  { id: "publish", label: "発信（配信）", href: "publish.html", note: "公開準備" },
  { id: "activity", label: "履歴", href: "activity.html", note: "監査ログ" },
];

const PAGE_META = {
  factory: {
    title: "ダッシュボード",
    subtitle: "AI動画制作コントロールルーム",
    intent: "何を作っていて、どこで止まり、次に何をすれば進むかを見る。",
    source: "/api/factory-data",
    decision: "次にやることとブロック理由を確認する。",
  },
  "generation-review": {
    title: "生成レビュー",
    subtitle: "Seedance投入前の承認判断",
    intent: "Blender構図コンポと写真キー候補を分け、Seedanceへ進めるかを判断する。",
    source: "generation-state.json / storyboard / jobs / blender_assets",
    decision: "承認済み写真キー画像があるか確認する。",
  },
  storyboard: {
    title: "絵コンテ",
    subtitle: "生成絵コンテ・素材・台本の確認",
    intent: "Seedance本番前に、絵コンテ、素材3枚、秒割り、音声/字幕方針を一画面で確認する。",
    source: "project-state.json / generated storyboard / product references",
    decision: "この絵コンテでSeedance条件提示へ進めるかを判断する。",
  },
  generation: {
    title: "生成レビュー",
    subtitle: "Seedance投入前の承認判断",
    intent: "Blender構図コンポと写真キー候補を分け、Seedanceへ進めるかを判断する。",
    source: "generation-state.json / storyboard / jobs / blender_assets",
    decision: "承認済み写真キー画像があるか確認する。",
  },
  "studio-lines": {
    title: "制作ライン",
    subtitle: "実データに連動する工程レーン",
    intent: "工程ごとに、AIがどこまで進み、どこで人間承認待ちになっているかを見る。",
    source: "generation-state.json / workflow[] / current_work",
    decision: "active工程の次に、何をCodexへ指示するかを決める。",
  },
  assets: {
    title: "素材",
    subtitle: "ローカル素材棚と3Dレーン",
    intent: "生成前に、使える素材、source captures、Blender/3Dレーン、ブロック済み記録を確認する。",
    source: "asset-library.json / cast manifest / videos/**/source-captures / workspace/assets/3d / blender status",
    decision: "Seedanceへ渡す素材と、ローカル3D preview plateを使うかを決める。",
  },
  "cast-library": {
    title: "演者ライブラリ",
    subtitle: "AI演者と利用範囲",
    intent: "AI演者の名前、役割、利用範囲、権利ステータスを見て、次の動画の配役を決める。",
    source: "workspace/assets/cast/generated_20260629/cast-manifest.json",
    decision: "主参照に使う1人と、背景/カメオに回す演者を選ぶ。",
  },
  script: {
    title: "台本",
    subtitle: "60秒物語の秒割り・ナレーション・テロップ",
    intent: "Seedance生成前に、映像、ナレーション、字幕の同期を確認する。",
    source: "generation-state.json / script.beats[]",
    decision: "この台本で音声生成と字幕編集へ進めるかを確認する。",
  },
  jobs: {
    title: "ジョブ",
    subtitle: "Seedanceクリップキューと費用状態",
    intent: "4本のSeedanceクリップの状態、見積、結果、レビューを追う。",
    source: "generation-state.json / jobs[]",
    decision: "見積未完了ならcost estimate、承認後だけ生成へ進む。",
  },
  gates: {
    title: "ゲート",
    subtitle: "安全ロックと承認停止",
    intent: "権利、費用、生成承認、広告公開の停止条件を一画面で見る。",
    source: "generation-state.json / gates[]",
    decision: "どのゲートが解除されるまで先へ進めないかを確認する。",
  },
  broadcast: {
    title: "発信（配信）",
    subtitle: "公開準備とパブリックサマリー",
    intent: "外から見ても、何を作っていて、どこで止め、次に何を判断するかが分かる形にする。",
    source: "generation-state.json / asset-library.json / source captures",
    decision: "公開前ブロックと投稿文を確認する。",
  },
  publish: {
    title: "発信（配信）",
    subtitle: "公開準備とパブリックサマリー",
    intent: "公開準備の最終確認と、発信に向けた判断・承認を行う。",
    source: "generation-state.json / asset-library.json / source captures",
    decision: "外部投稿はせず、承認に必要な情報だけ確認する。",
  },
  activity: {
    title: "履歴",
    subtitle: "Codex受信箱、更新ファイル、監査ログ",
    intent: "UIからCodexへ送った指示、状態更新、ファイル監視、git状態を監査する。",
    source: "codex-inbox.jsonl / activity[] / files.recent / git status",
    decision: "次の指示が届いているか、どのファイルが更新されたかを確認する。",
  },
};

const pageState = {
  page: document.body.dataset.page || "studio-lines",
  runtime: null,
  state: {},
  library: {},
  castManifest: {},
};

function html(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;",
  }[char]));
}

function toProjectPath(path) {
  if (!path) return "";
  if (/^https?:/.test(path) || path.startsWith("/")) return path;
  if (path.startsWith("state/")) return path;
  return "../../" + path;
}

function statusClass(status) {
  return String(status || "pending").toLowerCase().replace(/[^a-z0-9_-]/g, "_");
}

const STATUS_JA = {
  done: "完了",
  completed: "完了",
  approved: "承認済み",
  estimated: "見積済み",
  active: "進行中",
  generating: "生成中",
  rendering: "レンダー中",
  processing: "処理中",
  pending: "待機中",
  not_started: "未開始",
  blocked: "停止中",
  locked: "ロック中",
  captured: "取得済み",
  failed: "失敗",
  failed_review: "レビュー失敗",
  rejected: "却下",
  needs_revision: "修正必要",
  proposal: "提案中",
  ready: "準備完了",
  waiting_for_render: "レンダー待ち",
};

function statusJa(value) {
  return STATUS_JA[String(value || "").toLowerCase()] || String(value || "待機中");
}

function displayText(value) {
  return String(value ?? "")
    .replace(/^Clip\s+(\d+)/, "クリップ$1")
    .replaceAll("review pending", "レビュー待ち")
    .replaceAll("not estimated", "未見積")
    .replaceAll("Local-only Blender lane for 3D preview plates.", "3Dプレビュー用のローカルBlenderレーンです。")
    .replaceAll("Run workspace/scripts/render-blender-demo.sh", "workspace/scripts/render-blender-demo.sh を実行")
    .replaceAll("Run workspace/scripts/capture-blender-screen.sh", "workspace/scripts/capture-blender-screen.sh を実行")
    .replaceAll("No page renders", "ページレンダーなし")
    .replaceAll("No captures", "キャプチャなし")
    .replaceAll("No manifest", "マニフェストなし")
    .replaceAll("Empty", "空")
    .replaceAll("No inbox log in packaged mode", "配布モードでは受信箱ログなし");
}

function nowJst() {
  return new Intl.DateTimeFormat("ja-JP", {
    timeZone: "Asia/Tokyo",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(new Date());
}

function compactText(value, limit = 72) {
  const text = displayText(value).replace(/\s+/g, " ").trim();
  return text.length > limit ? `${text.slice(0, limit - 1)}...` : text;
}

function summaryText(value) {
  const text = displayText(value).replace(/\s+/g, " ").trim();
  return /(workspace\/|videos\/|assets\/|prompts\/|state\/|\.json|\.png|\.jpg|\.mp4|\.blend)/i.test(text) ? "証跡ファイルあり" : text;
}

function sourceLabel(value) {
  const text = String(value || "");
  return /(\/|\.json|workspace|state)/i.test(text) ? "ローカル状態データ" : text;
}

function imageRecord(path) {
  return path ? { path, exists: true, mtime_ns: Date.now() } : null;
}

function currentJob() {
  const jobs = pageState.state.jobs || [];
  return jobs.find(job => /generating|processing|active|failed|review|estimated/i.test(String(job.status || ""))) || jobs[0] || {};
}

function jobImage(job) {
  const panels = pageState.state.storyboard?.panels || [];
  const panel = panels.find(item => item.id === job.id || item.id === job.storyboard_panel) || {};
  return job.storyboard_image || job.reference_image || panel.generated_image || panel.reference_image || pageState.state.blender?.render_path || "";
}

function isBlenderDerived(path) {
  return /(^|\/)(blender|3d|renders?)\/|previs|viewport|blockout|render_plate|_panel_/i.test(String(path || ""));
}

function isSupportOnly(path) {
  return /lips|support|reference_only|crop/i.test(String(path || ""));
}

function jobPreview(job, className = "") {
  if (job.local_path) {
    return `<video class="${html(className)}" src="${html(toProjectPath(job.local_path))}" autoplay muted loop playsinline controls></video>`;
  }
  const image = jobImage(job);
  return image ? `<img class="${html(className)}" src="${html(toProjectPath(image))}" alt="${html(job.title || job.id || "生成プレビュー")}">` : `<div class="generation-placeholder">プレビュー待機中</div>`;
}

function blenderFrame() {
  const assets = pageState.runtime?.blender_assets || {};
  const screen = assets.screen_capture;
  return (screen?.exists && screen) || assets.latest_live_frame || assets.latest_render || imageRecord(pageState.state.blender?.render_path);
}

function clipNumberFrom(value) {
  const match = String(value || "").match(/clip[_\s-]?0?(\d+)/i);
  return match ? Number.parseInt(match[1], 10) : null;
}

function clipLabelFromJob(job) {
  const number = clipNumberFrom(job?.id) || clipNumberFrom(job?.title);
  return number ? `Clip ${number}` : "";
}

function beatsForJob(job) {
  const beats = pageState.state.script?.beats || [];
  const label = clipLabelFromJob(job);
  return label ? beats.filter(beat => String(beat.clip || "").toLowerCase() === label.toLowerCase()) : beats.slice(0, 3);
}

function materialsForJob(job, frame) {
  const referenceNote = job.reference_image
    ? (isBlenderDerived(job.reference_image) ? "Blender由来: 入力不可" : "写真キー候補: 要承認")
    : "";
  return [
    ["動画", job.local_path || job.output_path ? "レビュー対象あり" : ""],
    ["主参照", referenceNote || job.primary_reference],
    ["補助", job.secondary_reference ? "補助参照あり" : ""],
    ["絵コンテ", job.storyboard_image ? "構図コンポ / 入力不可" : ""],
    ["Blender", frame?.path || pageState.state.blender?.render_path ? "構図・動き設計専用" : ""],
  ].filter(([, value]) => value).slice(0, 5);
}

function workflowNodeClass(step) {
  const key = String(step?.status || "").toLowerCase();
  if (["done", "completed", "approved", "ready"].includes(key)) return "done";
  if (["active", "generating", "rendering", "processing", "estimated", "needs_revision", "failed", "failed_review"].includes(key)) return "active";
  if (["blocked", "locked"].includes(key)) return "locked";
  return "pending";
}

function firstWorkspacePath(value) {
  return String(value || "").match(/workspace\/[^\s,，)]+?\.(?:md|txt|json|jpg|jpeg|png|webp|mp4)/i)?.[0] || "";
}

function phaseLink(phase) {
  const state = pageState.state || {};
  const projectId = state.meta?.project_id || "macneo-pc-cm-15s";
  const storyboard = state.storyboard?.generated_contact_sheet_local_path || state.storyboard?.generated_contact_sheet;
  const paths = {
    brief: `workspace/projects/${projectId}/brief.md`,
    reference_assets: state.jobs?.[0]?.asset_manifest || "assets.html",
    preproduction_scope: `workspace/projects/${projectId}/preproduction-checklist.md`,
    storyboard_image: storyboard || state.storyboard?.generation_prompt,
    gate_storyboard: storyboard || `workspace/projects/${projectId}/storyboard-structure.md`,
    seedance_conditions: `workspace/projects/${projectId}/seedance-approval.md`,
    seedance_generation: state.jobs?.[0]?.prompt_path || "jobs.html",
    post_edit: "script.html",
  };
  return toProjectPath(firstWorkspacePath(phase.output || phase.note) || paths[phase.id] || "");
}

function p0StepClass(status) {
  const key = String(status || "").toLowerCase();
  if (["done", "completed", "approved"].includes(key)) return "done";
  if (["active", "generating", "review_ready"].includes(key)) return "current";
  if (["blocked", "locked"].includes(key)) return "blocked";
  return "pending";
}

function visualHandoff() {
  const state = pageState.state || {};
  const approvedKey = (state.jobs || []).find(job => /approved|ready/i.test(`${job.approval_status || ""} ${job.review_decision || ""}`) && job.reference_image && !isBlenderDerived(job.reference_image) && !isSupportOnly(job.reference_image));
  return {
    blenderRole: "構図参照 / Seedance入力不可",
    storyboardStatus: state.storyboard?.status || "pending",
    seedancePrimaryAllowed: Boolean(approvedKey),
    keyVisualPath: approvedKey?.reference_image || "",
    blockReason: approvedKey ? "承認済み写真キー画像があります" : "承認済みの写真キー画像が未確定です",
  };
}

function normalizeFactoryState(runtime, state, library) {
  const panels = state.storyboard?.panels || [];
  const jobs = state.jobs || [];
  const gates = state.gates || [];
  const handoff = visualHandoff();
  const firstJob = jobs[0] || {};
  return {
    project: state.meta?.project || state.script?.title || "新規CM",
    updatedAt: state.meta?.updated_at || runtime?.generated_at || "",
    blockReason: state.visual_handoff?.block_reason || state.block_reason || "承認待ちです",
    nextAction: state.current_work?.summary || state.meta?.operator_message || "生成条件を確認して承認する",
    handoff,
    panels,
    jobs,
    gates,
    counts: runtime?.counts || {},
    storyboardImage: state.storyboard?.generated_contact_sheet_local_path || state.storyboard?.generated_contact_sheet || panels[0]?.generated_image || "",
    blenderImage: state.blender?.render_path || firstJob.reference_image || panels[0]?.generated_image || "",
    supportImage: jobs.find(job => job.reference_image && isSupportOnly(job.reference_image))?.reference_image || "",
    keySlots: jobs.length ? jobs : [0, 1, 2, 3],
    approvedKeyCount: jobs.filter(job => /approved|ready/i.test(String(job.approval_status || job.status || ""))).length,
    library,
  };
}

async function pageJson(path) {
  const response = await fetch(`${path}?t=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function navMarkup() {
  return PAGE_NAV.map(item => `
    <a href="${item.href}" class="${item.id === pageState.page ? "active" : ""}" aria-current="${item.id === pageState.page ? "page" : "false"}">
      <strong>${html(item.label)}</strong>
      <span>${html(item.note)}</span>
    </a>
  `).join("");
}

function shellMarkup() {
  const meta = PAGE_META[pageState.page] || PAGE_META["studio-lines"];
  return `
    <div class="scanline" aria-hidden="true"></div>
    <div class="noise" aria-hidden="true"></div>
    <div class="app-shell">
      <aside class="left-rail">
        <div class="brand-lockup">
          <span class="brand-mark"></span>
          <div>
          <h1>生成工場</h1>
          <p>AI動画制作スタジオ</p>
          </div>
        </div>
        <nav class="rail-nav">${navMarkup()}</nav>
        <section class="rail-card rail-status-card">
          <span class="eyebrow">現在ページ</span>
          <strong>${html(meta.title)}</strong>
          <p>${html(meta.subtitle)}</p>
          <small id="loadStatus">接続中...</small>
        </section>
        <section class="rail-card rail-purpose-card">
          <span class="eyebrow">見るもの</span>
          <p>${html(meta.intent)}</p>
          <code>${html(sourceLabel(meta.source))}</code>
        </section>
      </aside>
      <main class="factory-page detail-page">
        <header class="top-command-bar">
          <div class="top-title">
            <h2>${html(meta.title)}</h2>
            <p>${html(meta.subtitle)}</p>
          </div>
          <div class="top-status-grid">
            <div class="status-tile"><span>システム時刻</span><strong id="systemTime">--:--:--</strong><small>JST</small></div>
            <div class="status-tile live"><span>稼働状態</span><strong>ローカル稼働中</strong><small>外部生成は実行しない</small></div>
            <div class="status-tile"><span>プロジェクト</span><strong id="projectName">読み込み中</strong><small>Seedance劇場</small></div>
          </div>
          <div class="theater-lockup">
            <h2>SEEDANCE劇場</h2>
            <p>ローカル制作データ室</p>
          </div>
        </header>
        <section class="detail-hero" id="pageHero"></section>
        <section class="detail-content" id="pageContent"></section>
      </main>
    </div>
  `;
}

function renderHero() {
  const meta = PAGE_META[pageState.page] || PAGE_META["studio-lines"];
  const counts = pageState.runtime?.counts || {};
  const target = document.getElementById("pageHero");
  if (["factory", "generation", "generation-review", "assets", "publish", "broadcast"].includes(pageState.page)) {
    target.hidden = true;
    target.innerHTML = "";
    return;
  }
  target.hidden = false;
  target.innerHTML = `
    <article class="hero-intent">
      <span class="eyebrow">目的</span>
      <h3>${html(meta.intent)}</h3>
      <p>${html(meta.decision)}</p>
    </article>
    <article class="hero-source">
      <span class="eyebrow">実データ連携</span>
      <h3>${html(meta.source)}</h3>
      <div class="binding-grid">
        <div><span>ジョブ</span><strong>${counts.jobs ?? 0}</strong></div>
        <div><span>演者</span><strong>${counts.generated_cast_files ?? 0}</strong></div>
        <div><span>キャプチャ</span><strong>${counts.source_capture_files ?? 0}</strong></div>
        <div><span>停止ゲート</span><strong>${counts.blocked_gates ?? 0}</strong></div>
      </div>
    </article>
  `;
}

function panel({ eyebrow, title, body, className = "", badge = "" }) {
  return `
    <section class="page-panel cockpit-panel ${className}">
      <div class="panel-heading">
        <div><span class="eyebrow">${html(eyebrow)}</span><h3>${html(title)}</h3></div>
        ${badge ? `<span class="thin-pill">${html(badge)}</span>` : ""}
      </div>
      ${body}
    </section>
  `;
}

function miniStats(items) {
  return `<div class="cockpit-stats">${items.map(([label, value]) => `
    <div><span>${html(label)}</span><strong>${html(value ?? 0)}</strong></div>
  `).join("")}</div>`;
}

function compactList(items, empty = "表示データなし") {
  return `<div class="compact-list">${items.length ? items.map(item => `
    <article>
      <strong>${html(item.title || "")}</strong>
      <span>${html(item.meta || "")}</span>
      ${item.note ? `<p>${html(item.note)}</p>` : ""}
    </article>
  `).join("") : `<article><strong>${html(empty)}</strong><span>state待機中</span></article>`}</div>`;
}

function imageCard(src, title, note = "") {
  return `
    <article class="image-card">
      ${src ? `<img src="${html(toProjectPath(src))}" alt="${html(title)}">` : `<div class="image-placeholder">NO IMAGE</div>`}
      <strong>${html(title)}</strong>
      <span>${html(note)}</span>
    </article>
  `;
}

function workflowCards(workflow) {
  return `<div class="cockpit-flow">${workflow.map((phase, index) => `
    <a class="${statusClass(phase.status)}" href="${html(phaseLink(phase))}">
      <i>${String(index + 1).padStart(2, "0")}</i>
      <strong>${html(compactText(phase.label || phase.id || "工程", 18))}</strong>
      <span>${html(statusJa(phase.status))}</span>
      <small>${html(compactText(summaryText(phase.output || phase.note || ""), 42))}</small>
    </a>
  `).join("")}</div>`;
}

function renderFactory() {
  const data = normalizeFactoryState(pageState.runtime, pageState.state || {}, pageState.library || {});
  const steps = pageState.state.workflow || [];
  return `
    <section class="p0-dashboard">
      <article class="p0-hero p0-blocked">
        <div>
          <span class="danger-label">BLOCKED</span>
          <h3>${html(data.project)}</h3>
          <p class="p0-lead">写真キー画像を生成・レビュー・承認するまで、Seedance生成と公開工程は止めます。</p>
          <dl class="p0-status-lines">
            <div><dt>ブロック理由</dt><dd>${html(data.blockReason)}</dd></div>
            <div><dt>Seedance</dt><dd>禁止</dd></div>
            <div><dt>音声・字幕・Palmier</dt><dd>映像承認後</dd></div>
          </dl>
        </div>
        <a class="p0-blender-mini" href="${html(toProjectPath(data.storyboardImage || data.blenderImage))}">
          ${data.storyboardImage || data.blenderImage ? `<img src="${html(toProjectPath(data.storyboardImage || data.blenderImage))}" alt="生成絵コンテ">` : `<div class="image-placeholder">STORYBOARD</div>`}
          <strong>${data.storyboardImage ? "生成絵コンテ" : "構図ソース"}</strong>
          <span>${data.storyboardImage ? "クリックで画像を開く" : "composition_only / Seedance入力不可"}</span>
        </a>
      </article>
      <aside class="p0-next">
        <span class="eyebrow">次にやること（最優先）</span>
        <h3>4枚の写真キー画像を生成・レビュー・承認する</h3>
        <ol>
          <li>Blender構図から写実キーを4枚作る</li>
          <li>レビュー画面で構図と質感を確認</li>
          <li>承認済みだけSeedance候補にする</li>
          <li>承認まで動画・音声・公開は禁止</li>
        </ol>
        <a href="generation-review.html">生成レビューへ</a>
      </aside>
      <section class="p0-panel p0-pipeline">
        <div class="p0-panel-head"><span>制作パイプライン</span><strong>各カードをクリックで素材へ移動</strong></div>
        <div class="p0-steps">
          ${steps.map((step, index) => `
            <a class="${p0StepClass(step.status)}" href="${html(phaseLink(step))}">
              <i>${String(index + 1).padStart(2, "0")}</i>
              <strong>${html(step.label || step.id || "工程")}</strong>
              <span>${html(statusJa(step.status))}</span>
              <small>${html(compactText(summaryText(step.output || step.note || ""), 34))}</small>
            </a>
          `).join("")}
        </div>
      </section>
      <section class="p0-panel p0-summary">
        <div class="p0-panel-head"><span>現在の状況サマリー</span><strong>判断だけ表示</strong></div>
        <div class="p0-metrics">
          <article><span>工程の現在地</span><strong>04 写真キー生成待ち</strong></article>
          <article><span>ブロック</span><strong>写真キー未承認</strong></article>
          <article><span>写真キー</span><strong>${data.approvedKeyCount}/4 承認</strong></article>
          <article><span>公開可否</span><strong>公開不可</strong></article>
        </div>
      </section>
      <section class="p0-panel">
        <div class="p0-panel-head"><span>安全ゲート概要</span><strong>Seedance / 公開は停止</strong></div>
        <div class="p0-gate-list">
          <span class="bad">写真キー承認: 未承認</span>
          <span class="bad">Seedance生成: 禁止</span>
          <span class="warn">音声・字幕: 映像承認後</span>
          <span class="ok">ローカル限定: ON</span>
        </div>
      </section>
      <section class="p0-panel">
        <div class="p0-panel-head"><span>役割</span><strong>混同禁止</strong></div>
        <div class="p0-role-grid">
          <article><b>Blender</b><span>composition_only</span><em>Seedance入力不可</em></article>
          <article><b>Higgsfield image2 / Key visual</b><span>visual_truth</span><em>承認後のみ入力候補</em></article>
          <article><b>Seedance</b><span>motion_truth</span><em>写真キー承認後</em></article>
        </div>
      </section>
    </section>
  `;
}

function renderStudioLines() {
  const workflow = pageState.state.workflow || [];
  return `
    ${panel({ eyebrow: "制作ライン", title: "現在の生成フロー", className: "wide", body: workflowCards(workflow) })}
    ${panel({
      eyebrow: "現在の作業",
      title: pageState.state.current_work?.title || pageState.state.meta?.active_stage || "待機中",
      body: `<p class="compact-copy">${html(pageState.state.current_work?.summary || pageState.state.meta?.operator_message || "")}</p>`,
    })}
    ${panel({
      eyebrow: "実データ",
      title: "工程サマリー",
      body: miniStats([["工程", workflow.length], ["ジョブ", pageState.state.jobs?.length || 0], ["ゲート", pageState.state.gates?.length || 0], ["停止", pageState.runtime?.counts?.blocked_gates || 0]]),
    })}
  `;
}

function renderAssets() {
  const data = normalizeFactoryState(pageState.runtime, pageState.state || {}, pageState.library || {});
  const lib = data.library || {};
  const refs = lib.external_references || [];
  const cast = pageState.castManifest?.cast || [];
  const blenderCards = data.panels.slice(0, 4).map(panel => ({
    title: panel.title || panel.id,
    image: panel.generated_image,
    kind: "blender_previs",
    role: "composition_only",
    approval: "承認構図",
    rights: "OK",
    allowed: false,
  }));
  const keyCards = data.keySlots.map((_, index) => ({
    title: `写真キー候補0${index + 1}`,
    image: "",
    kind: "photoreal_key_visual",
    role: "visual_truth",
    approval: "未生成",
    rights: "未確認",
    allowed: false,
  }));
  const supportCards = data.supportImage ? [{
    title: "Rina唇クロップ",
    image: data.supportImage,
    kind: "support_reference_only",
    role: "lips-skin-tone only",
    approval: "補助",
    rights: "OK",
    allowed: false,
  }] : [];
  const refCards = refs.slice(0, 2).map(item => ({
    title: item.id || "外部参考",
    image: item.thumbnail_path || item.path,
    kind: "external_reference",
    role: "reference_only",
    approval: "参考のみ",
    rights: item.rights_status || "要確認",
    allowed: false,
  }));
  const cards = [...blenderCards, ...keyCards, ...supportCards, ...refCards];
  return `
    <section class="p0-assets">
      <header class="p0-page-alert">
        <div>
          <span class="warn-label">素材分類</span>
          <h3>Blenderプレビューは構図検討専用です</h3>
          <p>Seedance入力不可。承認済みphotoreal key visualだけがSeedance入力候補になります。</p>
        </div>
      </header>
      <section class="p0-panel p0-asset-summary">
        <div class="p0-metrics">
          <article><span>総素材</span><strong>${cards.length}</strong></article>
          <article><span>Blender</span><strong>${blenderCards.length}</strong></article>
          <article><span>写真キー承認済み</span><strong>0</strong></article>
          <article><span>Seedance入力可</span><strong>0</strong></article>
          <article><span>キャスト</span><strong>${cast.length}</strong></article>
        </div>
      </section>
      <section class="p0-panel p0-handoff">
        <div class="p0-panel-head"><span>ハンドオフフロー</span><strong>Blender -> 写真キー -> 承認 -> Seedance</strong></div>
        <div class="asset-handoff-flow">
          <article class="blocked"><strong>Blenderプレビュー</strong><span>構図のみ / 入力不可</span></article>
          <article><strong>Higgsfield image2</strong><span>写真キー化</span></article>
          <article><strong>承認</strong><span>人間レビュー</span></article>
          <article class="ready"><strong>Seedance入力可</strong><span>承認済みのみ</span></article>
        </div>
      </section>
      <nav class="p0-tabs">
        ${["すべて", "Blender", "ストーリーボード", "商品素材", "キャスト", "外部参考"].map((tab, index) => `<span class="${index === 0 ? "active" : ""}">${html(tab)}</span>`).join("")}
      </nav>
      <section class="p0-asset-grid">
        ${cards.map(card => `
          <article class="${card.allowed ? "allowed" : "blocked"}">
            ${card.image ? `<img src="${html(toProjectPath(card.image))}" alt="${html(card.title)}">` : `<div class="p0-asset-empty">未生成</div>`}
            <strong>${html(card.title)}</strong>
            <div class="p0-badges">
              ${assetBadges(card).map(label => `<span>${html(label)}</span>`).join("")}
            </div>
          </article>
        `).join("")}
      </section>
    </section>
  `;
}

function assetBadges(card) {
  const kind = {
    blender_previs: "Blender",
    photoreal_key_visual: "写真キー",
    support_reference_only: "補助参照",
    external_reference: "外部参考",
  }[card.kind] || card.kind;
  const role = {
    composition_only: "構図のみ",
    visual_truth: "画作り",
    "lips-skin-tone only": "唇色参照",
    reference_only: "参考のみ",
  }[card.role] || card.role;
  const status = card.allowed ? "入力可" : card.kind === "photoreal_key_visual" ? "未生成" : "入力不可";
  return [kind, role, status].filter(Boolean);
}

function renderCastLibrary() {
  const cast = pageState.castManifest?.cast || [];
  return `
    ${panel({ eyebrow: "AI演者ライブラリ", title: `${cast.length}人の生成演者`, className: "wide", badge: "使用中ライブラリ", body: `
      <div class="cast-compact-grid">
        ${cast.map(item => `
          <article class="cast-compact-card">
            <img src="${html(toProjectPath(item.asset_path))}" alt="${html(item.name)}">
            <strong>${html(item.name)}</strong>
            <span>${html(compactText(item.id, 28))}</span>
            <p>${html(compactText(displayText(item.role), 54))}</p>
            <em>${html(compactText(displayText(item.rights_status || item.use_scope), 24))}</em>
          </article>
        `).join("")}
      </div>
    ` })}
  `;
}

function renderScript() {
  const script = pageState.state.script || {};
  const beats = script.beats || [];
  const voiceLines = script.voice_script?.length ? script.voice_script : beats.map(beat => beat.narration).filter(Boolean);
  const telopLines = script.telop_plan?.length ? script.telop_plan : beats.map(beat => beat.telop).filter(Boolean);
  return `
    ${panel({ eyebrow: "台本", title: script.title || "台本未登録", className: "wide", badge: statusJa(script.status || "done"), body: `
      <div class="script-timeline">
        ${beats.map(beat => `
          <article>
            <time>${html(beat.time || "")}</time>
            <strong>${html(beat.clip || "")}</strong>
            <p>${html(compactText(beat.visual || "", 84))}</p>
            <span>${html(compactText(beat.telop || beat.narration || "", 42))}</span>
          </article>
        `).join("") || `<article><strong>台本未登録</strong><p>generation-state.json 待機中</p></article>`}
      </div>
    ` })}
    ${panel({ eyebrow: "音声", title: script.voice || "Higgsfield ElevenLabs", body: compactList(voiceLines.slice(0, 12).map((line, index) => ({ title: `${index + 1}`, meta: line })), "音声台本なし") })}
    ${panel({ eyebrow: "字幕", title: script.subtitles || "後編集", body: compactList(telopLines.slice(0, 12).map((line, index) => ({ title: `${index + 1}`, meta: line })), "字幕なし") })}
  `;
}

function renderJobs() {
  const jobs = pageState.state.jobs || [];
  return `
    ${panel({ eyebrow: "Seedanceジョブ", title: "生成キューとレビュー", className: "wide", badge: "承認必須", body: `
      <div class="job-card-grid">
        ${jobs.map(job => `
          <article class="${statusClass(job.status)}">
            ${jobPreview(job, "job-card-media")}
            <div>
              <strong>${html(displayText(job.title || job.id))}</strong>
              <span>${html(statusJa(job.status))} / ${html(job.duration_seconds ? `${job.duration_seconds}s` : "-")} / ${html(job.aspect_ratio || "-")}</span>
              <p>${html(compactText(job.rejection_reason || job.note || "", 76))}</p>
              <em>${html(job.cost_credits || "未見積")} credits</em>
            </div>
          </article>
        `).join("") || `<article><div></div><strong>ジョブなし</strong><span>state待機中</span></article>`}
      </div>
    ` })}
  `;
}

function renderGates() {
  const gates = pageState.state.gates || [];
  return `
    ${panel({ eyebrow: "安全ゲート", title: "生成・公開前の停止条件", className: "wide", body: `
      <div class="gate-signal-grid">
        ${gates.map(gate => `
          <article class="${statusClass(gate.status)}">
            <i></i>
            <strong>${html(gate.label || gate.id)}</strong>
            <span>${html(statusJa(gate.status))}</span>
            <small>${html(gate.id || "")}</small>
          </article>
        `).join("") || `<article><i></i><strong>ゲートなし</strong><span>待機中</span></article>`}
      </div>
    ` })}
  `;
}

function renderGeneration() {
  const data = normalizeFactoryState(pageState.runtime, pageState.state || {}, pageState.library || {});
  const usesBlender = pageState.state.visual_handoff?.blender_role !== "not_used";
  const sourceTitle = usesBlender ? "Blender構図（構図の正）" : "参照素材（商品の正）";
  const sourceBadge = usesBlender ? "Seedance入力不可" : "承認後入力可";
  const sourceNote = usesBlender ? "構図・カメラ・動きの設計図です。画作りの正ではありません。" : "ユーザー提供の商品素材です。費用・権利・最終生成許可の確認後にSeedance参照へ進めます。";
  const candidateLabel = usesBlender ? "写真キー候補（画作りの正）" : "Seedance生成条件";
  const candidateStatus = pageState.state.seedance_generation_allowed ? "生成可" : "未承認";
  return `
    <section class="p0-review">
      <header class="p0-page-alert">
        <div>
          <span class="danger-label">BLOCKED</span>
          <h3>${html(data.blockReason)}</h3>
          <p>${html(data.nextAction)}</p>
        </div>
        <a href="assets.html">素材分類を見る</a>
      </header>
      <main class="p0-review-board">
        <article class="p0-review-card p0-blender-card">
          <div class="p0-card-head"><span>${html(sourceTitle)}</span><b>${html(sourceBadge)}</b></div>
          ${data.blenderImage ? `<img src="${html(toProjectPath(data.blenderImage))}" alt="${html(sourceTitle)}">` : `<div class="image-placeholder">SOURCE</div>`}
          <p>${html(sourceNote)}</p>
        </article>
        <article class="p0-review-card p0-key-card">
          <div class="p0-card-head"><span>${html(candidateLabel)}</span><b>${html(candidateStatus)}</b></div>
          <div class="p0-empty-key">
            <strong>${html(candidateStatus)}</strong>
            <span>${html(pageState.state.current_work?.status_text || "承認後に次工程へ進めます")}</span>
          </div>
          <p>UI承認は記録用です。実生成はmanifest/permissionゲートで別途止まります。</p>
        </article>
      </main>
      <aside class="p0-checklist">
        <div class="p0-panel-head"><span>承認チェックリスト</span><strong id="reviewChecklistCount">未完了 0/5</strong></div>
        <small id="reviewChecklistStatus" class="p0-checklist-status">未確認</small>
        ${["構図は意図通りか", "商品が美しく見えるか", "質感・ライティングの品質", "色味はブランドに合うか", "権利・素材の利用範囲"].map((item, index) => `<label><input type="checkbox" data-review-check="${index}"> ${html(item)}</label>`).join("")}
        <div class="p0-actions">
          <button type="button" id="reviewReject">差し戻し</button>
          <button type="button" id="reviewRequestChange">修正依頼</button>
          <button type="button" id="reviewApprove" disabled>承認する</button>
          <button type="button" id="reviewNext" disabled>次へ</button>
        </div>
      </aside>
      <section class="p0-key-slots">
        <div class="p0-panel-head"><span>4 key visual候補スロット</span><strong>0/4 生成済み</strong></div>
        <div>
          ${data.keySlots.map((_, index) => `
            <article>
              <i>0${index + 1}</i>
              <strong>${html(data.jobs[index]?.title || `候補 ${index + 1}`)}</strong>
              <span>${html(data.jobs[index]?.status || "not_generated")}</span>
              <small>${html(data.jobs[index]?.cost_credits ? `${data.jobs[index].cost_credits} credits` : "承認待ち")}</small>
            </article>
          `).join("")}
        </div>
      </section>
    </section>
  `;
}

function renderStoryboardPage() {
  const state = pageState.state || {};
  const storyboard = state.storyboard || {};
  const script = state.script || {};
  const beats = script.beats || [];
  const job = state.jobs?.[0] || {};
  const board = storyboard.generated_contact_sheet_local_path || storyboard.generated_contact_sheet || job.storyboard_image || "";
  const noncanonicalPreview = storyboard.noncanonical_preview_local_path || "";
  const requestPath = storyboard.canonical_storyboard_request || "";
  const contePath = storyboard.conte_spec || storyboard.structure_diagram || "";
  const keyRequests = storyboard.canonical_keyvisual_requests || [];
  const refs = [
    ["Hero lineup", "workspace/assets/brand/products/macneo/hero.webp"],
    ["Color gallery", "workspace/assets/brand/products/macneo/color-gallery.jpeg"],
    ["Blush closeup", "workspace/assets/brand/products/macneo/blush-product.jpg"],
  ];
  return `
    <section class="storyboard-review-page">
      <article class="storyboard-main-panel">
        <div class="p0-panel-head">
          <span>Higgsfield image2 絵コンテ</span>
          <strong>${html(statusJa(storyboard.status || "pending"))} / ${html(storyboard.approval_status || "未承認")}</strong>
        </div>
        ${board ? `<a href="${html(toProjectPath(board))}" target="_blank" rel="noopener"><img src="${html(toProjectPath(board))}" alt="MacNeo generated storyboard"></a>` : `<div class="image-placeholder">Higgsfield image2 絵コンテ未生成</div>`}
        <div class="storyboard-file-actions">
          ${requestPath ? `<a class="p0-link" href="${html(toProjectPath(requestPath))}" target="_blank" rel="noopener">Higgsfield request JSON</a>` : ""}
          ${contePath ? `<a class="p0-link" href="${html(toProjectPath(contePath))}" target="_blank" rel="noopener">コンテ仕様</a>` : ""}
        </div>
      </article>
      <aside class="storyboard-side-panel">
        <div class="p0-panel-head"><span>判断</span><strong>Seedance前</strong></div>
        <div class="p0-gate-list">
          <span class="${storyboard.status === "review_ready" ? "ok" : "warn"}">絵コンテ: ${html(statusJa(storyboard.status))}</span>
          <span class="warn">承認: ${html(storyboard.approval_status || "未承認")}</span>
          <span class="bad">Seedance: ${html(state.seedance_generation_allowed ? "許可" : "未許可")}</span>
          <span class="ok">正規ルート: Higgsfield MCP image2</span>
        </div>
        <a class="p0-link" href="generation-review.html">生成レビューへ</a>
      </aside>
      ${noncanonicalPreview ? `
        <section class="p0-panel storyboard-noncanonical-panel">
          <div class="p0-panel-head"><span>非正規プレビュー</span><strong>絵コンテではありません</strong></div>
          <a href="${html(toProjectPath(noncanonicalPreview))}" target="_blank" rel="noopener"><img src="${html(toProjectPath(noncanonicalPreview))}" alt="Non-canonical key visual preview"></a>
          <p class="compact-copy">これは過去に作った写真キープレビューです。Higgsfield image2の正規成果物ではないため、Seedance承認素材にはしません。</p>
        </section>
      ` : ""}
      ${keyRequests.length ? `
        <section class="p0-panel storyboard-keyrequest-panel">
          <div class="p0-panel-head"><span>写真キー request</span><strong>Higgsfield image2</strong></div>
          <div class="p0-gate-list">
            ${keyRequests.map(path => `<a class="p0-link" href="${html(toProjectPath(path))}" target="_blank" rel="noopener">${html(path)}</a>`).join("")}
          </div>
        </section>
      ` : ""}
      <section class="p0-panel storyboard-reference-panel">
        <div class="p0-panel-head"><span>使用素材</span><strong>3 references</strong></div>
        <div class="storyboard-ref-grid">
          ${refs.map(([title, src]) => imageCard(src, title, "Higgsfield image2 reference")).join("")}
        </div>
      </section>
      <section class="p0-panel storyboard-beat-panel">
        <div class="p0-panel-head"><span>15秒構成</span><strong>台本 / カメラ割り</strong></div>
        <div class="script-timeline">
          ${beats.map(beat => `
            <article>
              <time>${html(beat.time || "")}</time>
              <strong>${html(beat.telop || beat.caption || "")}</strong>
              <p>${html(beat.visual || "")}</p>
              <span>${html(beat.narration || "音楽/SFX")}</span>
            </article>
          `).join("")}
        </div>
      </section>
      <section class="p0-panel storyboard-notes-panel">
        <div class="p0-panel-head"><span>レビュー注意</span><strong>後編集前提</strong></div>
        <div class="p0-gate-list">
          ${(storyboard.review_notes || []).map(note => `<span class="warn">${html(note)}</span>`).join("") || `<span class="warn">字幕と macneo apple は後編集</span>`}
        </div>
      </section>
    </section>
  `;
}

function broadcastPostText() {
  const state = pageState.state || {};
  const project = compactText(state.meta?.project || state.script?.title || "新作リップCM", 34);
  return compactText(
    `${project}を制作中です。完成後に、商品の質感と余韻を丁寧に届ける短編映像として公開します。#ROUGENOIR #リップ #新作CM`,
    276,
  );
}

function renderBroadcast() {
  const data = normalizeFactoryState(pageState.runtime, pageState.state || {}, pageState.library || {});
  const post = broadcastPostText();
  return `
    <section class="p0-publish">
      <article class="p0-publish-hero p0-blocked">
        <span class="danger-label">公開不可 / BLOCKED</span>
        <h3>${html(data.project)}</h3>
        <p>理由: 写真キー画像未承認のため、まだ公開できません。</p>
        <div class="p0-gate-list">
          <span class="bad">外部投稿: 未実行</span>
          <span class="bad">人間承認: 必須</span>
          <span class="ok">ローカル限定: ON</span>
        </div>
      </article>
      <section class="p0-panel">
        <div class="p0-panel-head"><span>内部ステータス</span><strong>工場内の判断</strong></div>
        <div class="p0-publish-status">
          <label><input type="checkbox" disabled> 写真キー画像: 未生成 / 未承認</label>
          <label><input type="checkbox" disabled> Seedance生成: 禁止中</label>
          <label><input type="checkbox" disabled> 音声 / 字幕 / Palmier: 映像承認後</label>
          <label><input type="checkbox" disabled> 公開可否: 公開不可</label>
        </div>
      </section>
      <section class="p0-panel">
        <div class="p0-panel-head"><span>外向けコピー（ドラフト）</span><strong>内部失敗理由は混ぜない</strong></div>
        <textarea class="broadcast-post" id="broadcastPost" readonly>${html(post)}</textarea>
        <div class="broadcast-copy-row"><button type="button" id="copyBroadcastPost">コピー</button><span id="broadcastCopyStatus">未コピー</span></div>
      </section>
      <section class="p0-panel">
        <div class="p0-panel-head"><span>安全性・コンプライアンス</span><strong>公開前ゲート</strong></div>
        <div class="p0-gate-list">
          <span class="bad">有料生成: 未実行</span>
          <span class="bad">外部投稿: 未実行</span>
          <span class="warn">人間承認: 必須</span>
          <span class="ok">権利確認: UI上で分離</span>
        </div>
      </section>
      <section class="p0-panel">
        <div class="p0-panel-head"><span>次の判断</span><strong>公開ではなくレビューへ戻す</strong></div>
        <p class="compact-copy">写真キー画像4枚を生成し、レビュー画面で承認してください。承認まで発信導線はロックします。</p>
        <a class="p0-link" href="generation-review.html">生成レビューへ</a>
      </section>
    </section>
  `;
}

function renderActivity() {
  const activity = pageState.state.activity || [];
  const inbox = pageState.runtime?.inbox || [];
  const files = pageState.runtime?.files?.recent || [];
  return `
    ${panel({ eyebrow: "履歴", title: "状態監査ログ", body: compactList(activity.slice().reverse().slice(0, 18).map(item => ({ title: displayText(item.actor), meta: `${item.time} / ${displayText(item.event)}` })), "履歴なし") })}
    ${panel({ eyebrow: "Codex受信箱", title: `${inbox.length}件のメッセージ`, body: compactList(inbox.slice().reverse().slice(0, 12).map(item => ({ title: item.source || "UI", meta: item.time, note: item.message })), "受信箱は空") })}
    ${panel({ eyebrow: "監視ファイル", title: `${files.length}件の最近更新`, className: "wide", badge: `git ${pageState.runtime?.git?.changed_files ?? 0}`, body: compactList(files.slice(0, 18).map(file => ({ title: file.path, meta: `${file.mtime || ""} / ${file.bytes || 0} bytes` })), "更新ファイルなし") })}
  `;
}

function renderPageContent() {
  const renderers = {
    factory: renderFactory,
    generation: renderGeneration,
    "generation-review": renderGeneration,
    storyboard: renderStoryboardPage,
    "studio-lines": renderStudioLines,
    assets: renderAssets,
    "cast-library": renderCastLibrary,
    script: renderScript,
    jobs: renderJobs,
    gates: renderGates,
    broadcast: renderBroadcast,
    publish: renderBroadcast,
    activity: renderActivity,
  };
  document.getElementById("pageContent").innerHTML = (renderers[pageState.page] || renderStudioLines)();
  setupBroadcastCopy();
  setupGenerationCopy();
  setupReviewChecklist();
}

function setupReviewChecklist() {
  if (!document.querySelectorAll) return;
  const checks = [...document.querySelectorAll("[data-review-check]")];
  const count = document.getElementById("reviewChecklistCount");
  const status = document.getElementById("reviewChecklistStatus");
  const reject = document.getElementById("reviewReject");
  const requestChange = document.getElementById("reviewRequestChange");
  const approve = document.getElementById("reviewApprove");
  const next = document.getElementById("reviewNext");
  if (!checks.length || !count) return;
  const key = `seedance-review-checklist:${pageState.state.meta?.project || "default"}`;
  const storage = typeof localStorage === "undefined" ? null : localStorage;
  const saved = storage ? JSON.parse(storage.getItem(key) || "{}") : {};
  const save = nextState => storage?.setItem(key, JSON.stringify({ ...saved, ...nextState, updatedAt: new Date().toISOString() }));
  const update = () => {
    const done = checks.filter(input => input.checked).length;
    const allDone = done === checks.length;
    const decision = allDone ? JSON.parse(storage?.getItem(key) || "{}").decision : "";
    const approved = decision === "approved";
    count.textContent = approved ? `承認済み ${done}/${checks.length}` : allDone ? `確認済み ${done}/${checks.length}` : `未完了 ${done}/${checks.length}`;
    if (status) status.textContent = decision === "rejected" ? "差し戻し済み" : decision === "change_requested" ? "修正依頼済み" : approved ? "承認済み / 次へ進めます" : allDone ? "5項目確認済み。承認できます。" : "全項目の確認が必要です。";
    if (approve) approve.disabled = !allDone;
    if (next) next.disabled = !approved;
    save({ checks: Object.fromEntries(checks.map(input => [input.dataset.reviewCheck, input.checked])), decision: allDone ? decision : "" });
  };
  checks.forEach(input => {
    input.checked = Boolean(saved.checks?.[input.dataset.reviewCheck] ?? saved[input.dataset.reviewCheck]);
    if (!input.dataset.ready) {
      input.dataset.ready = "1";
      input.addEventListener("change", update);
    }
  });
  reject?.addEventListener("click", () => { save({ decision: "rejected" }); if (status) status.textContent = "差し戻し済み"; update(); });
  requestChange?.addEventListener("click", () => { save({ decision: "change_requested" }); if (status) status.textContent = "修正依頼済み"; update(); });
  approve?.addEventListener("click", () => { save({ decision: "approved" }); update(); });
  next?.addEventListener("click", () => { window.location.href = "jobs.html"; });
  update();
}

function setupBroadcastCopy() {
  const button = document.getElementById("copyBroadcastPost");
  const textarea = document.getElementById("broadcastPost");
  const status = document.getElementById("broadcastCopyStatus");
  if (!button || !textarea || button.dataset.ready) return;
  button.dataset.ready = "1";
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(textarea.value);
      status.textContent = "コピー済み";
    } catch {
      textarea.select();
      document.execCommand("copy");
      status.textContent = "コピー済み";
    }
  });
}

function setupGenerationCopy() {
  const button = document.getElementById("copyGenerationPost");
  const textarea = document.getElementById("generationPost");
  const status = document.getElementById("generationCopyStatus");
  if (!button || !textarea || button.dataset.ready) return;
  button.dataset.ready = "1";
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(textarea.value);
      status.textContent = "コピー済み";
    } catch {
      textarea.select();
      document.execCommand("copy");
      status.textContent = "コピー済み";
    }
  });
}

async function loadPageData() {
  try {
    let runtime = null;
    let state = null;
    let library = {};
    let castManifest = {};
    try {
      runtime = await pageJson(PAGE_API);
      state = runtime.state || {};
      library = runtime.library || {};
      castManifest = runtime.cast_manifest || {};
    } catch (apiError) {
      console.warn("factory API unavailable", apiError);
      state = await pageJson(PAGE_STATE_PATH);
      library = await pageJson(PAGE_LIBRARY_PATH).catch(() => ({}));
      if (library.generated_cast_manifest?.path) {
        castManifest = await pageJson(toProjectPath(library.generated_cast_manifest.path)).catch(() => ({}));
      }
    }
    pageState.runtime = runtime;
    pageState.state = state;
    pageState.library = library;
    pageState.castManifest = castManifest;
    document.getElementById("loadStatus").textContent = `${runtime?.local_server?.local_only ? "ローカルサーバー" : "静的表示"}: ${new Date().toLocaleTimeString()}`;
    document.getElementById("systemTime").textContent = nowJst();
    document.getElementById("projectName").textContent = state.meta?.project || "Seedance Theater";
    renderHero();
    renderPageContent();
  } catch (error) {
    document.getElementById("loadStatus").textContent = `読み込み失敗: ${error.message}`;
  }
}

document.body.innerHTML = shellMarkup();
loadPageData();
setInterval(loadPageData, 3500);
setInterval(() => {
  const clock = document.getElementById("systemTime");
  if (clock) clock.textContent = nowJst();
}, 1000);
