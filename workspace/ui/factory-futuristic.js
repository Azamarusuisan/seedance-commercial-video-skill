const FACTORY_API = "/api/factory-data";
const STATE_PATH = "state/generation-state.json";
const LIBRARY_PATH = "state/asset-library.json";

// UI演出専用のmock telemetry。本物の市場データ、広告配信、生成結果ではない。
// 本番KPI、ジョブ、キュー、成果物は state/API の実データを使う。
const MOCK_GENERATION_DATA_UI_ONLY = {
  pipeline: [
    ["INGEST", "Complete", "complete"],
    ["ANALYZE", "Complete", "complete"],
    ["GENERATE", "Processing", "active"],
    ["RENDER", "76%", "active"],
    ["POST", "Pending", "pending"],
    ["DELIVER", "Locked", "locked"],
  ],
};

const appState = {
  tick: 0,
  runtime: null,
  state: {},
  library: {},
  castManifest: {},
  logTape: [
    "Line 04: Local factory server online",
    "Seedance queue locked until human approval",
    "ElevenLabs voice lane prepared",
    "Subtitle post-edit gate armed",
    "Publish blocked: human review required",
    "No paid generation executed",
  ],
  sendInFlight: false,
};

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;",
  }[char]));
}

function cls(value) {
  return String(value || "pending").replace(/[^a-zA-Z0-9_-]/g, "_").toLowerCase();
}

function toProjectPath(path) {
  if (!path) return "";
  if (/^(https?:|data:|file:)/.test(path) || path.startsWith("/")) return path;
  if (path.startsWith("state/")) return path;
  return "../../" + path;
}

