const FACTORY_API = "/api/factory-data";
const STATE_PATH = "state/generation-state.json";
const LIBRARY_PATH = "state/asset-library.json";

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
  planned: "計画済み",
  queued: "キュー",
  preparing: "準備中",
  storyboard_review: "絵コンテ確認",
  generated_draft_review: "生成ドラフト確認",
  required_before_any_generation: "生成前許可必須",
  not_granted_for_next_generation: "未許可",
  needs_user_approval_before_generation: "承認待ち",
  completed_review_needed: "完了・要レビュー",
  review_needed: "要レビュー",
  needs_decision: "要判断",
  missing_if_needed: "必要なら未作成",
  draft_ready: "下書きあり",
  connected: "接続済み",
  unavailable: "未接続",
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
  if (/^https?:/.test(path) || path.startsWith("/")) return path;
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

function scriptBeats() {
  return appState.state.script?.beats || [];
}

function clipNumberFrom(value) {
  const text = String(value || "");
  const match = text.match(/clip[_\s-]?0?(\d+)/i);
  return match ? Number.parseInt(match[1], 10) : null;
}

function clipLabelFromJob(job) {
  const number = clipNumberFrom(job?.id) || clipNumberFrom(job?.title);
  return number ? `Clip ${number}` : "";
}

function beatsForJob(job) {
  const label = clipLabelFromJob(job);
  return scriptBeats().filter(beat => String(beat.clip || "").toLowerCase() === label.toLowerCase());
}

function storyboardPanelForJob(job) {
  return (appState.state.storyboard?.panels || []).find(panel => panel.id === job?.id) || {};
}

function jobReviewImage(job) {
  const panel = storyboardPanelForJob(job);
  return panel.generated_image || panel.image || job?.storyboard_image || job?.reference_image || appState.state.blender?.render_path || "";
}

function jobMediaHtml(job, className = "") {
  if (job?.local_path) {
    const src = toProjectPath(job.local_path);
    return `
      <div class="video-review-shell">
        <video class="${escapeHtml(className)}" src="${escapeHtml(src)}" controls muted playsinline preload="metadata"></video>
        ${videoActionsHtml(src, job.title || job.id || "video")}
      </div>
    `;
  }
  const image = jobReviewImage(job);
  return image ? `<img class="${escapeHtml(className)}" src="${escapeHtml(toProjectPath(image))}" alt="${escapeHtml(job.title || job.id)}">` : "";
}

function queueMediaHtml(job) {
  if (job?.local_path) {
    const src = toProjectPath(job.local_path);
    return `<video src="${escapeHtml(src)}" muted playsinline preload="metadata"></video>`;
  }
  const image = jobReviewImage(job);
  return image ? `<img src="${escapeHtml(toProjectPath(image))}" alt="${escapeHtml(job.title || job.id)}">` : "";
}

function videoActionsHtml(src, label) {
  const cleanSrc = escapeHtml(src);
  const filename = String(label || "seedance-video").replace(/[^a-zA-Z0-9_-]+/g, "_").toLowerCase() + ".mp4";
  return `
    <div class="video-actions">
      <button type="button" data-video-action="fullscreen">全画面</button>
      <a href="${cleanSrc}" download="${escapeHtml(filename)}">ダウンロード</a>
      <a href="${cleanSrc}" target="_blank" rel="noopener">別タブ</a>
    </div>
  `;
}

function workflowDetail(phase) {
  const jobs = appState.state.jobs || [];
  const beats = scriptBeats();
  const key = phase.id || "";
  if (key === "script") return `${beats.length}ビート / ナレ${beats.filter(beat => beat.narration).length}行 / テロップ${beats.filter(beat => beat.telop).length}本`;
  if (key === "cost") return `見積 ${estimatedCredits(jobs)?.toFixed(0) || "未見積"} credits / ${jobs.length}本`;
  if (key === "seedance") return `${jobs.filter(job => job.status === "estimated").length}/${jobs.length}本 見積済み / 生成待機`;
  if (key === "voice") return `${appState.state.script?.voice_script?.length || beats.length}行 / ElevenLabs待機`;
  if (key === "subtitles") return `${appState.state.script?.telop_plan?.length || beats.length}本 / 後編集`;
  if (key === "palmier") return appState.state.palmier?.timeline_status || "Palmier Pro編集レーン待機";
  if (key === "conversation") return `${(appState.state.generation_conversation || []).length}件 / 生成判断ログ`;
  if (key === "review") return `${appState.state.gates?.filter(gate => gate.status === "pending").length || 0}ゲート確認待ち`;
  return phase.output || phase.note || "";
}

