from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads, dumps as encode_json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from studio.core.approvals import ApprovalLog
from studio.core.jobs import GenerationBlocked, record_generation_result, run_generation_from_contract
from studio.core.registry import AssetRegistry, sha256_file
from studio.memory.production_memory import ProductionMemory
from studio.providers.mock import MockProvider
from studio.providers.seedance import SeedanceProvider

INDEX = """<!doctype html>
<meta charset="utf-8">
<title>Studio v2</title>
<style>
body{margin:0;background:#07111d;color:#eef;font:16px system-ui;padding:24px}
.banner{border:1px solid #0cf;padding:12px;border-radius:8px;margin-bottom:16px}
.card{border:1px solid #345;padding:16px;border-radius:8px;margin:12px 0;background:#101b2b}
.demo{color:#ffd54a;font-weight:700}
label{display:block;margin:8px 0} input{background:#08111f;color:#eef;border:1px solid #456;padding:8px;border-radius:6px}
button{background:#19d3ff;color:#00111d;border:0;border-radius:6px;padding:8px 12px;font-weight:700} button:disabled{opacity:.5}
code{color:#70ffbd}
</style>
<div class="banner"><b>Studio v2</b> / V1 FROZEN — 閲覧専用。制作はStudio v2へ。<br><small>workspace/run/*.permission.json は人間編集の安全装置。execute系trueはself_auditで停止。</small></div>
<div class="card"><h2>作る</h2>
<label>Root <input id="root" value="/tmp/studio-web-demo"></label>
<label>Project <input id="project" value="demo"></label>
<label>商品は？ <input id="product" value="Product"></label>
<label>誰に？ <input id="target" value="general"></label>
<label>どこで使う？ <input id="platform" value="tiktok"></label>
<button onclick="post('/api/create-project',{root:v('root'),project:v('project'),product:v('product'),target:v('target'),platform:v('platform')})">ブリーフ作成</button>
<label>写真パス <input id="asset_path" placeholder="/path/to/photo.png"></label>
<button onclick="post('/api/register-asset',{root:v('root'),asset_id:'photo_001',path:v('asset_path'),asset_kind:'product_photo',rights_status:'ai_generated'})">写真をRegistry登録</button>
</div>
<div class="card"><h2>見る</h2>
<p>承認対象sha256とblocked理由はAPIの値をそのまま表示します。実データ不在時は <span class="demo">DEMO DATA</span>。</p>
<button onclick="loadStatus()">状態を見る</button>
<button onclick="post('/api/approve',{root:v('root'),project:v('project'),target_file:v('asset_path'),target_name:'photo_001'})">採用</button>
<button onclick="post('/api/review',{root:v('root'),project:v('project'),take:'take_001',file:v('asset_path'),verdict:'rejected',failure_tag:'needs_retry'})">やり直し</button>
<label>契約JSON <input id="contract_path" placeholder="/path/to/shot_contract.json"></label>
<label>Provider <input id="provider" value="mock"></label>
<button onclick="post('/api/generate',{root:v('root'),contract:v('contract_path'),take:'take_001',provider:v('provider')})">契約から生成/準備</button>
<label>Request <input id="request_path" placeholder="/path/to/request.json"></label>
<label>Output <input id="output_path" placeholder="/path/to/output.mp4"></label>
<button onclick="post('/api/record',{root:v('root'),request:v('request_path'),output:v('output_path')})">生成結果を記録</button>
</div>
<div class="card"><h2>保存</h2><p>完パケDLはassembly後。公開は人間の外部判断。</p><button disabled title="assembly後に有効">完パケDL</button></div>
<pre id="out" class="card"><span class="demo">DEMO DATA</span></pre>
<script>
const v=id=>document.getElementById(id).value;
async function post(path,payload){ const r=await fetch(path,{method:'POST',body:JSON.stringify(payload)}); out.textContent=await r.text(); }
async function loadStatus(){ const r=await fetch('/api/status?root='+encodeURIComponent(v('root'))); out.textContent=await r.text(); }
</script>
"""


