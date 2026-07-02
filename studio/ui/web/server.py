from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads, dumps as encode_json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from studio.core.approvals import ApprovalLog
from studio.core.permission import Permission
from studio.core.registry import AssetRegistry, sha256_file
from studio.memory.production_memory import ProductionMemory
from studio.providers.mock import MockProvider

INDEX = """<!doctype html>
<meta charset="utf-8">
<title>Studio v2</title>
<style>
body{margin:0;background:#07111d;color:#eef;font:16px system-ui;padding:24px}
.banner{border:1px solid #0cf;padding:12px;border-radius:8px;margin-bottom:16px}
.card{border:1px solid #345;padding:16px;border-radius:8px;margin:12px 0;background:#101b2b}
.demo{color:#ffd54a;font-weight:700}
button:disabled{opacity:.5}
</style>
<div class="banner"><b>Studio v2</b> / V1 FROZEN — 閲覧専用。制作はStudio v2へ。</div>
<div class="card"><h2>作る</h2><p>ブリーフ3質問と写真登録はCLI/API経由。実データ不在時は <span class="demo">DEMO DATA</span> と表示。</p></div>
<div class="card"><h2>見る</h2><p>絵コンテ/テイクを承認またはやり直し。UIは台帳へ直接書かず、コアAPIを呼びます。</p></div>
<div class="card"><h2>保存</h2><p>完パケDLはassembly後。公開は人間の外部判断。</p></div>
"""


def _root(payload: dict) -> Path:
    return Path(payload["root"]).resolve()


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
    allowed = Permission.load(root / "permission.json").can_execute("seedance_generate", estimated_cost=float(payload.get("estimated_cost", 1)))
    if not allowed.allowed:
        return {"blocked": allowed.reason}
    result = MockProvider().generate(prompt=payload.get("prompt", "mock"), output_dir=root / "takes", duration_sec=float(payload.get("duration", 4)))
    return {"output_path": str(result.output_path), "provider_job_id": result.job_id}


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
        elif path == "/api/generate":
            self._send(api_generate(payload))
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
