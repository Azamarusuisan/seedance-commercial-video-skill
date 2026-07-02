from __future__ import annotations

import re
from pathlib import Path

from studio.core.registry import sha256_file
from studio.memory.production_memory import ProductionMemory
from studio.memory.seeds import active_items


FP_RE = re.compile(r"^## (FP-\d{3}):\s*(.+)$", re.MULTILINE)


def import_known_failures(md_path: str | Path, memory: ProductionMemory) -> int:
    path = Path(md_path)
    text = path.read_text(encoding="utf-8")
    digest = sha256_file(path)
    count = 0
    for fp_id, title in FP_RE.findall(text):
        memory.upsert_failure_pattern(fp_id=fp_id, title=title, source_path=str(path), source_sha256=digest)
        count += 1
    return count


def import_retry_playbooks(memory: ProductionMemory) -> int:
    count = 0
    for item in active_items("retry_playbook"):
        memory.upsert_playbook(tag=item["id"], recipe=item["recipe"], source=item["source"])
        count += 1
    return count


def import_project(project_path: str | Path, memory: ProductionMemory, *, known_failures: str | Path = "references/known-failure-patterns.md") -> dict[str, int]:
    project = Path(project_path)
    imported_files = 0
    if project.exists():
        for path in sorted(project.rglob("*")):
            if path.suffix.lower() not in {".md", ".txt", ".json"}:
                continue
            rel = path.relative_to(project)
            name = path.name.lower()
            if not any(token in name for token in ("prompt", "review", "postmortem", "condition", "brief", "learning", "storyboard")):
                continue
            tag = "postmortem" if "postmortem" in name else "review" if "review" in name else ""
            memory.record_generation(
                project=project.name,
                take=f"v1:{rel}",
                verdict="imported",
                failure_tag=tag,
                note=f"sha256={sha256_file(path)}",
            )
            imported_files += 1
    return {
        "failure_patterns": import_known_failures(known_failures, memory),
        "playbooks": import_retry_playbooks(memory),
        "project_files": imported_files,
    }
