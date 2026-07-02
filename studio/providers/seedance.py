from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from studio.memory.seeds import active_items
from studio.providers.base import Estimate


def execution_token(data: dict[str, Any]) -> str:
    payload = {key: value for key, value in data.items() if key != "execution_token"}
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


class SeedanceProvider:
    provider = "higgsfield-seedance"
    model = "seedance-2.0"
    mode = "prepare"

    def estimate(self, *, prompt: str, duration_sec: float = 0, kind: str = "video") -> Estimate:
        price = next((item for item in active_items("provider_pricing") if item["id"] == "higgsfield_seedance_video"), None)
        if not price:
            raise RuntimeError("active provider pricing missing: higgsfield_seedance_video")
        cost = round(max(duration_sec, 1) * float(price["usd_per_second"]), 6)
        return Estimate(self.provider, self.model, cost)

    def prepare(self, *, prompt: str, contract: dict, output_dir: Path, meta: dict) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        request = {
            "schema_version": "mcp_request.v1",
            "kind": "seedance_video",
            "project": meta["project"],
            "shot_id": meta["shot_id"],
            "take": meta["take"],
            "contract_sha256": meta["contract_sha256"],
            "prompt_sha256": meta["prompt_sha256"],
            "prompt": prompt,
            "duration_sec": float(contract["duration_sec"]),
            "aspect": meta.get("aspect", "9:16"),
            "references": meta["references"],
            "estimate": {"provider": self.provider, "model": self.model, "cost_usd": meta["estimate_cost"]},
            "gates": "all_pass",
            "created_at": datetime.now(UTC).isoformat(),
            "status": "prepared",
            "mcp_hint": {"tool": "higgsfield", "note": "人間がMCPで実行し、結果を studio record へ"},
        }
        request["execution_token"] = execution_token(request)
        path = output_dir / f"{meta['shot_id']}-{meta['contract_sha256'][:12]}-{meta['take']}.request.json"
        path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def generate(self, **_kwargs):
        raise NotImplementedError("SeedanceProvider only prepares Higgsfield MCP request JSON; it never executes generation.")
