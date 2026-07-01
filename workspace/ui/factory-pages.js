const PAGE_API = "/api/factory-data";
const PAGE_STATE_PATH = "state/generation-state.json";
const PAGE_LIBRARY_PATH = "state/asset-library.json";

const PAGE_NAV = [
  ["factory", "工場", "live-workflow.html"],
  ["studio-lines", "制作ライン", "studio-lines.html"],
  ["assets", "素材", "assets.html"],
  ["cast-library", "演者ライブラリ", "cast-library.html"],
  ["script", "台本", "script.html"],
  ["jobs", "ジョブ", "jobs.html"],
  ["gates", "ゲート", "gates.html"],
  ["activity", "履歴", "activity.html"],
];

const PAGE_META = {
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
          <h1>生成工場</h1>
          <p>AI動画制作スタジオ</p>
          </div>
        </div>
        <nav class="rail-nav">${navMarkup()}</nav>
        <section class="rail-card">
          <span class="eyebrow">状態ファイル</span>
          <code>workspace/ui/state/generation-state.json</code>
          <p id="loadStatus">接続中...</p>
        </section>
        <section class="rail-card compact">
          <span class="eyebrow">ページの目的</span>
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
            <div class="status-tile"><span>システム時刻</span><strong id="systemTime">--:--:--</strong><small>JST</small></div>
            <div class="status-tile live"><span>データ元</span><strong>ローカル状態</strong><small>${html(meta.source)}</small></div>
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
  const meta = PAGE_META[pageState.page];
  const counts = pageState.runtime?.counts || {};
  document.getElementById("pageHero").innerHTML = `
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

function renderStudioLines() {
  const workflow = pageState.state.workflow || [];
  return `
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">制作ライン</span><h3>実データから見る工程</h3></div></div>
      <div class="line-board">
        ${workflow.map((phase, index) => `
          <article class="line-card ${statusClass(phase.status)}">
            <span class="thin-pill ${statusClass(phase.status)}">${html(statusJa(phase.status))}</span>
            <h3>${String(index + 1).padStart(2, "0")} / ${html(phase.label)}</h3>
            <p>${html(displayText(phase.note))}</p>
            <div class="kv-grid"><span>担当</span><strong>${html(displayText(phase.owner))}</strong><span>出力</span><strong>${html(displayText(phase.output))}</strong></div>
          </article>
        `).join("")}
      </div>
    </section>
    <section class="page-panel">
      <span class="eyebrow">現在の作業</span>
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
  const blenderAssets = pageState.runtime?.blender_assets || {};
  const blenderRenders = blenderAssets.renders || [];
  const blenderScreen = blenderAssets.screen_capture || {};
  const blenderScreenState = blenderAssets.screen_state || {};
  const blenderManifests = blenderAssets.manifests || [];
  return `
    <section class="page-panel">
      <div class="panel-heading"><div><span class="eyebrow">素材棚</span><h3>ローカル素材一覧</h3></div></div>
      <div class="binding-grid large">
        <div><span>生成演者</span><strong>${pageState.runtime?.counts?.generated_cast_files ?? 0}</strong></div>
        <div><span>ソースキャプチャ</span><strong>${captures.length}</strong></div>
        <div><span>ページレンダー</span><strong>${pageRenders.length}</strong></div>
        <div><span>外部参考</span><strong>${refs.length}</strong></div>
        <div><span>ブロック記録</span><strong>${blocked.length}</strong></div>
        <div><span>Blender素材</span><strong>${blenderRenders.length + (blenderScreen.exists ? 1 : 0)}</strong></div>
      </div>
    </section>
    <section class="page-panel">
      <span class="eyebrow">Blender / 3Dプレビューレーン</span>
      <h3>${blender.available ? "利用可能" : "未検出"}</h3>
      <p>${html(displayText(blender.note || "Local-only Blender lane for 3D preview plates."))}</p>
      <div class="kv-grid"><span>実行ファイル</span><strong>${html(blender.executable || blender.cli || "未検出")}</strong><span>バージョン</span><strong>${html(blender.version || "-")}</strong><span>方式</span><strong>${html(blender.mode || "ローカル限定")}</strong><span>状態</span><strong>${html(statusJa(blenderAssets.status || "waiting"))}</strong></div>
    </section>
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">Blender実画面</span><h3>ワークフロー中央へ投影</h3></div></div>
      <div class="render-shelf">
        ${blenderScreen.exists ? `
          <article class="render-card">
            <img src="${html(toProjectPath(blenderScreen.path))}?t=${encodeURIComponent(blenderScreen.mtime || "")}" alt="Blender実画面キャプチャ">
            <div>
              <strong>${html(blenderScreen.path)}</strong>
              <span>${html(statusJa(blenderScreenState.status || "captured"))} / ${html(blenderScreenState.window_rect || "")} / ${html(blenderScreen.mtime || "")}</span>
            </div>
          </article>
        ` : "<article class=\"render-card\"><div><strong>Blender実画面なし</strong><span>workspace/scripts/capture-blender-screen.sh を実行</span></div></article>"}
      </div>
    </section>
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">Blenderライブプレート</span><h3>レンダー結果とマニフェスト</h3></div></div>
      <div class="render-shelf">
        ${blenderRenders.map(item => `
          <article class="render-card">
            ${item.path && item.path.match(/\.(png|jpe?g|webp)$/i) ? `<img src="${html(toProjectPath(item.path))}?t=${encodeURIComponent(item.mtime || "")}" alt="${html(item.path)}">` : ""}
            <div>
              <strong>${html(item.path)}</strong>
              <span>${html(item.mtime || "")} / ${html(item.bytes || 0)} bytes</span>
            </div>
          </article>
        `).join("") || "<article class=\"render-card\"><div><strong>Blenderレンダーなし</strong><span>workspace/scripts/render-blender-demo.sh を実行</span></div></article>"}
      </div>
      <div class="data-list">
        ${blenderManifests.map(item => `<article><strong>${html(item.name || item.id)}</strong><span>${html(item.path || "")} / ${html(statusJa(item.review_status || ""))}</span></article>`).join("") || "<article><strong>マニフェストなし</strong><span>レンダースクリプトが workspace/assets/3d/manifests/*.json に書き込みます</span></article>"}
      </div>
    </section>
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">ページレンダー</span><h3>ダウンロード可能なローカル出力</h3></div></div>
      <div class="data-list">
        ${pageRenders.map(item => `<article><strong>${html(item.name || item.id)}</strong><span>${html(item.type)} / ${html(item.path)}</span></article>`).join("") || "<article><strong>ページレンダーなし</strong><span>先にローカルレンダー取得を実行</span></article>"}
      </div>
    </section>
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">ソースキャプチャ</span><h3>ワークフローと操作画面の記録</h3></div></div>
      <div class="data-list">
        ${captures.map(item => `<article><strong>${html(item.name || item.id)}</strong><span>${html(item.type)} / ${html(item.path)}</span></article>`).join("") || "<article><strong>キャプチャなし</strong><span>source capturesフォルダは空です</span></article>"}
      </div>
    </section>
  `;
}

