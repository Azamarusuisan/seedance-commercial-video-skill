#!/usr/bin/env python3
from __future__ import annotations

import argparse
import functools
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / "workspace" / "ui" / "state"
INBOX_PATH = STATE_DIR / "codex-inbox.jsonl"
TERMINAL_FORWARD_LOG = STATE_DIR / "codex-terminal-forward.jsonl"
STATE_PATH = STATE_DIR / "generation-state.json"
ASSET_LIBRARY_PATH = STATE_DIR / "asset-library.json"
ASSET_3D_DIR = REPO_ROOT / "workspace" / "assets" / "3d"
MCP_REQUEST_DIR = REPO_ROOT / "workspace" / "mcp-requests"
LOG_DIR = REPO_ROOT / "workspace" / "logs"


def now_label() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def terminal_safe(text: str) -> str:
    allowed_controls = {"\n", "\r", "\t"}
    return "".join(
        char if char >= " " or char in allowed_controls else f"\\x{ord(char):02x}"
        for char in text
    )


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def file_record(path: Path) -> dict[str, object]:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return {
            "path": rel(path),
            "exists": False,
        }
    return {
        "path": rel(path),
        "exists": True,
        "bytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds"),
        "mtime_ns": stat.st_mtime_ns,
    }


def tail_jsonl(path: Path, limit: int = 25) -> list[dict[str, object]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []

    records: list[dict[str, object]] = []
    for line in lines[-limit:]:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.append({"time": "", "source": "raw", "message": line, "status": "unparsed"})
    return records


def list_recent_files(paths: list[Path], limit: int = 16) -> list[dict[str, object]]:
    records = [file_record(path) for path in paths if path.exists()]
    records.sort(key=lambda item: str(item.get("mtime", "")), reverse=True)
    return records[:limit]


def git_summary() -> dict[str, object]:
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=1.0,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=1.0,
        ).stdout.splitlines()
    except (OSError, subprocess.TimeoutExpired):
        return {"available": False, "branch": "", "changed_files": 0}

    return {
        "available": True,
        "branch": branch,
        "changed_files": len(status),
    }


