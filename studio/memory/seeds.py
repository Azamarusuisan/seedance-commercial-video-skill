from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SEED_DIR = Path(__file__).resolve().parent / "seeds"


def load_seed(name: str) -> dict[str, Any]:
    path = Path(os.environ.get("STUDIO_SEED_DIR", str(SEED_DIR))) / f"{name}.json"
    if not path.is_file():
        raise FileNotFoundError(f"seed missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def seed_items(name: str, *, status: str | None = None) -> list[dict[str, Any]]:
    items = load_seed(name).get("items", [])
    if status:
        return [item for item in items if item.get("status") == status]
    return list(items)


def active_items(name: str) -> list[dict[str, Any]]:
    return seed_items(name, status="active")


def candidate_items(name: str) -> list[dict[str, Any]]:
    return seed_items(name, status="candidate")