function renderCastLibrary() {
  const cast = pageState.castManifest?.cast || [];
  return `
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">AI演者ライブラリ</span><h3>${cast.length}人の生成演者</h3></div><span class="thin-pill success">使用中ライブラリ</span></div>
      <div class="cast-library-grid">
        ${cast.map(item => `
          <article class="cast-card">
            <img src="${html(toProjectPath(item.asset_path))}" alt="${html(item.name)}">
            <div>
              <h3>${html(item.name)}</h3>
              <span>${html(item.id)}</span>
              <p>${html(displayText(item.role))}</p>
              <div class="kv-grid"><span>権利</span><strong>${html(displayText(item.rights_status))}</strong><span>範囲</span><strong>${html(displayText(item.use_scope))}</strong></div>
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderScript() {
  const script = pageState.state.script || {};
  const beats = script.beats || [];
  const voiceLines = script.voice_script?.length ? script.voice_script : beats.map(beat => beat.narration).filter(Boolean);
  const telopLines = script.telop_plan?.length ? script.telop_plan : beats.map(beat => beat.telop).filter(Boolean);
  return `
    <section class="page-panel wide">
      <div class="panel-heading">
        <div><span class="eyebrow">60秒台本</span><h3>${html(script.title || "台本未登録")}</h3></div>
        <span class="thin-pill success">${html(statusJa(script.status || "done"))}</span>
      </div>
      <div class="script-board">
        ${beats.map(beat => `
          <article class="script-row">
            <div><strong>${html(beat.time || "")}</strong><span>${html(beat.clip || "")}</span></div>
            <div><span>映像</span><p>${html(beat.visual || "")}</p></div>
            <div><span>ナレーション</span><p>${html(beat.narration || "")}</p></div>
            <div><span>テロップ</span><strong>${html(beat.telop || "")}</strong></div>
          </article>
        `).join("") || "<article class=\"script-row\"><p>台本がまだ登録されていません。</p></article>"}
      </div>
    </section>
    <section class="page-panel">
      <div class="panel-heading"><div><span class="eyebrow">音声台本</span><h3>${html(script.voice || "Higgsfield ElevenLabs")}</h3></div></div>
      <div class="script-line-list">${voiceLines.map(line => `<p>${html(line)}</p>`).join("")}</div>
    </section>
    <section class="page-panel">
      <div class="panel-heading"><div><span class="eyebrow">字幕テロップ</span><h3>${html(script.subtitles || "後編集")}</h3></div></div>
      <div class="script-line-list">${telopLines.map(line => `<p>${html(line)}</p>`).join("")}</div>
    </section>
  `;
}

function renderJobs() {
  const jobs = pageState.state.jobs || [];
  return `
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">Seedanceジョブ</span><h3>実ジョブ状態</h3></div><span class="thin-pill danger">有料生成未実行</span></div>
      <div class="job-table">
        ${jobs.map(job => `
          <article class="job-row ${statusClass(job.status)}">
            <div><strong>${html(displayText(job.title))}</strong><span>${html(job.id)}</span></div>
            <div><span>状態</span><strong>${html(statusJa(job.status))}</strong></div>
            <div><span>参照素材</span><strong>${html(job.primary_reference || "-")}</strong></div>
            <div><span>クレジット</span><strong>${html(displayText(job.cost_credits || "not estimated"))}</strong></div>
            <div><span>レビュー</span><strong>${html(statusJa(job.review || "pending"))}</strong></div>
            <p>${html(displayText(job.note || ""))}</p>
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
      <div class="panel-heading"><div><span class="eyebrow">安全ゲート</span><h3>生成・公開前の停止条件</h3></div></div>
      <div class="gate-grid">
        ${gates.map(gate => `
          <article class="gate-detail ${statusClass(gate.status)}">
            <span class="thin-pill ${statusClass(gate.status)}">${html(statusJa(gate.status))}</span>
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
      <div class="panel-heading"><div><span class="eyebrow">履歴</span><h3>状態監査ログ</h3></div></div>
      <div class="data-list">${activity.slice().reverse().map(item => `<article><strong>${html(displayText(item.actor))}</strong><span>${html(item.time)} / ${html(displayText(item.event))}</span></article>`).join("")}</div>
    </section>
    <section class="page-panel">
      <div class="panel-heading"><div><span class="eyebrow">Codex受信箱</span><h3>${inbox.length}件のメッセージ</h3></div></div>
      <div class="data-list">${inbox.slice().reverse().slice(0, 8).map(item => `<article><strong>${html(item.source || "UI")}</strong><span>${html(item.time)} / ${html(item.message || "")}</span></article>`).join("") || "<article><strong>空</strong><span>配布モードでは受信箱ログなし</span></article>"}</div>
    </section>
    <section class="page-panel wide">
      <div class="panel-heading"><div><span class="eyebrow">監視ファイル</span><h3>${files.length}件の最近更新</h3></div><span class="thin-pill">git ${html(pageState.runtime?.git?.changed_files ?? 0)}件変更</span></div>
      <div class="data-list">${files.map(file => `<article><strong>${html(file.path)}</strong><span>${html(file.mtime || "")} / ${html(file.bytes || 0)} bytes</span></article>`).join("")}</div>
    </section>
  `;
}

function renderPageContent() {
  const renderers = {
    "studio-lines": renderStudioLines,
    assets: renderAssets,
    "cast-library": renderCastLibrary,
    script: renderScript,
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