def blender_summary() -> dict[str, object]:
    cli = shutil.which("blender")
    app_paths = sorted(Path("/Applications").glob("Blender*")) if Path("/Applications").exists() else []
    executable = ""
    if app_paths:
        app_executable = app_paths[0] / "Contents" / "MacOS" / "Blender"
        if app_executable.exists():
            executable = str(app_executable)
    if not executable:
        executable = cli
    version = ""
    if executable:
        try:
            version = subprocess.run(
                [executable, "--version"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=2.0,
            ).stdout.splitlines()[0]
        except (OSError, subprocess.TimeoutExpired, IndexError):
            version = ""
    return {
        "available": bool(cli or app_paths),
        "cli": cli or "",
        "executable": executable or "",
        "version": version,
        "applications": [str(path) for path in app_paths],
        "mode": "local-only",
        "note": "Use only for local 3D preview/render plates; never trigger paid generation.",
    }


def blender_assets() -> dict[str, object]:
    render_dir = ASSET_3D_DIR / "renders"
    blend_dir = ASSET_3D_DIR / "blend"
    manifest_dir = ASSET_3D_DIR / "manifests"
    live_dir = ASSET_3D_DIR / "live"
    renders = [
        file_record(path)
        for path in sorted(render_dir.glob("*"))
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov"}
    ]
    blends = [
        file_record(path)
        for path in sorted(blend_dir.glob("*.blend"))
        if path.is_file()
    ]
    manifests = []
    for path in sorted(manifest_dir.glob("*.json")):
        record = read_json(path, {})
        if isinstance(record, dict):
            record["_file"] = file_record(path)
            manifests.append(record)

    live_frames = [
        file_record(path)
        for path in sorted(live_dir.glob("blender_live_*.png"))
        if path.is_file()
    ]
    live_frames.sort(key=lambda item: str(item.get("mtime", "")), reverse=True)
    live_state_path = live_dir / "live-state.json"
    live_state = read_json(live_state_path, {})
    if isinstance(live_state, dict):
        live_state["_file"] = file_record(live_state_path)
    screen_state_path = live_dir / "blender-screen-state.json"
    screen_state = read_json(screen_state_path, {})
    if isinstance(screen_state, dict):
        screen_state["_file"] = file_record(screen_state_path)
    screen_capture = file_record(live_dir / "blender_screen_current.png")

    renders.sort(key=lambda item: str(item.get("mtime", "")), reverse=True)
    latest = renders[0] if renders else None
    screen_status = screen_state.get("status") if isinstance(screen_state, dict) else ""
    live_status = live_state.get("status") if isinstance(live_state, dict) else ""
    return {
        "root": rel(ASSET_3D_DIR),
        "render_dir": rel(render_dir),
        "blend_dir": rel(blend_dir),
        "manifest_dir": rel(manifest_dir),
        "live_dir": rel(live_dir),
        "renders": renders,
        "blends": blends,
        "manifests": manifests,
        "live_frames": live_frames,
        "live_state": live_state,
        "screen_state": screen_state,
        "screen_capture": screen_capture,
        "latest_live_frame": live_frames[0] if live_frames else None,
        "latest_render": latest,
        "status": screen_status or live_status or ("ready" if latest else "waiting_for_render"),
    }


def higgsfield_mcp_state() -> dict[str, object]:
    requests = []
    for path in sorted(MCP_REQUEST_DIR.glob("*.json")):
        record = read_json(path, {})
        if isinstance(record, dict):
            record["_file"] = file_record(path)
            requests.append(record)

    logs = []
    for path in sorted(LOG_DIR.glob("*.json")):
        record = read_json(path, {})
        if isinstance(record, dict):
            record["_file"] = file_record(path)
            logs.append(record)

    return {
        "mode": "prepared-request-handoff",
        "direct_tool_visible": False,
        "local_only": True,
        "requests_dir": rel(MCP_REQUEST_DIR),
        "logs_dir": rel(LOG_DIR),
        "requests": requests,
        "logs": logs,
        "result_urls": file_record(LOG_DIR / "result-urls.md"),
        "pending": sum(1 for item in logs if item.get("status") == "pending_mcp_execution"),
        "blocked": sum(1 for item in logs if item.get("status") == "blocked"),
        "note": "The local UI prepares and watches Higgsfield MCP handoff files. It does not call paid generation APIs.",
    }


def factory_data(server_address: tuple[str, int]) -> dict[str, object]:
    state = read_json(STATE_PATH, {})
    library = read_json(ASSET_LIBRARY_PATH, {})

    cast_manifest_path = REPO_ROOT / "workspace" / "assets" / "cast" / "generated_20260629" / "cast-manifest.json"
    manifest_ref = library.get("generated_cast_manifest", {}) if isinstance(library, dict) else {}
    if isinstance(manifest_ref, dict) and manifest_ref.get("path"):
        cast_manifest_path = REPO_ROOT / str(manifest_ref["path"])
    cast_manifest = read_json(cast_manifest_path, {})

    generated_cast_files = sorted((REPO_ROOT / "workspace" / "assets" / "cast" / "generated_20260629").glob("*.png"))
    source_capture_files = [
        path
        for path in sorted((REPO_ROOT / "videos").glob("**/*"))
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".html", ".mp4"}
        and not path.name.startswith("x-reference-")
    ]
    render_outputs = [
        path
        for path in sorted((REPO_ROOT / "videos").glob("**/*"))
        if path.is_file() and path.suffix.lower() in {".mp4", ".mov", ".wav", ".mp3", ".m4a"}
    ]
    jobs = state.get("jobs", []) if isinstance(state, dict) else []
    workflow = state.get("workflow", []) if isinstance(state, dict) else []
    gates = state.get("gates", []) if isinstance(state, dict) else []
    inbox = tail_jsonl(INBOX_PATH)
    terminal_forward_log = tail_jsonl(TERMINAL_FORWARD_LOG)
    blender_asset_data = blender_assets()
    higgsfield_mcp = higgsfield_mcp_state()
    mcp_request_files = sorted(MCP_REQUEST_DIR.glob("*.json"))
    mcp_log_files = sorted(LOG_DIR.glob("*.json"))
    tracked_paths = [
        STATE_PATH,
        ASSET_LIBRARY_PATH,
        INBOX_PATH,
        cast_manifest_path,
        *mcp_request_files[-6:],
        *mcp_log_files[-6:],
        *generated_cast_files[-8:],
        *source_capture_files[-8:],
        *render_outputs[-8:],
    ]

    host, port = server_address
    return {
        "ok": True,
        "generated_at": now_label(),
        "local_server": {
            "host": host,
            "port": port,
            "local_only": host in {"127.0.0.1", "localhost", "::1"},
            "package_mode": "local-first",
            "storage": "workspace/ui/state/*.json + project asset folders",
            "terminal_forward_enabled": terminal_forward_enabled(),
            "terminal_forward_app": os.environ.get("CODEX_TERMINAL_APP", "Terminal"),
        },
        "state": state,
        "library": library,
        "cast_manifest": cast_manifest,
        "inbox": inbox,
        "terminal_forward_log": terminal_forward_log,
        "counts": {
            "workflow_steps": len(workflow),
            "jobs": len(jobs),
            "active_jobs": sum(1 for job in jobs if job.get("status") not in {"done", "completed", "discard"}),
            "gates": len(gates),
            "blocked_gates": sum(1 for gate in gates if gate.get("status") == "blocked"),
            "generated_cast_files": len(generated_cast_files),
            "library_source_captures": len(library.get("source_captures", [])) if isinstance(library, dict) else 0,
            "library_page_renders": len(library.get("page_renders", [])) if isinstance(library, dict) else 0,
            "blender_renders": len(blender_asset_data["renders"]),
            "blender_blends": len(blender_asset_data["blends"]),
            "blender_manifests": len(blender_asset_data["manifests"]),
            "blender_live_frames": len(blender_asset_data["live_frames"]),
            "blender_screen_captures": 1 if blender_asset_data.get("screen_capture", {}).get("exists") else 0,
            "source_capture_files": len(source_capture_files),
            "render_outputs": len(render_outputs),
            "inbox_messages": len(inbox),
            "terminal_forward_messages": len(terminal_forward_log),
            "higgsfield_mcp_requests": len(higgsfield_mcp["requests"]),
            "higgsfield_mcp_logs": len(higgsfield_mcp["logs"]),
            "higgsfield_mcp_pending": higgsfield_mcp["pending"],
            "higgsfield_mcp_blocked": higgsfield_mcp["blocked"],
        },
        "files": {
            "state": file_record(STATE_PATH),
            "asset_library": file_record(ASSET_LIBRARY_PATH),
            "codex_inbox": file_record(INBOX_PATH),
            "terminal_forward_log": file_record(TERMINAL_FORWARD_LOG),
            "cast_manifest": file_record(cast_manifest_path),
            "recent": list_recent_files(tracked_paths),
        },
        "git": git_summary(),
        "blender": blender_summary(),
        "blender_assets": blender_asset_data,
        "higgsfield_mcp": higgsfield_mcp,
    }


