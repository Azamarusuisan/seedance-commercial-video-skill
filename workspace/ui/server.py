#!/usr/bin/env python3
from __future__ import annotations

import argparse
import functools
import json
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / "workspace" / "ui" / "state"
INBOX_PATH = STATE_DIR / "codex-inbox.jsonl"
STATE_PATH = STATE_DIR / "generation-state.json"


def now_label() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def terminal_safe(text: str) -> str:
    allowed_controls = {"\n", "\r", "\t"}
    return "".join(
        char if char >= " " or char in allowed_controls else f"\\x{ord(char):02x}"
        for char in text
    )


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


class CodexWorkflowHandler(SimpleHTTPRequestHandler):
    server_version = "SeedanceWorkflowUI/1.0"

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

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

        print("\n" + "=" * 72)
        print("[Codex inbox] instruction received")
        print(f"time: {record['time']}")
        print(f"source: {source}")
        print("-" * 72)
        print(terminal_safe(message))
        print("=" * 72 + "\n")
        sys.stdout.flush()

        response = {
            "ok": True,
            "queued_at": record["time"],
            "inbox": str(INBOX_PATH.relative_to(REPO_ROOT)),
        }
        body = json.dumps(response, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


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
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Seedance live workflow UI.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
