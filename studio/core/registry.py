from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class AssetRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def records(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def get(self, asset_id: str) -> dict[str, Any] | None:
        for record in reversed(self.records()):
            if record.get("asset_id") == asset_id:
                return record
        return None

    def register(
        self,
        *,
        asset_id: str,
        file_path: str | Path,
        asset_kind: str,
        rights_status: str,
        real_face: bool = False,
        origin: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        allowed = rights_status != "unknown" and not real_face
        record = {
            "asset_id": asset_id,
            "path": str(file_path),
            "sha256": sha256_file(file_path),
            "asset_kind": asset_kind,
            "origin": origin or {},
            "rights_status": rights_status,
            "real_face": bool(real_face),
            "seedance_upload_allowed": allowed,
            "registered_at": datetime.now(UTC).isoformat(),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record

    def verify_sha(self, asset_id: str) -> bool:
        record = self.get(asset_id)
        if not record:
            return False
        path = Path(record["path"])
        return path.is_file() and sha256_file(path) == record.get("sha256")