function nowJstParts() {
  return new Intl.DateTimeFormat("ja-JP", {
    timeZone: "Asia/Tokyo",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(new Date());
}

async function loadJson(path) {
  const response = await fetch(`${path}?t=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function loadFactoryData() {
  const loadStatus = document.getElementById("loadStatus");
  try {
    let runtime = null;
    let state;
    let library = {};
    let castManifest = {};

    try {
      runtime = await loadJson(FACTORY_API);
      state = runtime.state || {};
      library = runtime.library || {};
      castManifest = runtime.cast_manifest || {};
    } catch (apiError) {
      console.warn("factory API unavailable; using static JSON", apiError);
      state = await loadJson(STATE_PATH);
      library = await loadJson(LIBRARY_PATH).catch(() => ({}));
      if (library.generated_cast_manifest?.path) {
        castManifest = await loadJson(toProjectPath(library.generated_cast_manifest.path)).catch(() => ({}));
      }
    }

    appState.runtime = runtime;
    appState.state = state;
    appState.library = library;
    appState.castManifest = castManifest;
    loadStatus.textContent = `${runtime?.local_server?.local_only ? "local server" : "static"}: ${new Date().toLocaleTimeString()}`;
    document.getElementById("connectionStatus").textContent = runtime?.local_server?.local_only ? "LOCAL ONLY" : "STATIC FALLBACK";
    renderAll();
  } catch (error) {
    loadStatus.textContent = `state load failed: ${error.message}`;
  }
}

function statusProgress(status) {
  const key = String(status || "").toLowerCase();
  if (["done", "completed", "approved"].includes(key)) return 100;
  if (["estimated"].includes(key)) return 68;
  if (["active", "generating", "rendering"].includes(key)) return 44;
  if (["processing"].includes(key)) return 32;
  if (["pending", "not_started"].includes(key)) return 8;
  if (["blocked", "locked"].includes(key)) return 0;
  return 12;
}

function estimatedCredits(jobs) {
  const values = (jobs || []).map(job => Number.parseFloat(String(job.cost_credits || "").replace(/[^\d.]/g, ""))).filter(Number.isFinite);
  if (!values.length || values.every(value => value === 0)) return null;
  return values.reduce((sum, value) => sum + value, 0);
}

function renderValue(value) {
  if (value === null || value === undefined || value === "") return "pending";
  if (typeof value === "number") return value.toLocaleString("ja-JP");
  return String(value);
}

function renderTop() {
  const state = appState.state;
  document.getElementById("systemTime").textContent = nowJstParts();
  document.getElementById("queueStatus").textContent = "LOCKED";

  const statusStrip = document.getElementById("statusStrip");
  const sourceRefs = state.assets?.source_ref_count ?? 0;
  const currentWork = state.current_work?.title || "Cost estimate active";
  statusStrip.innerHTML = [
    ["CURRENT WORK", currentWork, "magenta"],
    ["HUMAN APPROVAL", "REQUIRED", "warning"],
    ["PUBLISH", "BLOCKED", "danger"],
    ["SOURCE_REFS", String(sourceRefs), ""],
    ["LINE", "LIVE", "success"],
    ["VOICE", "ELEVENLABS", ""],
    ["SUBTITLE", "POST_EDIT", ""],
    ["PAID GENERATION", "NOT EXECUTED", "danger"],
  ].map(([label, value, tone]) => (
    `<span class="thin-pill ${tone}">${escapeHtml(label)} ${escapeHtml(value)}</span>`
  )).join("");
}

function renderMetrics() {
  const counts = appState.runtime?.counts || {};
  const jobs = appState.state.jobs || [];
  const credits = estimatedCredits(jobs);
  const blocked = counts.blocked_gates ?? (appState.state.gates || []).filter(gate => gate.status === "blocked").length;
  const metrics = [
    ["Active Stage", appState.state.meta?.active_stage || "pending", "state.meta.active_stage"],
    ["Planned Jobs", counts.jobs ?? jobs.length, "state.jobs.length"],
    ["Estimated Credits", credits === null ? "not estimated" : credits.toFixed(1), "jobs[].cost_credits"],
    ["Render Outputs", counts.render_outputs ?? 0, "local output files"],
    ["Cast Assets", counts.generated_cast_files ?? appState.state.assets?.generated_cast_count ?? 0, "cast manifest files"],
    ["Approval Gates", `${blocked} blocked`, "human approval required"],
  ];
  const row = document.getElementById("metricRow");
  row.innerHTML = metrics.map(([label, value, note]) => `
      <article class="metric-card">
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(renderValue(value))}</strong>
        <small>${escapeHtml(note)}</small>
      </article>
  `).join("");
}

function renderFactoryOverview() {
  const counts = appState.runtime?.counts || {};
  const checks = [
    Boolean(appState.state.meta),
    Boolean(appState.library?.generated_cast_manifest),
    (counts.generated_cast_files ?? 0) > 0,
    (counts.jobs ?? 0) > 0,
    (appState.state.gates || []).some(gate => gate.id === "human_approval"),
  ];
  const readiness = Math.round((checks.filter(Boolean).length / checks.length) * 100);
  document.getElementById("factoryOverviewPanel").innerHTML = `
    <div class="panel-heading">
      <div><span class="eyebrow">Factory Overview</span><h3>Local Readiness</h3></div>
      <span class="thin-pill success">Factory is live</span>
    </div>
    <div class="factory-overview">
      <div class="circular-gauge" style="--value:${readiness}">
        <div><strong>${readiness}%</strong><small>Local Ready</small></div>
      </div>
      <div class="overview-list">
        <div class="data-row"><span>Workflow Steps</span><strong>${counts.workflow_steps ?? 0}</strong></div>
        <div class="data-row"><span>Generating</span><strong>0</strong></div>
        <div class="data-row"><span>Queued Jobs</span><strong>${counts.active_jobs ?? 0}</strong></div>
        <div class="data-row"><span>Render Outputs</span><strong>${counts.render_outputs ?? 0}</strong></div>
      </div>
    </div>
  `;
}

function renderSystemMonitor() {
  const rows = [
    ["State JSON", appState.runtime?.files?.state?.exists ? 100 : 0],
    ["Asset Library", appState.runtime?.files?.asset_library?.exists ? 100 : 0],
    ["Codex Inbox", appState.runtime?.files?.codex_inbox?.exists ? 100 : 0],
    ["Cast Files", Math.min(100, ((appState.runtime?.counts?.generated_cast_files ?? 0) / 17) * 100)],
    ["Blender Lane", 0],
  ];
  document.getElementById("systemMonitorPanel").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">System Monitor</span><h3>Local Data Health</h3></div></div>
    <div class="monitor-list">
      ${rows.map(([label, base], index) => {
        const value = Math.round(Math.max(0, Math.min(100, base)));
        return `
          <div class="monitor-row">
            <span>${escapeHtml(label)}</span>
            <div class="meter"><i style="width:${value}%"></i></div>
            <strong>${value}%</strong>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function chartPoints(count, width, height, phase, amplitude = 24) {
  return Array.from({ length: count }, (_, index) => {
    const x = Math.round((index / (count - 1)) * width);
    const wave = Math.sin((index + phase) / 2.2) * amplitude;
    const drift = Math.cos((index + phase) / 4.6) * (amplitude * 0.45);
    const y = Math.round(height / 2 - wave - drift);
    return `${x},${Math.max(8, Math.min(height - 8, y))}`;
  }).join(" ");
}

function renderMarketFeed() {
  const phase = appState.tick / 2;
  const chart = chartPoints(28, 270, 82, phase, 18);
  document.getElementById("marketFeedPanel").innerHTML = `
    <div class="panel-heading">
      <div><span class="eyebrow">Market Feed</span><h3>AI Video Index</h3></div>
      <span class="thin-pill">mock</span>
    </div>
    <div class="market-value"><strong>${(8247.33 + Math.sin(appState.tick / 8) * 18).toFixed(2)}</strong><span>+3.27%</span></div>
    <svg class="mini-chart" viewBox="0 0 270 96" aria-label="Mock AI video index chart">
      <polyline points="${chart}" fill="none" stroke="#34d399" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      <polyline points="${chartPoints(28, 270, 82, phase + 5, 12)}" fill="none" stroke="#22d3ee" stroke-width="2" opacity="0.65"/>
    </svg>
    <div class="market-mini-row">
      <div>AIvD<strong>+3.27%</strong></div>
      <div>REND<strong>+2.91%</strong></div>
      <div>GEN<strong>+4.32%</strong></div>
      <div>META<strong>+2.14%</strong></div>
    </div>
  `;
}

function renderGlobalActivity() {
  const cityTimes = [
    ["New York", "America/New_York"],
    ["London", "Europe/London"],
    ["Tokyo", "Asia/Tokyo"],
    ["Singapore", "Asia/Singapore"],
  ];
  const formatter = zone => new Intl.DateTimeFormat("en-GB", {
    timeZone: zone,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date());

  document.getElementById("globalActivityPanel").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">Global Activity</span><h3>Render Watch</h3></div></div>
    <div class="world-map"></div>
    <div class="timezone-row">
      ${cityTimes.map(([city, zone]) => `<div>${escapeHtml(city)}<strong>${formatter(zone)}</strong></div>`).join("")}
    </div>
  `;
}

function renderFactoryVisual() {
  ["conveyorLaneA", "conveyorLaneB", "conveyorLaneC"].forEach((id, laneIndex) => {
    const lane = document.getElementById(id);
    if (!lane || lane.children.length) return;
    for (let i = 0; i < 7; i += 1) {
      const cube = document.createElement("span");
      cube.className = "video-cube";
      cube.dataset.label = `#${1287 - i}`;
      cube.style.animationDelay = `${-(i * 1.8 + laneIndex * 0.9)}s`;
      cube.style.left = `${i * 18}%`;
      lane.appendChild(cube);
    }
  });
}

function renderPipeline() {
  document.getElementById("productionPipeline").innerHTML = MOCK_GENERATION_DATA_UI_ONLY.pipeline.map(([label, status, state]) => `
    <article class="pipeline-node ${escapeHtml(state)}">
      <strong>${escapeHtml(label)}</strong>
      <span>${escapeHtml(status)}</span>
    </article>
  `).join("");
}

function castImages() {
  const cast = appState.castManifest?.cast || [];
  return cast.map(item => ({
    id: item.id,
    name: item.name,
    role: item.role,
    src: toProjectPath(item.asset_path),
  }));
}

function renderRecentOutputs() {
  const images = castImages();
  const jobs = appState.state.jobs || [];
  const planned = jobs.length ? jobs : [{ id: "clip_pending", title: "No planned clips", status: "pending", note: "Add jobs to generation-state.json" }];
  document.getElementById("recentOutputs").innerHTML = planned.map((job, index) => {
    const image = images[index % Math.max(1, images.length)];
    const imageHtml = image?.src
      ? `<img src="${escapeHtml(image.src)}" alt="${escapeHtml(image.name)}">`
      : "";
    const progress = statusProgress(job.status);
    return `
      <article class="output-card">
        <div class="output-thumb">${imageHtml}</div>
        <div class="output-body">
          <strong>${escapeHtml(job.title || job.id)}</strong>
          <span>${escapeHtml(job.id || `clip_${index + 1}`)} / ${escapeHtml(job.status || "pending")} / ${escapeHtml(job.review || "review pending")}</span>
          <div class="progress" style="--progress:${progress}%"><i></i></div>
        </div>
      </article>
    `;
  }).join("");
}

function renderGenerationQueue() {
  const jobs = appState.state.jobs || [];
  document.getElementById("generationQueuePanel").innerHTML = `
    <div class="panel-heading">
      <div><span class="eyebrow">Generation Queue</span><h3>Locked Queue</h3></div>
      <span class="thin-pill danger">approval required</span>
    </div>
    <div class="queue-list">
      ${jobs.map((job, index) => {
        const progress = statusProgress(job.status);
        return `
        <div class="queue-item">
          <strong class="queue-id">#${String(index + 1).padStart(2, "0")}</strong>
          <div>
            <strong>${escapeHtml(job.title || job.id)}</strong>
            <div class="progress" style="--progress:${progress}%"><i></i></div>
          </div>
          <span class="queue-status">${escapeHtml(job.status || "pending")}</span>
        </div>
      `;}).join("")}
    </div>
  `;
}

function renderActiveGenerations() {
  const images = castImages();
  const jobs = appState.state.jobs || [];
  const active = jobs.slice(0, 3);
  document.getElementById("activeGenerationsPanel").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">Planned Generations</span><h3>Studio Jobs</h3></div></div>
    <div class="active-list">
      ${active.map((job, index) => {
        const image = images[(index + 2) % Math.max(1, images.length)];
        const progress = statusProgress(job.status);
        return `
          <article class="active-card">
            <div class="active-thumb">${image?.src ? `<img src="${escapeHtml(image.src)}" alt="${escapeHtml(image.name)}">` : ""}</div>
            <div>
              <strong>${escapeHtml(job.title || job.id)}</strong>
              <span>${escapeHtml(job.id || "-")} / ${escapeHtml(job.status || "pending")} / Seedance visual-only / approval locked</span>
              <div class="progress" style="--progress:${progress}%"><i></i></div>
              <span>${escapeHtml(job.note || "No paid generation executed")}</span>
            </div>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

function renderSystemPerformance() {
  const phase = appState.tick / 1.7;
  const counts = appState.runtime?.counts || {};
  const status = counts.render_outputs ? "OUTPUTS" : "LOCKED";
  document.getElementById("systemPerformancePanel").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">System Performance</span><h3>Local Render State</h3></div></div>
    <div class="performance-grid">
      <svg class="performance-chart" viewBox="0 0 270 130" aria-label="Local activity chart">
        <polyline points="${chartPoints(32, 270, 118, phase, 26)}" fill="none" stroke="#22d3ee" stroke-width="2"/>
        <polyline points="${chartPoints(32, 270, 118, phase + 4, 18)}" fill="none" stroke="#34d399" stroke-width="2"/>
        <polyline points="${chartPoints(32, 270, 118, phase + 8, 22)}" fill="none" stroke="#f472ff" stroke-width="2"/>
        <polyline points="${chartPoints(32, 270, 118, phase + 12, 14)}" fill="none" stroke="#fbbf24" stroke-width="2"/>
      </svg>
      <div class="big-speed">
        <div><strong>${escapeHtml(status)}</strong><span>${counts.render_outputs ?? 0} files</span></div>
      </div>
    </div>
  `;
}

function renderTerminal() {
  const runtime = appState.runtime;
  const latestInbox = (runtime?.inbox || []).slice(-1)[0];
  const baseEvents = [
    "Line 04: Cost estimation active",
    "Generation queue locked until human approval",
    "Seedance visual-only lane standing by",
    "ElevenLabs voice lane prepared",
    "Subtitle post-edit gate armed",
    "Publish blocked: human review required",
    `Local files watched: ${runtime?.files?.recent?.length ?? 0}`,
    latestInbox ? `Inbox latest: ${(latestInbox.message || "").slice(0, 80)}` : "Inbox latest: empty",
  ];
  if (appState.tick % 3 === 0) {
    const event = baseEvents[appState.tick % baseEvents.length];
    appState.logTape.push(event);
    appState.logTape = appState.logTape.slice(-13);
  }
  const time = nowJstParts();
  document.getElementById("terminalTicker").innerHTML = `<span>${baseEvents.concat(baseEvents).map(item => `[${time}] ${escapeHtml(item)}`).join("  |  ")}</span>`;
  document.getElementById("terminalLog").innerHTML = appState.logTape.map((line, index) => {
    const hot = index === appState.logTape.length - 1 ? "log-hot" : "";
    return `<span class="${hot}">[${time}] ${escapeHtml(line)}</span>`;
  }).join("\n");

  const activity = appState.state.activity || [];
  document.getElementById("activity").innerHTML = activity.slice(-5).reverse().map(item => `
    <article class="activity-item">
      <strong>${escapeHtml(item.actor || "System")}</strong>
      <span>${escapeHtml(item.time || "")}</span>
      <span>${escapeHtml(item.event || "")}</span>
    </article>
  `).join("");
}

function renderLowerData() {
  const images = castImages().slice(0, 8);
  const captures = appState.library?.source_captures || [];
  const references = appState.library?.external_references || [];
  const blocked = appState.library?.blocked_assets || appState.library?.removed_assets || [];
  document.getElementById("library").innerHTML = `
    <div class="panel-heading">
      <div><span class="eyebrow">Production Library</span><h3>${(appState.castManifest?.cast || []).length || 0} cast / ${captures.length} captures</h3></div>
      <span class="thin-pill success">generated refs</span>
    </div>
    <div class="mini-grid">
      ${images.map(item => `
        <article class="asset-mini-card">
          <img src="${escapeHtml(item.src)}" alt="${escapeHtml(item.name)}">
          <strong>${escapeHtml(item.name)}</strong>
          <span>${escapeHtml(item.role)}</span>
        </article>
      `).join("")}
    </div>
    <div class="library-ledger">
      <div>
        <strong>Source Captures</strong>
        ${captures.slice(0, 5).map(item => `<span>${escapeHtml(item.name || item.id)} / ${escapeHtml(item.type || "capture")}</span>`).join("") || "<span>none</span>"}
      </div>
      <div>
        <strong>External References</strong>
        ${references.slice(0, 3).map(item => `<span>${escapeHtml(item.id)} / structure only</span>`).join("") || "<span>none</span>"}
      </div>
      <div>
        <strong>Blocked Records</strong>
        <span>${blocked.length} records / not active assets</span>
      </div>
    </div>
  `;

  const jobs = appState.state.jobs || [];
  document.getElementById("jobs").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">Seedance Jobs</span><h3>${jobs.length} clips</h3></div></div>
    <div class="overview-list">
      ${jobs.map(job => `
        <article class="job-mini-card ${cls(job.status)}">
          <strong>${escapeHtml(job.title)}</strong>
          <span>${escapeHtml(job.status)} / ${escapeHtml(job.primary_reference || "-")}</span>
          <span>${escapeHtml(job.note || "")}</span>
        </article>
      `).join("")}
    </div>
  `;

  const gates = appState.state.gates || [];
  document.getElementById("gates").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">Safety Gates</span><h3>approval locks</h3></div></div>
    <div class="overview-list">
      ${gates.map(gate => `
        <article class="gate-mini-card ${cls(gate.status)}">
          <strong>${escapeHtml(gate.label)}</strong>
          <span>${escapeHtml(gate.status)} / ${escapeHtml(gate.id)}</span>
        </article>
      `).join("")}
    </div>
  `;
}

function renderAll() {
  renderTop();
  renderMetrics();
  renderFactoryOverview();
  renderSystemMonitor();
  renderMarketFeed();
  renderGlobalActivity();
  renderFactoryVisual();
  renderPipeline();
  renderRecentOutputs();
  renderGenerationQueue();
  renderActiveGenerations();
  renderSystemPerformance();
  renderTerminal();
  renderLowerData();
  document.getElementById("nextInstruction").value = appState.state.meta?.next_terminal_instruction || "";
}

async function sendInstruction() {
  if (appState.sendInFlight) return;
  const status = document.getElementById("sendStatus");
  const button = document.getElementById("sendInstruction");
  const message = document.getElementById("nextInstruction").value.trim();
  if (!message) {
    status.textContent = "送信する指示がありません。";
    return;
  }
  appState.sendInFlight = true;
  button.disabled = true;
  status.textContent = "Codex inboxへ送信中...";
  try {
    const response = await fetch("/api/send-to-codex", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: "live-workflow-ui", message }),
    });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.message || `HTTP ${response.status}`);
    status.textContent = `送信済み: ${result.queued_at}`;
    await loadFactoryData();
  } catch (error) {
    status.textContent = `送信失敗: ${error.message}`;
  } finally {
    appState.sendInFlight = false;
    button.disabled = false;
  }
}

document.getElementById("copyInstruction").addEventListener("click", async () => {
  await navigator.clipboard.writeText(document.getElementById("nextInstruction").value);
});

document.getElementById("sendInstruction").addEventListener("click", sendInstruction);

loadFactoryData();
setInterval(loadFactoryData, 3500);
setInterval(() => {
  appState.tick += 1;
  renderAll();
}, 1100);
