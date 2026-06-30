const PAGE_API = "/api/factory-data";
const PAGE_STATE_PATH = "state/generation-state.json";
const PAGE_LIBRARY_PATH = "state/asset-library.json";

const PAGE_NAV = [
  ["factory", "Factory", "live-workflow.html"],
  ["studio-lines", "Studio Lines", "studio-lines.html"],
  ["assets", "Assets", "assets.html"],
  ["cast-library", "Cast Library", "cast-library.html"],
  ["jobs", "Jobs", "jobs.html"],
  ["gates", "Gates", "gates.html"],
  ["activity", "Activity", "activity.html"],
];

const PAGE_META = {
  "studio-lines": {
    title: "Studio Lines",
    subtitle: "Workflow lanes tied to real state",
    intent: "工程ごとに、AIがどこまで進み、どこで人間承認待ちになっているかを見る。",
    source: "generation-state.json / workflow[] / current_work",
    decision: "active工程の次に、何をCodexへ指示するかを決める。",
  },
  assets: {
    title: "Assets",
    subtitle: "Local source shelves and 3D lanes",
    intent: "生成前に、使える素材、source captures、Blender/3Dレーン、ブロック済み記録を確認する。",
    source: "asset-library.json / cast manifest / videos/**/source-captures / blender status",
    decision: "Seedanceへ渡す素材と、ローカル3D previewを使うかを決める。",
  },
  "cast-library": {
    title: "Cast Library",
    subtitle: "AI actors and usage scope",
    intent: "AI演者の名前、役割、利用範囲、権利ステータスを見て、次の動画の配役を決める。",
    source: "workspace/assets/cast/generated_20260629/cast-manifest.json",
    decision: "主参照に使う1人と、背景/カメオに回す演者を選ぶ。",
  },
  jobs: {
    title: "Jobs",
    subtitle: "Seedance clip queue and cost state",
    intent: "4本のSeedanceクリップの状態、見積、結果、レビューを追う。",
    source: "generation-state.json / jobs[]",
    decision: "見積未完了ならcost estimate、承認後だけ生成へ進む。",
  },
  gates: {
    title: "Gates",
    subtitle: "Safety locks and approval stops",
    intent: "権利、費用、生成承認、広告公開の停止条件を一画面で見る。",
    source: "generation-state.json / gates[]",
    decision: "どのゲートが解除されるまで先へ進めないかを確認する。",
  },
  activity: {
    title: "Activity",
    subtitle: "Codex inbox, file updates, and audit trail",
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
  if (/^(https?:|data:|file:)/.test(path) || path.startsWith("/")) return path;
  if (path.startsWith("state/")) return path;
  return "../../" + path;
}

function statusClass(status) {
  return String(status || "pending").toLowerCase().replace(/[^a-z0-9_-]/g, "_");
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

async function pageJson(path) {
  const response = await fetch(`${path}?t=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function navMarkup() {
  return PAGE_NAV.map(([id, label, href]) => `
    <a href="${href}" class="${id === pageState.page ? "active" : ""}">${label}</a>
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
            <h1>GENERATION FACTORY</h1>
            <p>AI Video Production Studio</p>
          </div>
        </div>
        <nav class="rail-nav">${navMarkup()}</nav>
        <section class="rail-card">
          <span class="eyebrow">State file</span>
          <code>workspace/ui/state/generation-state.json</code>
          <p id="loadStatus">connecting...</p>
        </section>
        <section class="rail-card compact">
          <span class="eyebrow">Page intent</span>
          <strong>${html(meta.title)}</strong>
          <p>${html(meta.intent)}</p>
        </section>
      </aside>
      <main class="factory-page detail-page">
        <header class="top-command-bar">
          <div class="top-title">
            <h2>${html(meta.title)}</h2>
            <p>${html(meta.subtitle)}</p>
          </div>
          <div class="top-status-grid">
            <div class="status-tile"><span>System Time</span><strong id="systemTime">--:--:--</strong><small>JST</small></div>
            <div class="status-tile live"><span>Data Source</span><strong>LOCAL STATE</strong><small>${html(meta.source)}</small></div>
            <div class="status-tile"><span>Project</span><strong id="projectName">Loading</strong><small>Seedance Theater</small></div>
          </div>
          <div class="theater-lockup">
            <h2>SEEDANCE THEATER</h2>
            <p>Local Production Data Room</p>
          </div>
        </header>
        <section class="detail-hero" id="pageHero"></section>
        <section class="detail-content" id="pageContent"></section>
      </main>
    </div>
  `;
}

function renderHero() {
  const meta = PAGE_META[pageState.page];
  const counts = pageState.runtime?.counts || {};
  document.getElementById("pageHero").innerHTML = `
    <article class="hero-intent">
      <span class="eyebrow">Intent</span>
      <h3>${html(meta.intent)}</h3>
      <p>${html(meta.decision)}</p>
    </article>
    <article class="hero-source">
      <span class="eyebrow">Real Data Binding</span>
      <h3>${html(meta.source)}</h3>
      <div class="binding-grid">
        <div><span>Jobs</span><strong>${counts.jobs ?? 0}</strong></div>
        <div><span>Cast</span><strong>${counts.generated_cast_files ?? 0}</strong></div>
        <div><span>Captures</span><strong>${counts.source_capture_files ?? 0}</strong></div>
        <div><span>Blocked Gates</span><strong>${counts.blocked_gates ?? 0}</strong></div>
      </div>
    </article>
  `;
}

function renderStudioLines() {
  const workflow = pageState.state.workflow || [];
  return `
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">Studio Lines</span><h3>Workflow from real state</h3></div></div>
      <div class="line-board">
        ${workflow.map((phase, index) => `
          <article class="line-card ${statusClass(phase.status)}">
            <span class="thin-pill ${statusClass(phase.status)}">${html(phase.status)}</span>
            <h3>${String(index + 1).padStart(2, "0")} / ${html(phase.label)}</h3>
            <p>${html(phase.note)}</p>
            <div class="kv-grid"><span>Owner</span><strong>${html(phase.owner)}</strong><span>Output</span><strong>${html(phase.output)}</strong></div>
          </article>
        `).join("")}
      </div>
    </section>
    <section class="page-panel">
      <span class="eyebrow">Current Work</span>
      <h3>${html(pageState.state.current_work?.title || pageState.state.meta?.active_stage)}</h3>
      <p>${html(pageState.state.current_work?.summary || pageState.state.meta?.operator_message)}</p>
    </section>
  `;
}

function renderAssets() {
  const lib = pageState.library || {};
  const captures = lib.source_captures || [];
  const pageRenders = lib.page_renders || [];
  const refs = lib.external_references || [];
  const blocked = lib.blocked_assets || lib.removed_assets || [];
  const blender = pageState.runtime?.blender || {};
  return `
    <section class="page-panel">
      <div class="panel-heading"><div><span class="eyebrow">Asset Shelves</span><h3>Local source inventory</h3></div></div>
      <div class="binding-grid large">
        <div><span>Generated Cast</span><strong>${pageState.runtime?.counts?.generated_cast_files ?? 0}</strong></div>
        <div><span>Source Captures</span><strong>${captures.length}</strong></div>
        <div><span>Page Renders</span><strong>${pageRenders.length}</strong></div>
        <div><span>External References</span><strong>${refs.length}</strong></div>
        <div><span>Blocked Records</span><strong>${blocked.length}</strong></div>
      </div>
    </section>
    <section class="page-panel">
      <span class="eyebrow">Blender / 3D Preview Lane</span>
      <h3>${blender.available ? "available" : "unavailable"}</h3>
      <p>${html(blender.note || "Local-only Blender lane for 3D preview plates.")}</p>
      <div class="kv-grid"><span>CLI</span><strong>${html(blender.cli || "not found")}</strong><span>Mode</span><strong>${html(blender.mode || "local-only")}</strong></div>
    </section>
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">Page Renders</span><h3>Download-ready local renders</h3></div></div>
      <div class="data-list">
        ${pageRenders.map(item => `<article><strong>${html(item.name || item.id)}</strong><span>${html(item.type)} / ${html(item.path)}</span></article>`).join("") || "<article><strong>No page renders</strong><span>Run the local render capture step first</span></article>"}
      </div>
    </section>
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">Source Captures</span><h3>Workflow and operation captures</h3></div></div>
      <div class="data-list">
        ${captures.map(item => `<article><strong>${html(item.name || item.id)}</strong><span>${html(item.type)} / ${html(item.path)}</span></article>`).join("") || "<article><strong>No captures</strong><span>source captures folder is empty</span></article>"}
      </div>
    </section>
  `;
}

function renderCastLibrary() {
  const cast = pageState.castManifest?.cast || [];
  return `
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">AI Cast Library</span><h3>${cast.length} generated actors</h3></div><span class="thin-pill success">active library</span></div>
      <div class="cast-library-grid">
        ${cast.map(item => `
          <article class="cast-card">
            <img src="${html(toProjectPath(item.asset_path))}" alt="${html(item.name)}">
            <div>
              <h3>${html(item.name)}</h3>
              <span>${html(item.id)}</span>
              <p>${html(item.role)}</p>
              <div class="kv-grid"><span>Rights</span><strong>${html(item.rights_status)}</strong><span>Scope</span><strong>${html(item.use_scope)}</strong></div>
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderJobs() {
  const jobs = pageState.state.jobs || [];
  return `
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">Seedance Jobs</span><h3>Real job state</h3></div><span class="thin-pill danger">no paid generation executed</span></div>
      <div class="job-table">
        ${jobs.map(job => `
          <article class="job-row ${statusClass(job.status)}">
            <div><strong>${html(job.title)}</strong><span>${html(job.id)}</span></div>
            <div><span>Status</span><strong>${html(job.status)}</strong></div>
            <div><span>Reference</span><strong>${html(job.primary_reference || "-")}</strong></div>
            <div><span>Credits</span><strong>${html(job.cost_credits || "not estimated")}</strong></div>
            <div><span>Review</span><strong>${html(job.review || "pending")}</strong></div>
            <p>${html(job.note || "")}</p>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderGates() {
  const gates = pageState.state.gates || [];
  return `
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">Safety Gates</span><h3>Stops before generation and publishing</h3></div></div>
      <div class="gate-grid">
        ${gates.map(gate => `
          <article class="gate-detail ${statusClass(gate.status)}">
            <span class="thin-pill ${statusClass(gate.status)}">${html(gate.status)}</span>
            <h3>${html(gate.label)}</h3>
            <p>${html(gate.id)}</p>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderActivity() {
  const activity = pageState.state.activity || [];
  const inbox = pageState.runtime?.inbox || [];
  const files = pageState.runtime?.files?.recent || [];
  return `
    <section class="page-panel">
      <div class="panel-heading"><div><span class="eyebrow">Activity</span><h3>State audit trail</h3></div></div>
      <div class="data-list">${activity.slice().reverse().map(item => `<article><strong>${html(item.actor)}</strong><span>${html(item.time)} / ${html(item.event)}</span></article>`).join("")}</div>
    </section>
    <section class="page-panel">
      <div class="panel-heading"><div><span class="eyebrow">Codex Inbox</span><h3>${inbox.length} messages</h3></div></div>
      <div class="data-list">${inbox.slice().reverse().slice(0, 8).map(item => `<article><strong>${html(item.source || "UI")}</strong><span>${html(item.time)} / ${html(item.message || "")}</span></article>`).join("") || "<article><strong>Empty</strong><span>No inbox log in packaged mode</span></article>"}</div>
    </section>
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">Watched Files</span><h3>${files.length} recent files</h3></div><span class="thin-pill">git ${html(pageState.runtime?.git?.changed_files ?? 0)} changed</span></div>
      <div class="data-list">${files.map(file => `<article><strong>${html(file.path)}</strong><span>${html(file.mtime || "")} / ${html(file.bytes || 0)} bytes</span></article>`).join("")}</div>
    </section>
  `;
}

function renderPageContent() {
  const renderers = {
    "studio-lines": renderStudioLines,
    assets: renderAssets,
    "cast-library": renderCastLibrary,
    jobs: renderJobs,
    gates: renderGates,
    activity: renderActivity,
  };
  document.getElementById("pageContent").innerHTML = (renderers[pageState.page] || renderStudioLines)();
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
    document.getElementById("loadStatus").textContent = `${runtime?.local_server?.local_only ? "local server" : "static"}: ${new Date().toLocaleTimeString()}`;
    document.getElementById("systemTime").textContent = nowJst();
    document.getElementById("projectName").textContent = state.meta?.project || "Seedance Theater";
    renderHero();
    renderPageContent();
  } catch (error) {
    document.getElementById("loadStatus").textContent = `load failed: ${error.message}`;
  }
}

document.body.innerHTML = shellMarkup();
loadPageData();
setInterval(loadPageData, 3500);
setInterval(() => {
  const clock = document.getElementById("systemTime");
  if (clock) clock.textContent = nowJst();
}, 1000);
