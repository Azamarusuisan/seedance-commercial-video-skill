const FACTORY_API = "/api/factory-data";
const STATE_PATH = "state/generation-state.json";
const LIBRARY_PATH = "state/asset-library.json";

// UI演出専用のmock telemetry。本物の市場データ、広告配信、生成結果ではない。
// 本番KPI、ジョブ、キュー、成果物は state/API の実データを使う。
const MOCK_GENERATION_DATA_UI_ONLY = {
  pipeline: [
    ["取込", "完了", "complete"],
    ["解析", "完了", "complete"],
    ["Blender", "実画面投影", "active"],
    ["生成", "待機中", "active"],
    ["レンダー", "76%", "active"],
    ["後編集", "待機中", "pending"],
    ["納品", "ロック中", "locked"],
  ],
};

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
  waiting: "待機中",
  waiting_for_render: "レンダー待ち",
  ready: "準備完了",
};

function statusJa(value) {
  return STATUS_JA[String(value || "").toLowerCase()] || String(value || "待機中");
}

function displayText(value) {
  return String(value ?? "")
    .replace(/^Clip\s+(\d+)/, "クリップ$1")
    .replaceAll("review pending", "レビュー待ち")
    .replaceAll("approval locked", "承認待ち")
    .replaceAll("No paid generation executed", "有料生成は未実行")
    .replaceAll("Seedance visual-only", "Seedance映像のみ")
    .replaceAll("not estimated", "未見積")
    .replaceAll("structure only", "構造だけ参照")
    .replaceAll("waiting for local render", "ローカルレンダー待ち")
    .replaceAll("main lead", "主役")
    .replaceAll("co-lead", "相手役")
    .replaceAll("local guide", "現地ガイド");
}