function pipelineClass(status) {
  const key = String(status || "").toLowerCase();
  if (["done", "completed", "approved"].includes(key)) return "complete";
  if (["active", "generating", "rendering", "processing", "estimated", "planned", "connected"].includes(key)) return "active";
  if (["blocked", "locked"].includes(key)) return "locked";
  return "pending";
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
  const phase = String(appState.state.current_work?.title || appState.state.meta?.active_stage || "待機中")
    .replace("Workflow locked: ", "")
    .replace("Blenderプリビズ肉付けレビュー", "肉付けレビュー");
  const metrics = [
    ["現在工程", phase, "generation-state.json"],
    ["予定ジョブ", counts.jobs ?? jobs.length, "state.jobs.length"],
    ["見積クレジット", credits === null ? "未見積" : credits.toFixed(1), "jobs[].cost_credits"],
    ["MCP要求", counts.higgsfield_mcp_requests ?? 0, "workspace/mcp-requests"],
    ["Blender画面", counts.blender_screen_captures ?? counts.blender_live_frames ?? counts.blender_renders ?? 0, "workspace/assets/3d/live"],
    ["演者素材", counts.generated_cast_files ?? appState.state.assets?.generated_cast_count ?? 0, "cast manifest"],
    ["承認ゲート", `${blocked}停止`, "人間承認必須"],
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

function requirementClass(status) {
  const key = String(status || "").toLowerCase();
  if (["done", "approved", "ready"].includes(key)) return "ok";
  if (["draft_ready", "pending", "needs_decision", "missing_if_needed"].includes(key)) return "warn";
  if (["blocked", "failed"].includes(key)) return "stop";
  return "warn";
}

function renderRequirements() {
  const target = document.getElementById("requirementsPanel");
  if (!target) return;
  const items = appState.state.pre_generation_checklist || [];
  const stopCount = items.filter(item => requirementClass(item.status) === "stop").length;
  const warnCount = items.filter(item => requirementClass(item.status) === "warn").length;
  target.innerHTML = `
    <div class="panel-heading">
      <div>
        <span class="eyebrow">生成前ゲート</span>
        <h3>抜け漏れチェック</h3>
      </div>
      <span class="thin-pill danger">${escapeHtml(stopCount)}停止 / ${escapeHtml(warnCount)}要確認</span>
    </div>
    <div class="requirements-grid">
      ${items.map(item => `
        <article class="requirement-card ${escapeHtml(requirementClass(item.status))}">
          <div>
            <strong>${escapeHtml(item.label)}</strong>
            <span>${escapeHtml(statusJa(item.status))} / ${escapeHtml(item.required_before || "")}</span>
          </div>
          <p>${escapeHtml(item.current || "")}</p>
          <em>${escapeHtml(item.done_when || "")}</em>
        </article>
      `).join("")}
    </div>
  `;
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
  const preferRenderPlate = appState.state.blender?.projection_mode === "render_plate";
  const projectedFrame = preferRenderPlate ? (latestRender || latestLive || screenCapture) : (screenCapture?.exists ? screenCapture : (latestLive || latestRender));
  const isAppScreen = Boolean(screenCapture?.exists && !preferRenderPlate);
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
            <span>${escapeHtml(appState.runtime?.blender?.version || "Blender")}</span>
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
  const workflow = appState.state.workflow || [];
  const fallback = [
    { id: "assets", label: "素材", status: "pending", output: "状態読み込み待ち" },
    { id: "script", label: "台本", status: "pending", output: "script.beats[]待ち" },
    { id: "seedance", label: "映像生成", status: "pending", output: "jobs[]待ち" },
  ];
  document.getElementById("productionPipeline").innerHTML = (workflow.length ? workflow : fallback).map(phase => `
    <article class="pipeline-node ${escapeHtml(pipelineClass(phase.status))} ${escapeHtml(cls(phase.id || phase.status))}">
      <strong>${escapeHtml(phase.label || phase.id || "工程")}</strong>
      <span>${escapeHtml(statusJa(phase.status))}</span>
      <small>${escapeHtml(displayText(workflowDetail(phase)))}</small>
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
  const jobs = appState.state.jobs || [];
  const planned = jobs.length ? jobs : [{ id: "clip_pending", title: "予定クリップなし", status: "pending", note: "generation-state.json にジョブを追加" }];
  document.getElementById("recentOutputs").innerHTML = planned.map((job, index) => {
    const progress = statusProgress(job.status);
    return `
      <article class="output-card">
        <div class="output-thumb">${queueMediaHtml(job)}</div>
        <div class="output-body">
          <strong>${escapeHtml(displayText(job.title || job.id))}</strong>
          <span>${escapeHtml(job.id || `clip_${index + 1}`)} / ${escapeHtml(statusJa(job.status))} / ${job.local_path ? "MP4保存済み" : `${beatsForJob(job).length}ビート連動`}</span>
          <div class="progress" style="--progress:${progress}%"><i></i></div>
          ${job.local_path ? `<small>${escapeHtml(job.local_path)}</small>` : ""}
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
        const beatCount = beatsForJob(job).length;
        return `
        <div class="queue-item">
          <strong class="queue-id">#${String(index + 1).padStart(2, "0")}</strong>
          <div>
            <strong>${escapeHtml(displayText(job.title || job.id))}</strong>
            <span>${escapeHtml(beatCount)}ビート / ${escapeHtml(job.cost_credits || "未見積")} credits / 台本連動</span>
            <div class="progress" style="--progress:${progress}%"><i></i></div>
          </div>
          <span class="queue-status">${escapeHtml(statusJa(job.status))}</span>
        </div>
      `;}).join("")}
    </div>
  `;
}

function renderActiveGenerations() {
  const jobs = appState.state.jobs || [];
  const active = jobs.slice(0, 4);
  document.getElementById("activeGenerationsPanel").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">生成予定</span><h3>参照画像つきジョブ</h3></div></div>
    <div class="active-list">
      ${active.map((job, index) => {
        const progress = statusProgress(job.status);
        const linkedBeats = beatsForJob(job);
        return `
          <article class="active-card">
            <div class="active-thumb">${jobMediaHtml(job)}</div>
            <div>
              <strong>${escapeHtml(displayText(job.title || job.id))}</strong>
              <span>${escapeHtml(job.id || "-")} / ${escapeHtml(statusJa(job.status))} / ${job.local_path ? "MP4保存済み・音声なし" : `${linkedBeats.length}ビート / Seedance映像のみ`}</span>
              <div class="progress" style="--progress:${progress}%"><i></i></div>
              <span>${escapeHtml(job.local_path || linkedBeats.map(beat => beat.telop).filter(Boolean).join(" -> ") || displayText(job.note || "No paid generation executed"))}</span>
            </div>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

function renderStoryboardReview() {
  const storyboard = appState.state.storyboard || {};
  const approval = appState.state.approval_contract || {};
  const jobs = appState.state.jobs || [];
  const screenCapture = appState.runtime?.blender_assets?.screen_capture;
  const generatedSheet = storyboard.generated_contact_sheet || storyboard.contact_sheet;
  const referenceSheet = storyboard.reference_contact_sheet;
  const panels = storyboard.panels || [];
  const target = document.getElementById("storyboardReview");
  if (!target) return;
  target.innerHTML = `
    <div class="panel-heading">
      <div>
        <span class="eyebrow">生成前レビュー</span>
        <h3>生成絵コンテ / 許可ゲート</h3>
      </div>
      <span class="thin-pill danger">追加生成は許可待ち</span>
    </div>

    <div class="approval-gate-strip">
      <div>
        <span>現在地</span>
        <strong>${escapeHtml(appState.state.current_work?.title || "生成前レビュー")}</strong>
      </div>
      <div class="blocked">
        <span>次の生成許可</span>
        <strong>${escapeHtml(statusJa(approval.current_permission || "blocked"))}</strong>
      </div>
      <div>
        <span>Seedance本番</span>
        <strong>未実行</strong>
      </div>
      <div>
        <span>絵コンテ状態</span>
        <strong>${escapeHtml(statusJa(storyboard.status || "pending"))}</strong>
      </div>
    </div>

    <div class="storyboard-cinema-grid">
      <article class="generated-storyboard-hero">
        <div class="storyboard-frame-label">
          <span>AI GENERATED STORYBOARD DRAFT</span>
          <strong>ASCENSION LINE</strong>
          <em>この生成絵コンテを承認してから次の生成へ進む</em>
        </div>
        ${generatedSheet ? `<img src="${escapeHtml(toProjectPath(generatedSheet))}?t=${Date.now()}" alt="生成絵コンテドラフト">` : "<strong>生成絵コンテ未作成</strong>"}
      </article>
      <article class="reference-stack">
        <div class="reference-card">
          <span>Blender実画面</span>
          ${screenCapture?.exists ? `<img src="${escapeHtml(toProjectPath(screenCapture.path))}?t=${encodeURIComponent(screenCapture.mtime_ns || Date.now())}" alt="Blender実画面">` : "<strong>キャプチャ待ち</strong>"}
        </div>
        <div class="reference-card">
          <span>参照カード / 根拠</span>
          ${referenceSheet ? `<img src="${escapeHtml(toProjectPath(referenceSheet))}?t=${Date.now()}" alt="参照画像確認カード">` : "<strong>参照カード未作成</strong>"}
        </div>
      </article>
    </div>

    <div class="storyboard-panel-grid">
      ${jobs.map(job => {
        const panel = panels.find(item => item.id === job.id) || {};
        const image = panel.generated_image || panel.image || job.storyboard_image;
        const ref = panel.reference_image || job.reference_image;
        return `
          <article class="storyboard-card">
            ${image ? `<img src="${escapeHtml(toProjectPath(image))}?t=${Date.now()}" alt="${escapeHtml(panel.title || job.title || job.id)}">` : ""}
            <div>
              <strong>${escapeHtml(panel.title || job.title || job.id)}</strong>
              <span>${escapeHtml(panel.note || job.note || "")}</span>
              <em>生成ドラフト / ${escapeHtml(statusJa(job.status))}</em>
              <small>参照: ${escapeHtml(ref || "-")}</small>
            </div>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

function renderBlenderReview() {
  const target = document.getElementById("blenderReview");
  if (!target) return;
  const review = appState.state.blender_to_seedance || {};
  const source = review.blender_source || {};
  const outputs = review.seedance_outputs || [];
  target.innerHTML = `
    <div class="panel-heading">
      <div>
        <span class="eyebrow">Blender to Seedance</span>
        <h3>プリビズ肉付けレビュー</h3>
      </div>
      <span class="thin-pill warning">追加生成はレビュー後</span>
    </div>
    <div class="blender-review-grid">
      <article class="blender-source-card">
        <div class="review-card-head">
          <span>SOURCE / BLENDER PREVIS</span>
          <strong>主素材</strong>
        </div>
        <img src="${escapeHtml(toProjectPath(source.render_path || appState.state.blender?.render_path || ""))}?t=${Date.now()}" alt="Blenderプリビズ">
        <div class="review-paths">
          <span>${escapeHtml(source.render_path || "")}</span>
          <span>${escapeHtml(source.blend_path || "")}</span>
        </div>
      </article>
      <div class="seedance-output-grid">
        ${outputs.map(item => `
          <article class="seedance-output-card">
            <div class="review-card-head">
              <span>${escapeHtml(item.id || "clip")} / SEEDANCE OUTPUT</span>
              <strong>${escapeHtml(statusJa(item.status))}</strong>
            </div>
            ${item.output ? `
              <div class="video-review-shell">
                <video src="${escapeHtml(toProjectPath(item.output))}" controls muted playsinline preload="metadata"></video>
                ${videoActionsHtml(toProjectPath(item.output), item.id || "seedance-output")}
              </div>
            ` : ""}
            <div class="review-focus-list">
              ${(item.review_focus || []).map(focus => `<span>${escapeHtml(focus)}</span>`).join("")}
            </div>
          </article>
        `).join("")}
      </div>
    </div>
    <div class="support-reference-note">
      <strong>補助参照</strong>
      <span>${escapeHtml(review.support_only?.generated_storyboard || "")}</span>
      <em>${escapeHtml(review.support_only?.note || "生成絵コンテは補助。主軸はBlenderプリビズ。")}</em>
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
  const proofImages = [
    ...(appState.library?.page_renders || []),
    ...(appState.library?.source_captures || []),
  ].filter(item => item.thumbnail_path || item.path).slice(0, 6);
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
  document.getElementById("activity").innerHTML = `
    <div class="ui-proof-grid">
      ${proofImages.map(item => `
        <article>
          <img src="${escapeHtml(toProjectPath(item.thumbnail_path || item.path))}" alt="${escapeHtml(item.name || item.id || "UI proof")}">
          <strong>${escapeHtml(item.name || item.id || "UI")}</strong>
        </article>
      `).join("")}
    </div>
    ${activity.slice(-3).reverse().map(item => `
      <article class="activity-item">
        <strong>${escapeHtml(item.actor || "システム")}</strong>
        <span>${escapeHtml(item.time || "")}</span>
        <span>${escapeHtml(displayText(item.event || ""))}</span>
      </article>
    `).join("")}
  `;
}

function renderLowerData() {
  const images = castImages().slice(0, 8);
  const captures = appState.library?.source_captures || [];
  const blenderRenders = appState.runtime?.blender_assets?.renders || [];
  const liveFrames = appState.runtime?.blender_assets?.live_frames || [];
  const screenCapture = appState.runtime?.blender_assets?.screen_capture;
  const references = appState.library?.external_references || [];
  const blocked = appState.library?.blocked_assets || appState.library?.removed_assets || [];
  const sourceTruth = appState.state.real_links || [];
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
      <div>
        <strong>実データ連動</strong>
        ${sourceTruth.slice(0, 4).map(item => `<span>${escapeHtml(item.label)} / ${escapeHtml(statusJa(item.status))}</span>`).join("") || "<span>状態確認待ち</span>"}
      </div>
    </div>
  `;

  const script = appState.state.script || {};
  const beats = scriptBeats();
  document.getElementById("script").innerHTML = `
    <div class="panel-heading">
      <div><span class="eyebrow">台本</span><h3>${escapeHtml(script.title || "60秒台本")}</h3></div>
      <span class="thin-pill success">${escapeHtml(statusJa(script.status || "done"))}</span>
    </div>
    <div class="script-summary">
      <strong>${escapeHtml(script.logline || "台本待ち")}</strong>
      <span>${escapeHtml(script.voice || "Higgsfield ElevenLabs")} / ${escapeHtml(script.subtitles || "後編集テロップ")}</span>
    </div>
    <div class="script-beat-list">
      ${beats.slice(0, 10).map(beat => `
        <article class="script-beat-card">
          <div><strong>${escapeHtml(beat.time || "")}</strong><span>${escapeHtml(beat.clip || "")}</span></div>
          <p>${escapeHtml(beat.narration || "")}</p>
          <em>${escapeHtml(beat.telop || "")}</em>
        </article>
      `).join("") || "<article class=\"script-beat-card\"><p>台本がまだ登録されていません。</p></article>"}
    </div>
  `;

  const jobs = appState.state.jobs || [];
  document.getElementById("jobs").innerHTML = `
    <div class="panel-heading"><div><span class="eyebrow">Seedanceジョブ</span><h3>${jobs.length}本のクリップ</h3></div></div>
    <div class="overview-list">
      ${jobs.map(job => {
        const linkedBeats = beatsForJob(job);
        return `
        <article class="job-mini-card ${cls(job.status)}">
          <strong>${escapeHtml(displayText(job.title))}</strong>
          <span>${escapeHtml(statusJa(job.status))} / ${escapeHtml(job.primary_reference || "-")} / ${linkedBeats.length}ビート</span>
          <div class="job-linked-beats">
            ${linkedBeats.map(beat => `<b>${escapeHtml(beat.time || "")}</b><em>${escapeHtml(beat.telop || "")}</em>`).join("")}
          </div>
        </article>
      `;}).join("")}
    </div>
  `;

  const conversation = appState.state.generation_conversation || [];
  const palmier = appState.state.palmier || {};
  const conversationEl = document.getElementById("conversation");
  if (conversationEl) {
    conversationEl.innerHTML = `
      <div class="panel-heading">
        <div><span class="eyebrow">生成会話</span><h3>判断ログ / 次の会話</h3></div>
        <span class="thin-pill ${palmier.mcp_status === "connected" ? "success" : "warning"}">${escapeHtml(statusJa(palmier.mcp_status || "waiting"))}</span>
      </div>
      <div class="conversation-list">
        ${conversation.map(item => `
          <article class="conversation-card ${escapeHtml(cls(item.status || item.type))}">
            <div><strong>${escapeHtml(item.speaker || item.type || "system")}</strong><span>${escapeHtml(item.time || "")}</span></div>
            <p>${escapeHtml(item.message || "")}</p>
            ${item.decision ? `<em>${escapeHtml(item.decision)}</em>` : ""}
          </article>
        `).join("") || "<article class=\"conversation-card\"><p>生成会話はまだありません。</p></article>"}
      </div>
      <div class="source-truth-grid">
        ${(appState.state.real_links || []).map(item => `
          <div class="${escapeHtml(cls(item.status))}">
            <strong>${escapeHtml(item.label)}</strong>
            <span>${escapeHtml(item.path || item.note || "")}</span>
            <em>${escapeHtml(statusJa(item.status))}</em>
          </div>
        `).join("")}
      </div>
    `;
  }

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
  renderRequirements();
  renderFactoryOverview();
  renderSystemMonitor();
  renderMarketFeed();
  renderGlobalActivity();
  renderFactoryVisual();
  renderBlenderReview();
  renderStoryboardReview();
  renderPipeline();
  renderRecentOutputs();
  renderGenerationQueue();
  renderActiveGenerations();
  renderMcpBridge();
  renderSystemPerformance();
  renderTerminal();
  renderLowerData();
  // Don't clobber what the user is typing: renderAll runs ~every second, so only
  // seed the field when it isn't focused (otherwise live edits get wiped mid-type).
  const nextInstruction = document.getElementById("nextInstruction");
  if (nextInstruction && document.activeElement !== nextInstruction) {
    nextInstruction.value = appState.state.meta?.next_terminal_instruction || "";
  }
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
  status.textContent = "Codexへ送信中...";
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
  document.getElementById("sendStatus").textContent = "確認メモをコピーしました。";
});

document.getElementById("sendInstruction").addEventListener("click", sendInstruction);
document.getElementById("lowerDataToggle")?.addEventListener("click", event => {
  const section = document.getElementById("lowerDataSection");
  const collapsed = section?.classList.toggle("collapsed");
  event.currentTarget.setAttribute("aria-expanded", String(!collapsed));
  event.currentTarget.querySelector("strong").textContent = collapsed ? "開く" : "閉じる";
});
document.addEventListener("click", event => {
  const button = event.target.closest("[data-video-action='fullscreen']");
  if (!button) return;
  const video = button.closest(".video-review-shell")?.querySelector("video");
  if (video?.requestFullscreen) video.requestFullscreen();
});

loadFactoryData();
setInterval(loadFactoryData, 5000);
setInterval(() => {
  appState.tick += 1;
  document.getElementById("systemTime").textContent = nowJstParts();
}, 1000);
