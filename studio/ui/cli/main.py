from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from studio.agents.compiler import compile_prompt
from studio.assembly.ffmpeg import assemble_videos
from studio.assembly.palmier import prepare_palmier_request, record_palmier_export
from studio.core.approvals import ApprovalLog
from studio.core.contract_validator import validate_contract
from studio.core.jobs import GenerationBlocked, record_generation_result, run_generation_from_contract
from studio.core.registry import AssetRegistry, sha256_file
from studio.memory.import_v1 import import_project
from studio.memory.production_memory import ProductionMemory
from studio.providers.mock import MockProvider
from studio.providers.seedance import SeedanceProvider
from studio.schemas.validate import validate_document


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _permission_example_path(root: Path) -> Path:
    return root / "permission.json.example"


def _provider(name: str):
    if name == "mock":
        return MockProvider()
    if name == "higgsfield":
        return SeedanceProvider()
    raise SystemExit(f"blocked: unsupported provider {name}")


def cmd_new(args: argparse.Namespace) -> None:
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    protected = [root / "project.json", root / "permission.json"]
    existing = [str(path) for path in protected if path.exists()]
    if existing:
        raise SystemExit("blocked: existing project/permission file would be overwritten: " + ", ".join(existing))
    now = datetime.now(UTC).isoformat()
    project = {
        "id": args.project,
        "type": "short_ad",
        "status": "briefing",
        "brief": {
            "product": args.product,
            "target": "general",
            "platform": ["tiktok"],
            "duration_sec": 8,
            "aspect": "9:16",
            "language": "ja",
            "must_include": [],
            "must_avoid": [],
            "reference_urls": [],
        },
        "budget": {"cap_usd": 20, "daily_cap_usd": 10, "spent_usd": 0, "today_spent_usd": 0, "today_date": "", "generations": 0},
        "audio_policy": {"dialogue": "seedance_native", "narration": "elevenlabs"},
        "bible_ref": "bible.json",
        "shots": ["shot_001"],
        "timeline": "timeline.json",
        "created_at": now,
        "updated_at": now,
    }
    bible = {"project": args.project, "characters": [], "locations": [], "props": [], "style": {}, "brand": {}}
    permission = {
        "project": args.project,
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
    _write_json(root / "bible.json", bible)
    _write_json(_permission_example_path(root), permission)
    (root / "assets").mkdir(exist_ok=True)
    (root / "assets" / "registry.jsonl").touch()
    (root / "approvals.jsonl").touch()
    print(f"{root}\npermission template: {_permission_example_path(root)} (rename to permission.json after human approval)")


def cmd_status(args: argparse.Namespace) -> None:
    root = Path(args.root)
    project = json.loads((root / "project.json").read_text(encoding="utf-8"))
    print(f"{project['id']}: {project['status']}")
    mem = root / "memory.sqlite"
    if mem.exists():
        print(f"memory: {ProductionMemory(mem).counts()}")


def cmd_validate(args: argparse.Namespace) -> None:
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    validate_document(data, args.schema)
    print("ok")


def cmd_approve(args: argparse.Namespace) -> None:
    target = Path(args.target)
    log = ApprovalLog(Path(args.root) / "approvals.jsonl")
    event = log.append(gate=args.gate, project=args.project, target=args.name, target_sha256=sha256_file(target), verdict=args.verdict, note=args.note)
    print(event["event_id"])


def cmd_estimate(args: argparse.Namespace) -> None:
    prompt = Path(args.prompt).read_text(encoding="utf-8")
    try:
        est = _provider(args.provider).estimate(prompt=prompt, duration_sec=args.duration)
    except RuntimeError as exc:
        raise SystemExit(f"blocked: {exc}") from exc
    print(json.dumps(est.__dict__, ensure_ascii=False))
    if getattr(args, "root", None):
        mem = Path(args.root) / "memory.sqlite"
        if mem.exists():
            print(json.dumps({"memory": ProductionMemory(mem).counts()}, ensure_ascii=False))


def cmd_generate(args: argparse.Namespace) -> None:
    try:
        result = run_generation_from_contract(root=Path(args.root), contract_path=Path(args.contract), provider=_provider(args.provider), take=args.take)
    except GenerationBlocked as exc:
        raise SystemExit(f"blocked: {exc}") from exc
    print(result.get("output_path") or result.get("request_path"))


def cmd_record(args: argparse.Namespace) -> None:
    try:
        result = record_generation_result(root=Path(args.root), request_path=Path(args.request), output_path=Path(args.output), cost_usd=args.cost, response_path=Path(args.response) if args.response else None)
    except GenerationBlocked as exc:
        raise SystemExit(f"blocked: {exc}") from exc
    if result.get("unauthorized"):
        print("WARNING: recorded output was not authorized by current permission")
    print(result["output_path"])


def cmd_assemble(args: argparse.Namespace) -> None:
    out = assemble_videos([Path(item) for item in args.inputs], Path(args.output))
    print(out)


def cmd_review(args: argparse.Namespace) -> None:
    root = Path(args.root)
    log = ApprovalLog(Path(args.root) / "approvals.jsonl")
    event = log.append(
        gate="G_take",
        project=args.project,
        target=args.take,
        target_sha256=sha256_file(args.file),
        verdict=args.verdict,
        note=args.note,
    )
    ProductionMemory(root / "memory.sqlite").record_generation(
        project=args.project,
        take=args.take,
        verdict=args.verdict,
        failure_tag=args.failure_tag,
        cost_usd=args.cost,
        note=args.note,
    )
    print(event["event_id"])


def cmd_compile(args: argparse.Namespace) -> None:
    root = Path(args.root)
    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    bible = json.loads((root / "bible.json").read_text(encoding="utf-8"))
    registry = AssetRegistry(root / "assets" / "registry.jsonl")
    report = validate_contract(contract, registry)
    if not report.ok:
        raise SystemExit("; ".join(report.blocked))
    prompt = compile_prompt(contract, bible, registry)
    Path(args.output).write_text(prompt + "\n", encoding="utf-8")
    print(args.output)


def cmd_import(args: argparse.Namespace) -> None:
    root = Path(args.root)
    result = import_project(args.source, ProductionMemory(root / "memory.sqlite"))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


def cmd_export_prepare(args: argparse.Namespace) -> None:
    try:
        result = prepare_palmier_request(root=Path(args.root), inputs=[Path(item) for item in args.inputs], instruction=args.instruction)
    except GenerationBlocked as exc:
        raise SystemExit(f"blocked: {exc}") from exc
    print(result["request_path"])


def cmd_export_record(args: argparse.Namespace) -> None:
    try:
        result = record_palmier_export(root=Path(args.root), request_path=Path(args.request), output_path=Path(args.output))
    except GenerationBlocked as exc:
        raise SystemExit(f"blocked: {exc}") from exc
    if result.get("unauthorized"):
        print("WARNING: recorded Palmier export was not authorized by current permission")
    print(result["output_path"])


def main() -> None:
    parser = argparse.ArgumentParser(prog="studio")
    sub = parser.add_subparsers(required=True)
    p = sub.add_parser("new")
    p.add_argument("--root", required=True)
    p.add_argument("--project", required=True)
    p.add_argument("--product", default="Product")
    p.set_defaults(func=cmd_new)
    p = sub.add_parser("status")
    p.add_argument("--root", required=True)
    p.set_defaults(func=cmd_status)
    p = sub.add_parser("validate")
    p.add_argument("schema")
    p.add_argument("file")
    p.set_defaults(func=cmd_validate)
    p = sub.add_parser("approve")
    p.add_argument("--root", required=True)
    p.add_argument("--project", required=True)
    p.add_argument("--gate", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--verdict", default="approved", choices=["approved", "rejected", "revoked"])
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_approve)
    p = sub.add_parser("estimate")
    p.add_argument("--prompt", required=True)
    p.add_argument("--duration", type=float, default=8)
    p.add_argument("--provider", choices=["mock", "higgsfield"], default="mock")
    p.set_defaults(func=cmd_estimate)
    p = sub.add_parser("cost")
    p.add_argument("--prompt", required=True)
    p.add_argument("--duration", type=float, default=8)
    p.add_argument("--root")
    p.add_argument("--provider", choices=["mock", "higgsfield"], default="mock")
    p.set_defaults(func=cmd_estimate)
    p = sub.add_parser("generate")
    p.add_argument("--root", required=True)
    p.add_argument("--contract", required=True)
    p.add_argument("--take", default="take_001")
    p.add_argument("--provider", choices=["mock", "higgsfield"], default="mock")
    p.set_defaults(func=cmd_generate)
    p = sub.add_parser("record")
    p.add_argument("--root", required=True)
    p.add_argument("--request", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--cost", type=float)
    p.add_argument("--response")
    p.set_defaults(func=cmd_record)
    p = sub.add_parser("assemble")
    p.add_argument("--output", required=True)
    p.add_argument("inputs", nargs="+")
    p.set_defaults(func=cmd_assemble)
    p = sub.add_parser("review")
    p.add_argument("--root", required=True)
    p.add_argument("--project", required=True)
    p.add_argument("--take", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--verdict", default="approved", choices=["approved", "rejected", "revoked"])
    p.add_argument("--failure-tag", default="")
    p.add_argument("--cost", type=float, default=0)
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_review)
    p = sub.add_parser("compile")
    p.add_argument("--root", required=True)
    p.add_argument("--contract", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_compile)
    p = sub.add_parser("import")
    p.add_argument("--root", required=True)
    p.add_argument("source")
    p.set_defaults(func=cmd_import)
    p = sub.add_parser("export-prepare")
    p.add_argument("--root", required=True)
    p.add_argument("--instruction", default="")
    p.add_argument("inputs", nargs="+")
    p.set_defaults(func=cmd_export_prepare)
    p = sub.add_parser("export-record")
    p.add_argument("--root", required=True)
    p.add_argument("--request", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_export_record)
    args = parser.parse_args()
    args.func(args)