const appState = {
  tick: 0,
  runtime: null,
  state: {},
  library: {},
  castManifest: {},
  logTape: [
    "ライン04: ローカル工場サーバー起動",
    "Seedanceキューは人間承認までロック",
    "ElevenLabs音声レーン準備完了",
    "字幕後編集ゲート待機中",
    "公開停止: 人間レビュー必須",
    "有料生成は未実行",
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
    loadStatus.textContent = `${runtime?.local_server?.local_only ? "ローカルサーバー" : "静的表示"}: ${new Date().toLocaleTimeString()}`;
    document.getElementById("connectionStatus").textContent = runtime?.local_server?.local_only ? "ローカル限定" : "静的フォールバック";
    renderAll();
  } catch (error) {
    loadStatus.textContent = `状態読み込み失敗: ${error.message}`;
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
  if (value === null || value === undefined || value === "") return "待機中";
  if (typeof value === "number") return value.toLocaleString("ja-JP");
  return displayText(String(value));
}

function renderTop() {
  const state = appState.state;
  document.getElementById("systemTime").textContent = nowJstParts();
  document.getElementById("queueStatus").textContent = "ロック中";

  const statusStrip = document.getElementById("statusStrip");
  const sourceRefs = state.assets?.source_ref_count ?? 0;
  const currentWork = state.current_work?.title || "費用見積が進行中";
  statusStrip.innerHTML = [
    ["現在作業", currentWork, "magenta"],
    ["人間承認", "必須", "warning"],
    ["公開", "停止中", "danger"],
    ["外部素材参照", String(sourceRefs), ""],
    ["ライン", "稼働中", "success"],
    ["音声", "ElevenLabs", ""],
    ["字幕", "後編集", ""],
    ["有料生成", "未実行", "danger"],
  ].map(([label, value, tone]) => (
    `<span class="thin-pill ${tone}">${escapeHtml(label)} ${escapeHtml(displayText(value))}</span>`
  )).join("");
}

function renderMetrics() {
  const counts = appState.runtime?.counts || {};
  const jobs = appState.state.jobs || [];
  const credits = estimatedCredits(jobs);
  const blocked = counts.blocked_gates ?? (appState.state.gates || []).filter(gate => gate.status === "blocked").length;
  const metrics = [
    ["現在工程", appState.state.current_work?.title || appState.state.meta?.active_stage || "待機中", "generation-state.json"],
    ["予定ジョブ", counts.jobs ?? jobs.length, "state.jobs.length"],
    ["見積クレジット", credits === null ? "未見積" : credits.toFixed(1), "jobs[].cost_credits"],
    ["MCP要求", counts.higgsfield_mcp_requests ?? 0, "workspace/mcp-requests"],
    ["Blender画面", counts.blender_screen_captures ?? counts.blender_live_frames ?? counts.blender_renders ?? 0, "workspace/assets/3d/live"],
    ["演者素材", counts.generated_cast_files ?? appState.state.assets?.generated_cast_count ?? 0, "cast manifest"],
    ["承認ゲート", `${blocked}件停止中`, "人間承認必須"],
  ];
  const row = document.getElementById("metricRow");
  row.innerHTML = metrics.map(([label, value, note]) => `
      <article class="metric-card">
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(renderValue(value))}</strong>
        <small>${escapeHtml(displayText(note))}</small>
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
      <div><span class="eyebrow">工場概要</span><h3>ローカル準備率</h3></div>
      <span class="thin-pill success">工場稼働中</span>
    </div>
    <div class="factory-overview">
      <div class="circular-gauge" style="--value:${readiness}">
        <div><strong>${readiness}%</strong><small>準備完了</small></div>
      </div>
      <div class="overview-list">
        <div class="data-row"><span>工程数</span><strong>${counts.workflow_steps ?? 0}</strong></div>
        <div class="data-row"><span>生成中</span><strong>0</strong></div>
        <div class="data-row"><span>待機ジョブ</span><strong>${counts.active_jobs ?? 0}</strong></div>
        <div class="data-row"><span>出力数</span><strong>${counts.render_outputs ?? 0}</strong></div>
      </div>
    </div>
  `;
}

function renderSystemMonitor() {
  const blenderReady = appState.runtime?.blender?.available ? 100 : 0;
  const rows = [
    ["状態JSON", appState.runtime?.files?.state?.exists ? 100 : 0],
    ["素材ライブラリ", appState.runtime?.files?.asset_library?.exists ? 100 : 0],
    ["Codex受信箱", appState.runtime?.files?.codex_inbox?.exists ? 100 : 0],
    ["演者ファイル", Math.min(100, ((appState.runtime?.counts?.generated_cast_files ?? 0) / 17) * 100)],
    ["Blenderレーン", blenderReady],
  ];
  document.getElementById("systemMonitorPanel").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">システム監視</span><h3>ローカルデータ状態</h3></div></div>
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
      <div><span class="eyebrow">需要メーター</span><h3>AI動画指数</h3></div>
      <span class="thin-pill">演出用</span>
    </div>
    <div class="market-value"><strong>${(8247.33 + Math.sin(appState.tick / 8) * 18).toFixed(2)}</strong><span>+3.27%</span></div>
    <svg class="mini-chart" viewBox="0 0 270 96" aria-label="演出用AI動画指数チャート">
      <polyline points="${chart}" fill="none" stroke="#34d399" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      <polyline points="${chartPoints(28, 270, 82, phase + 5, 12)}" fill="none" stroke="#22d3ee" stroke-width="2" opacity="0.65"/>
    </svg>
    <div class="market-mini-row">
      <div>動画指数<strong>+3.27%</strong></div>
      <div>描画<strong>+2.91%</strong></div>
      <div>生成<strong>+4.32%</strong></div>
      <div>素材<strong>+2.14%</strong></div>
    </div>
  `;
}

function renderGlobalActivity() {
  const cityTimes = [
    ["ニューヨーク", "America/New_York"],
    ["ロンドン", "Europe/London"],
    ["東京", "Asia/Tokyo"],
    ["シンガポール", "Asia/Singapore"],
  ];
  const formatter = zone => new Intl.DateTimeFormat("en-GB", {
    timeZone: zone,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date());

  document.getElementById("globalActivityPanel").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">拠点表示</span><h3>レンダー監視</h3></div></div>
    <div class="world-map"></div>
    <div class="timezone-row">
      ${cityTimes.map(([city, zone]) => `<div>${escapeHtml(city)}<strong>${formatter(zone)}</strong></div>`).join("")}
    </div>
  `;
}

function renderFactoryVisual() {
  const factoryVisual = document.getElementById("factoryVisual");
  const projection = document.getElementById("blenderProjection");
  const screenState = appState.runtime?.blender_assets?.screen_state || {};
  const screenCapture = appState.runtime?.blender_assets?.screen_capture;
  const latestLive = appState.runtime?.blender_assets?.latest_live_frame;
  const latestRender = appState.runtime?.blender_assets?.latest_render;
  const liveState = appState.runtime?.blender_assets?.live_state || {};
  const projectedFrame = screenCapture?.exists ? screenCapture : (latestLive || latestRender);
  const isAppScreen = Boolean(screenCapture?.exists);
  const blenderStatus = screenState.status || liveState.status || appState.runtime?.blender_assets?.status || "waiting";
  const frame = liveState.frame || (latestLive ? 1 : 0);
  const frameCount = liveState.frame_count || (latestLive ? appState.runtime?.counts?.blender_live_frames : 0) || 0;
  const progress = isAppScreen ? 100 : Math.max(0, Math.min(100, Number(liveState.progress || 0)));
  const cacheKey = projectedFrame?.mtime_ns || projectedFrame?.mtime || Date.now();
  if (factoryVisual) {
    factoryVisual.classList.toggle("has-app-screen", Boolean(isAppScreen && projectedFrame?.path));
  }
  if (projection) {
    if (projectedFrame?.path) {
      projection.innerHTML = isAppScreen ? `
        <img class="raw-blender-screen" src="${escapeHtml(toProjectPath(projectedFrame.path))}?t=${encodeURIComponent(cacheKey)}" alt="Blender実画面キャプチャ">
      ` : `
          <div class="blender-window-bar">
            <span>Blender 5.1.2</span>
            <strong>ビューポート</strong>
            <em>${escapeHtml(statusJa(blenderStatus))}</em>
          </div>
          <img src="${escapeHtml(toProjectPath(projectedFrame.path))}?t=${encodeURIComponent(cacheKey)}" alt="Blenderライブプレート">
          <div class="blender-window-sidebar">
            <span>シーン</span>
            <b>工場ライン</b>
            <b>動画キューブ</b>
            <b>カメラ</b>
          </div>
          <div class="projection-overlay">
          <span>BLENDERライブプレート</span>
          <strong>${escapeHtml(statusJa(blenderStatus))} / ${escapeHtml(frame)}-${escapeHtml(frameCount)}</strong>
          <small>${escapeHtml(projectedFrame.path)}</small>
          </div>
          <div class="blender-timeline">
            <span>フレーム ${escapeHtml(frame)}</span>
            <i style="width:${progress}%"></i>
          </div>
      `;
      projection.classList.add("is-ready");
      projection.classList.toggle("is-app-screen", isAppScreen);
    } else {
      projection.innerHTML = `
        <div class="mirror-placeholder">
          <div class="mirror-rings"><i></i><i></i><i></i></div>
          <div class="mirror-scan"></div>
          <span>BLENDERミラー待機中</span>
          <strong>ローカル工場アニメーション</strong>
          <small>Blender起動後に capture-blender-screen.sh で実画面へ切替</small>
        </div>
      `;
      projection.classList.remove("is-ready");
      projection.classList.remove("is-app-screen");
      if (factoryVisual) factoryVisual.classList.remove("has-app-screen");
    }
  }

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
  const planned = jobs.length ? jobs : [{ id: "clip_pending", title: "予定クリップなし", status: "pending", note: "generation-state.json にジョブを追加" }];
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
          <strong>${escapeHtml(displayText(job.title || job.id))}</strong>
          <span>${escapeHtml(job.id || `clip_${index + 1}`)} / ${escapeHtml(statusJa(job.status))} / ${escapeHtml(displayText(job.review || "review pending"))}</span>
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
      <div><span class="eyebrow">生成キュー</span><h3>承認待ちキュー</h3></div>
      <span class="thin-pill danger">承認必須</span>
    </div>
    <div class="queue-list">
      ${jobs.map((job, index) => {
        const progress = statusProgress(job.status);
        return `
        <div class="queue-item">
          <strong class="queue-id">#${String(index + 1).padStart(2, "0")}</strong>
          <div>
            <strong>${escapeHtml(displayText(job.title || job.id))}</strong>
            <div class="progress" style="--progress:${progress}%"><i></i></div>
          </div>
          <span class="queue-status">${escapeHtml(statusJa(job.status))}</span>
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
    <div class="panel-heading"><div><span class="eyebrow">生成予定</span><h3>スタジオジョブ</h3></div></div>
    <div class="active-list">
      ${active.map((job, index) => {
        const image = images[(index + 2) % Math.max(1, images.length)];
        const progress = statusProgress(job.status);
        return `
          <article class="active-card">
            <div class="active-thumb">${image?.src ? `<img src="${escapeHtml(image.src)}" alt="${escapeHtml(image.name)}">` : ""}</div>
            <div>
              <strong>${escapeHtml(displayText(job.title || job.id))}</strong>
              <span>${escapeHtml(job.id || "-")} / ${escapeHtml(statusJa(job.status))} / Seedance映像のみ / 承認待ち</span>
              <div class="progress" style="--progress:${progress}%"><i></i></div>
              <span>${escapeHtml(displayText(job.note || "No paid generation executed"))}</span>
            </div>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

function renderMcpBridge() {
  const mcp = appState.runtime?.higgsfield_mcp || {};
  const requests = mcp.requests || [];
  const logs = mcp.logs || [];
  const latestLog = logs.slice().sort((a, b) => String(b.checked_at || "").localeCompare(String(a.checked_at || "")))[0];
  const visible = mcp.direct_tool_visible ? "直接ツール検出" : "handoff方式";
  document.getElementById("mcpBridgePanel").innerHTML = `
    <div class="panel-heading">
      <div><span class="eyebrow">Higgsfield MCP連結</span><h3>${escapeHtml(visible)}</h3></div>
      <span class="thin-pill warning">生成は未実行</span>
    </div>
    <div class="overview-list">
      <div class="data-row"><span>リクエストJSON</span><strong>${requests.length}</strong></div>
      <div class="data-row"><span>実行ログ</span><strong>${logs.length}</strong></div>
      <div class="data-row"><span>MCP待ち</span><strong>${mcp.pending ?? 0}</strong></div>
      <div class="data-row"><span>停止中</span><strong>${mcp.blocked ?? 0}</strong></div>
    </div>
    <div class="data-list compact-list">
      ${requests.slice(-3).reverse().map(item => `<article><strong>${escapeHtml(displayText(item.request_type || "MCP要求"))}</strong><span>${escapeHtml(item._file?.path || "")}</span></article>`).join("") || "<article><strong>MCP要求なし</strong><span>workspace/scripts/higgsfield-status.sh を実行</span></article>"}
      ${latestLog ? `<article><strong>最新ログ: ${escapeHtml(statusJa(latestLog.status))}</strong><span>${escapeHtml(displayText(latestLog.command || latestLog.reason || ""))}</span></article>` : ""}
    </div>
  `;
}

function renderSystemPerformance() {
  const phase = appState.tick / 1.7;
  const counts = appState.runtime?.counts || {};
  const status = counts.blender_screen_captures ? "実画面投影中" : (counts.blender_live_frames ? "ライブ表示" : (counts.blender_renders ? "3D準備完了" : "ロック中"));
  document.getElementById("systemPerformancePanel").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">処理状態</span><h3>ローカルレンダー状態</h3></div></div>
    <div class="performance-grid">
      <svg class="performance-chart" viewBox="0 0 270 130" aria-label="ローカル活動チャート">
        <polyline points="${chartPoints(32, 270, 118, phase, 26)}" fill="none" stroke="#22d3ee" stroke-width="2"/>
        <polyline points="${chartPoints(32, 270, 118, phase + 4, 18)}" fill="none" stroke="#34d399" stroke-width="2"/>
        <polyline points="${chartPoints(32, 270, 118, phase + 8, 22)}" fill="none" stroke="#f472ff" stroke-width="2"/>
        <polyline points="${chartPoints(32, 270, 118, phase + 12, 14)}" fill="none" stroke="#fbbf24" stroke-width="2"/>
      </svg>
      <div class="big-speed">
        <div><strong>${escapeHtml(status)}</strong><span>${counts.blender_screen_captures ?? 0} 実画面 / ${counts.blender_live_frames ?? 0} フレーム</span></div>
      </div>
    </div>
  `;
}

function renderTerminal() {
  const runtime = appState.runtime;
  const latestInbox = (runtime?.inbox || []).slice(-1)[0];
  const baseEvents = [
    "ライン04: 費用見積が進行中",
    "生成キュー: 人間承認までロック",
    "Seedance映像レーン: 待機中",
    "ElevenLabs音声レーン: 準備完了",
    "字幕後編集ゲート: 待機中",
    "公開停止: 人間レビュー必須",
    `監視ファイル: ${runtime?.files?.recent?.length ?? 0}件`,
    latestInbox ? `受信箱最新: ${(latestInbox.message || "").slice(0, 80)}` : "受信箱最新: 空",
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
      <strong>${escapeHtml(item.actor || "システム")}</strong>
      <span>${escapeHtml(item.time || "")}</span>
      <span>${escapeHtml(displayText(item.event || ""))}</span>
    </article>
  `).join("");
}

function renderLowerData() {
  const images = castImages().slice(0, 8);
  const captures = appState.library?.source_captures || [];
  const blenderRenders = appState.runtime?.blender_assets?.renders || [];
  const liveFrames = appState.runtime?.blender_assets?.live_frames || [];
  const screenCapture = appState.runtime?.blender_assets?.screen_capture;
  const references = appState.library?.external_references || [];
  const blocked = appState.library?.blocked_assets || appState.library?.removed_assets || [];
  document.getElementById("library").innerHTML = `
    <div class="panel-heading">
      <div><span class="eyebrow">制作ライブラリ</span><h3>${(appState.castManifest?.cast || []).length || 0} 演者 / ${captures.length} キャプチャ</h3></div>
      <span class="thin-pill success">生成素材</span>
    </div>
    <div class="mini-grid">
      ${images.map(item => `
        <article class="asset-mini-card">
          <img src="${escapeHtml(item.src)}" alt="${escapeHtml(item.name)}">
          <strong>${escapeHtml(item.name)}</strong>
          <span>${escapeHtml(displayText(item.role))}</span>
        </article>
      `).join("")}
    </div>
    <div class="library-ledger">
      <div>
        <strong>Blender実画面 / ライブフレーム</strong>
        ${screenCapture?.exists ? `<span>${escapeHtml(screenCapture.path)} / ${escapeHtml(screenCapture.mtime || "")}</span>` : ""}
        ${liveFrames.slice(0, 4).map(item => `<span>${escapeHtml(item.path)} / ${escapeHtml(item.mtime || "")}</span>`).join("") || blenderRenders.slice(0, 3).map(item => `<span>${escapeHtml(item.path)} / ${escapeHtml(item.mtime || "")}</span>`).join("") || "<span>ローカルレンダー待ち</span>"}
      </div>
      <div>
        <strong>ソースキャプチャ</strong>
        ${captures.slice(0, 5).map(item => `<span>${escapeHtml(item.name || item.id)} / ${escapeHtml(item.type || "capture")}</span>`).join("") || "<span>なし</span>"}
      </div>
      <div>
        <strong>外部参考</strong>
        ${references.slice(0, 3).map(item => `<span>${escapeHtml(item.id)} / 構造だけ参照</span>`).join("") || "<span>なし</span>"}
      </div>
      <div>
        <strong>ブロック記録</strong>
        <span>${blocked.length}件 / 使用素材ではない</span>
      </div>
    </div>
  `;

  const jobs = appState.state.jobs || [];
  document.getElementById("jobs").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">Seedanceジョブ</span><h3>${jobs.length}本のクリップ</h3></div></div>
    <div class="overview-list">
      ${jobs.map(job => `
        <article class="job-mini-card ${cls(job.status)}">
          <strong>${escapeHtml(displayText(job.title))}</strong>
          <span>${escapeHtml(statusJa(job.status))} / ${escapeHtml(job.primary_reference || "-")}</span>
          <span>${escapeHtml(displayText(job.note || ""))}</span>
        </article>
      `).join("")}
    </div>
  `;

  const gates = appState.state.gates || [];
  document.getElementById("gates").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">安全ゲート</span><h3>承認ロック</h3></div></div>
    <div class="overview-list">
      ${gates.map(gate => `
        <article class="gate-mini-card ${cls(gate.status)}">
          <strong>${escapeHtml(gate.label)}</strong>
          <span>${escapeHtml(statusJa(gate.status))} / ${escapeHtml(gate.id)}</span>
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
  renderMcpBridge();
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
    const forward = result.terminal_forward || {};
    if (forward.ok) {
      status.textContent = `送信済み / Terminal転送OK: ${result.queued_at}`;
    } else if (forward.enabled) {
      status.textContent = `受信箱保存済み / Terminal転送失敗: ${forward.message || result.queued_at}`;
    } else {
      status.textContent = `受信箱保存済み / Terminal転送OFF: ${result.queued_at}`;
    }
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
setInterval(loadFactoryData, 1000);
setInterval(() => {
  appState.tick += 1;
  renderAll();
}, 1100);