def _root(payload: dict) -> Path:
    return Path(payload["root"]).resolve()


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(encode_json(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _permission_example_path(root: Path) -> Path:
    return root / "permission.json.example"


def api_create_project(payload: dict) -> dict:
    from datetime import UTC, datetime

    root = _root(payload)
    protected = [root / "project.json", root / "permission.json"]
    existing = [str(path) for path in protected if path.exists()]
    if existing:
        return {"blocked": "existing project/permission file would be overwritten", "files": existing}
    now = datetime.now(UTC).isoformat()
    project_id = payload["project"]
    project = {
        "id": project_id,
        "type": "short_ad",
        "status": "briefing",
        "brief": {
            "product": payload.get("product", "Product"),
            "target": payload.get("target", "general"),
            "platform": [payload.get("platform", "tiktok")],
            "duration_sec": float(payload.get("duration_sec", 15)),
            "aspect": payload.get("aspect", "9:16"),
            "language": payload.get("language", "ja"),
            "must_include": [],
            "must_avoid": [],
            "reference_urls": [],
        },
        "budget": {"cap_usd": 20, "daily_cap_usd": 10, "spent_usd": 0, "today_spent_usd": 0, "today_date": "", "generations": 0},
        "audio_policy": {"dialogue": "none", "narration": "post"},
        "bible_ref": "bible.json",
        "shots": ["shot_001"],
        "timeline": "timeline.json",
        "created_at": now,
        "updated_at": now,
    }
    permission = {
        "project": project_id,
        "execute": {
            "gpt_image": False,
            "seedance_estimate": True,
            "seedance_generate": False,
            "higgsfield_image": False,
            "elevenlabs": False,
            "palmier_or_upscale": False,
            "palmier_edit": False,
            "palmier_export": False,
            "publish": False,
        },
        "budget": {"cap_usd": 20, "daily_cap_usd": 10, "max_takes_per_shot": 3, "max_parallel": 1},
        "edited_by": "human_only",
    }
    _write_json(root / "project.json", project)
    _write_json(root / "bible.json", {"project": project_id, "characters": [], "locations": [], "props": [], "style": {}, "brand": {}})
    _write_json(_permission_example_path(root), permission)
    (root / "assets" / "registry.jsonl").parent.mkdir(parents=True, exist_ok=True)
    (root / "assets" / "registry.jsonl").touch()
    (root / "approvals.jsonl").touch()
    return {"project": project, "root": str(root), "permission_template": str(_permission_example_path(root))}


def api_register_asset(payload: dict) -> dict:
    root = _root(payload)
    record = AssetRegistry(root / "assets" / "registry.jsonl").register(
        asset_id=payload["asset_id"],
        file_path=payload["path"],
        asset_kind=payload.get("asset_kind", "product_photo"),
        rights_status=payload.get("rights_status", "unknown"),
        real_face=bool(payload.get("real_face", False)),
        origin={"via": "studio_web"},
    )
    return {"asset": record}


def api_status(root: str | Path) -> dict:
    root = Path(root)
    project_path = root / "project.json"
    registry = AssetRegistry(root / "assets" / "registry.jsonl")
    approvals = ApprovalLog(root / "approvals.jsonl")
    memory_path = root / "memory.sqlite"
    return {
        "demo_data": not project_path.exists(),
        "project": loads(project_path.read_text(encoding="utf-8")) if project_path.exists() else {},
        "assets": registry.records(),
        "approvals": approvals.events(),
        "memory": ProductionMemory(memory_path).counts() if memory_path.exists() else {"generations": 0, "failure_patterns": 0, "playbooks": 0},
    }


def api_approve(payload: dict) -> dict:
    root = _root(payload)
    target = Path(payload["target_file"])
    event = ApprovalLog(root / "approvals.jsonl").append(
        gate=payload.get("gate", "G_storyboard"),
        project=payload["project"],
        target=payload["target_name"],
        target_sha256=sha256_file(target),
        verdict=payload.get("verdict", "approved"),
        note=payload.get("note", "web"),
    )
    return {"event": event}


def api_generate(payload: dict) -> dict:
    root = _root(payload)
    contract = payload.get("contract")
    if not contract:
        return {"blocked": "contract is required"}
    provider_name = payload.get("provider", "mock")
    providers = {"mock": MockProvider, "higgsfield": SeedanceProvider}
    if provider_name not in providers:
        return {"blocked": f"unsupported provider: {provider_name}"}
    try:
        return run_generation_from_contract(root=root, contract_path=Path(contract), provider=providers[provider_name](), take=payload.get("take", "take_001"))
    except (GenerationBlocked, RuntimeError) as exc:
        return {"blocked": str(exc)}


def api_record(payload: dict) -> dict:
    root = _root(payload)
    try:
        return record_generation_result(root=root, request_path=Path(payload["request"]), output_path=Path(payload["output"]), cost_usd=payload.get("cost"), response_path=Path(payload["response"]) if payload.get("response") else None)
    except GenerationBlocked as exc:
        return {"blocked": str(exc)}


def api_review(payload: dict) -> dict:
    root = _root(payload)
    target = Path(payload["file"])
    event = ApprovalLog(root / "approvals.jsonl").append(
        gate="G_take",
        project=payload["project"],
        target=payload["take"],
        target_sha256=sha256_file(target),
        verdict=payload.get("verdict", "approved"),
        note=payload.get("note", "web"),
    )
    ProductionMemory(root / "memory.sqlite").record_generation(
        project=payload["project"],
        take=payload["take"],
        verdict=payload.get("verdict", "approved"),
        failure_tag=payload.get("failure_tag", ""),
        cost_usd=float(payload.get("cost", 0)),
        note=payload.get("note", "web"),
    )
    return {"event": event}


class Handler(BaseHTTPRequestHandler):
    def _send(self, data: dict | str, code: int = 200) -> None:
        body = data.encode("utf-8") if isinstance(data, str) else encode_json(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8" if isinstance(data, str) else "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send(INDEX)
            return
        if parsed.path == "/api/status":
            root = parse_qs(parsed.query).get("root", [""])[0]
            self._send(api_status(root))
            return
        self._send({"error": "not found"}, 404)

    def do_POST(self) -> None:
        payload = loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
        path = urlparse(self.path).path
        if path == "/api/approve":
            self._send(api_approve(payload))
        elif path == "/api/create-project":
            self._send(api_create_project(payload))
        elif path == "/api/register-asset":
            self._send(api_register_asset(payload))
        elif path == "/api/generate":
            self._send(api_generate(payload))
        elif path == "/api/record":
            self._send(api_record(payload))
        elif path == "/api/review":
            self._send(api_review(payload))
        else:
            self._send({"error": "not found"}, 404)


def run(host: str = "127.0.0.1", port: int = 8788) -> None:
    if host not in {"127.0.0.1", "localhost"}:
        raise SystemExit("Studio web UI is local-only; bind to 127.0.0.1")
    HTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    run()
