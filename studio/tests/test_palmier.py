from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from studio.assembly.palmier import prepare_palmier_request, record_palmier_export
from studio.core.approvals import ApprovalLog
from studio.core.jobs import GenerationBlocked
from studio.core.registry import sha256_file


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


class PalmierTests(unittest.TestCase):
    def test_palmier_prepare_requires_take_approval_and_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_json(root / "project.json", {"id": "p"})
            take = root / "take_001.mp4"
            take.write_text("take", encoding="utf-8")
            _write_json(root / "permission.json", {"execute": {"palmier_edit": False}, "budget": {"cap_usd": 20}})
            with self.assertRaisesRegex(GenerationBlocked, "palmier_edit"):
                prepare_palmier_request(root=root, inputs=[take], instruction="edit")
            permission = json.loads((root / "permission.json").read_text(encoding="utf-8"))
            permission["execute"]["palmier_edit"] = True
            _write_json(root / "permission.json", permission)
            with self.assertRaisesRegex(GenerationBlocked, "not approved"):
                prepare_palmier_request(root=root, inputs=[take], instruction="edit")
            ApprovalLog(root / "approvals.jsonl").append(gate="G_take", project="p", target="take_001", target_sha256=sha256_file(take), verdict="approved")
            result = prepare_palmier_request(root=root, inputs=[take], instruction="edit")
            self.assertTrue(Path(result["request_path"]).is_file())

    def test_palmier_record_marks_export_unauthorized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_json(root / "project.json", {"id": "p"})
            _write_json(root / "permission.json", {"execute": {"palmier_edit": True, "palmier_export": False}, "budget": {"cap_usd": 20}})
            take = root / "take_001.mp4"
            take.write_text("take", encoding="utf-8")
            ApprovalLog(root / "approvals.jsonl").append(gate="G_take", project="p", target="take_001", target_sha256=sha256_file(take), verdict="approved")
            prepared = prepare_palmier_request(root=root, inputs=[take], instruction="edit")
            final = root / "final.mp4"
            final.write_text("final", encoding="utf-8")
            record = record_palmier_export(root=root, request_path=Path(prepared["request_path"]), output_path=final)
            self.assertTrue(record["unauthorized"])
            permission = json.loads((root / "permission.json").read_text(encoding="utf-8"))
            permission["execute"]["palmier_export"] = True
            _write_json(root / "permission.json", permission)
            record = record_palmier_export(root=root, request_path=Path(prepared["request_path"]), output_path=final)
            self.assertFalse(record["unauthorized"])


if __name__ == "__main__":
    unittest.main()