def append_activity(message: str, source: str) -> None:
    if not STATE_PATH.exists():
        return
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    meta = state.setdefault("meta", {})
    meta["codex_status"] = "terminal_instruction_received"
    meta["last_sent_to_codex_at"] = now_label()
    meta["last_sent_to_codex_message"] = message

    activity = state.setdefault("activity", [])
    activity.append(
        {
            "time": now_label(),
            "actor": source or "UI",
            "event": "Sent instruction to Codex inbox.",
        }
    )
    state["activity"] = activity[-50:]
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def append_terminal_forward_log(payload: dict[str, object]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with TERMINAL_FORWARD_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def terminal_forward_enabled() -> bool:
    return os.environ.get("CODEX_FORWARD_TO_TERMINAL", "0").strip().lower() in {"1", "true", "yes", "on"}


def forward_to_terminal(record: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {
        "enabled": terminal_forward_enabled(),
        "attempted": False,
        "ok": False,
        "app": os.environ.get("CODEX_TERMINAL_APP", "Terminal"),
        "message": "",
    }
    if not result["enabled"]:
        result["message"] = "ターミナル転送はOFFです。CODEX_FORWARD_TO_TERMINAL=1 で有効化できます。"
        append_terminal_forward_log({"time": now_label(), **result})
        return result

    text = str(record.get("message", "")).strip()
    if not text:
        result["message"] = "転送するメッセージが空です。"
        append_terminal_forward_log({"time": now_label(), **result})
        return result

    result["attempted"] = True
    app = str(result["app"] or "Terminal")
    paste_text = text + "\n"
    try:
        subprocess.run(
            ["pbcopy"],
            input=paste_text,
            text=True,
            check=True,
            timeout=2.0,
        )
        apple_script = f'''
tell application "{app}" to activate
delay 0.15
tell application "System Events"
  keystroke "v" using command down
  key code 36
end tell
'''
        proc = subprocess.run(
            ["osascript"],
            input=apple_script,
            text=True,
            capture_output=True,
            check=False,
            timeout=4.0,
        )
        if proc.returncode == 0:
            result["ok"] = True
            result["message"] = f"{app} へ貼り付けて送信しました。"
        else:
            result["message"] = proc.stderr.strip() or proc.stdout.strip() or "osascript failed"
    except (OSError, subprocess.SubprocessError) as exc:
        result["message"] = str(exc)

    append_terminal_forward_log({"time": now_label(), **result})
    return result


class CodexWorkflowHandler(SimpleHTTPRequestHandler):
    server_version = "SeedanceWorkflowUI/1.0"

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/factory-data":
            self.send_json(factory_data(self.server.server_address))
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/send-to-codex":
            self.send_error(404, "Unknown endpoint")
            return

        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError:
            self.send_error(400, "Invalid content length")
            return

        if length <= 0 or length > 256_000:
            self.send_error(400, "Invalid payload size")
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400, "Invalid JSON")
            return

        message = str(payload.get("message", "")).strip()
        source = str(payload.get("source", "UI")).strip() or "UI"
        if not message:
            self.send_error(400, "message is required")
            return

        STATE_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "time": now_label(),
            "source": source,
            "message": message,
            "status": "queued",
        }
        with INBOX_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

        append_activity(message, source)
        terminal_forward = forward_to_terminal(record)

        print("\n" + "=" * 72)
        print("[Codex inbox] instruction received")
        print(f"time: {record['time']}")
        print(f"source: {source}")
        print(f"terminal_forward: {terminal_forward}")
        print("-" * 72)
        print(terminal_safe(message))
        print("=" * 72 + "\n")
        sys.stdout.flush()

        response = {
            "ok": True,
            "queued_at": record["time"],
            "inbox": str(INBOX_PATH.relative_to(REPO_ROOT)),
            "terminal_forward": terminal_forward,
        }
        self.send_json(response)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--bind", default="127.0.0.1")
    args = parser.parse_args()

    handler = functools.partial(CodexWorkflowHandler, directory=str(REPO_ROOT))
    server = ThreadingHTTPServer((args.bind, args.port), handler)

    print("Seedance live workflow UI:")
    print(f"  http://{args.bind}:{args.port}/workspace/ui/live-workflow.html")
    print(f"  http://{args.bind}:{args.port}/workspace/ui/generation-checkpoint.html")
    print("Codex inbox endpoint:")
    print(f"  http://{args.bind}:{args.port}/api/send-to-codex")
    print("Factory data endpoint:")
    print(f"  http://{args.bind}:{args.port}/api/factory-data")
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Seedance live workflow UI.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
