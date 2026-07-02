from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio.core.approvals import ApprovalLog
from studio.core.jobs import GenerationBlocked, record_generation_result, run_generation_from_contract
from studio.core.registry import sha256_file
from studio.memory.seeds import SEED_DIR
from studio.providers.seedance import SeedanceProvider


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _root(tmp: str) -> tuple[Path, Path]:
    root = Path(tmp)
    _write_json(
        root / "project.json",
        {
            "id": "p",
            "type": "short_ad",
            "status": "preproduction",
            "brief": {"product": "p", "target": "t", "platform": ["tiktok"], "duration_sec": 4, "aspect": "9:16", "language": "ja"},
            "budget": {"cap_usd": 20, "daily_cap_usd": 10, "spent_usd": 0, "today_spent_usd": 0, "generations": 0},
            "bible_ref": "bible.json",
            "shots": ["shot_001"],
            "created_at": "now",
            "updated_at": "now",
        },
    )
    _write_json(root / "bible.json", {"project": "Demo", "characters": [], "locations": [], "props": [], "style": {}, "brand": {}})
    _write_json(
        root / "permission.json",
        {
            "execute": {"seedance_generate": True},
            "budget": {"cap_usd": 20, "daily_cap_usd": 10, "max_takes_per_shot": 1, "max_parallel": 1},
        },
    )
    (root / "assets" / "registry.jsonl").parent.mkdir(parents=True, exist_ok=True)
    (root / "assets" / "registry.jsonl").touch()
    (root / "approvals.jsonl").touch()
    contract_path = root / "contract.json"
    _write_json(
        contract_path,
        {
            "shot_id": "shot_001",
            "narrative_function": "show product",
            "duration_sec": 4,
            "camera": "slow dolly",
            "action": "product opens",
            "audio": {},
            "references": [],
            "acceptance_criteria": ["clear product"],
            "state": "approved",
        },
    )
    return root, contract_path


def _active_pricing(tmp: str) -> Path:
    seed_dir = Path(tmp) / "seeds"
    shutil.copytree(SEED_DIR, seed_dir)
    pricing = json.loads((seed_dir / "provider_pricing.json").read_text(encoding="utf-8"))
    pricing["items"][0]["status"] = "active"
    pricing["items"][0]["usd_per_second"] = 0.25
    pricing["items"][0]["verified_at"] = "test"
    (seed_dir / "provider_pricing.json").write_text(json.dumps(pricing), encoding="utf-8")
    return seed_dir


class ProviderPrepareRecordTests(unittest.TestCase):
    def test_candidate_pricing_blocks_estimate(self):
        with self.assertRaises(RuntimeError):
            SeedanceProvider().estimate(prompt="x", duration_sec=4)

    def test_higgsfield_prepare_and_record_flow(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"STUDIO_SEED_DIR": str(_active_pricing(tmp))}):
            root, contract_path = _root(tmp)
            with self.assertRaisesRegex(GenerationBlocked, "絵コンテが承認待ちです"):
                run_generation_from_contract(root=root, contract_path=contract_path, provider=SeedanceProvider())
            self.assertFalse((root / "requests").exists())
            ApprovalLog(root / "approvals.jsonl").append(gate="G_storyboard", project="p", target="shot_001", target_sha256=sha256_file(contract_path), verdict="approved")
            prepared = run_generation_from_contract(root=root, contract_path=contract_path, provider=SeedanceProvider())
            self.assertEqual(prepared["status"], "prepared")
            self.assertTrue(Path(prepared["request_path"]).is_file())
            project = json.loads((root / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(project["budget"]["spent_usd"], 0)
            output = root / "out.mp4"
            output.write_text("video", encoding="utf-8")
            recorded = record_generation_result(root=root, request_path=Path(prepared["request_path"]), output_path=output, cost_usd=1.0)
            self.assertFalse(recorded["unauthorized"])
            project = json.loads((root / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(project["budget"]["spent_usd"], 1.0)
            again = record_generation_result(root=root, request_path=Path(prepared["request_path"]), output_path=output, cost_usd=1.0)
            self.assertTrue(again["idempotent"])
            project = json.loads((root / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(project["budget"]["spent_usd"], 1.0)

    def test_record_rejects_tampered_request_and_records_unauthorized(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"STUDIO_SEED_DIR": str(_active_pricing(tmp))}):
            root, contract_path = _root(tmp)
            ApprovalLog(root / "approvals.jsonl").append(gate="G_storyboard", project="p", target="shot_001", target_sha256=sha256_file(contract_path), verdict="approved")
            prepared = run_generation_from_contract(root=root, contract_path=contract_path, provider=SeedanceProvider())
            request_path = Path(prepared["request_path"])
            request = json.loads(request_path.read_text(encoding="utf-8"))
            request["prompt"] += " tampered"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            output = root / "out.mp4"
            output.write_text("video", encoding="utf-8")
            with self.assertRaisesRegex(GenerationBlocked, "request改竄"):
                record_generation_result(root=root, request_path=request_path, output_path=output)
            root, contract_path = _root(str(Path(tmp) / "second"))
            ApprovalLog(root / "approvals.jsonl").append(gate="G_storyboard", project="p", target="shot_001", target_sha256=sha256_file(contract_path), verdict="approved")
            prepared = run_generation_from_contract(root=root, contract_path=contract_path, provider=SeedanceProvider())
            permission = json.loads((root / "permission.json").read_text(encoding="utf-8"))
            permission["execute"]["seedance_generate"] = False
            _write_json(root / "permission.json", permission)
            output = root / "out.mp4"
            output.write_text("video", encoding="utf-8")
            recorded = record_generation_result(root=root, request_path=Path(prepared["request_path"]), output_path=output)
            self.assertTrue(recorded["unauthorized"])


if __name__ == "__main__":
    unittest.main()
