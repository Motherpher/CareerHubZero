from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from careerhub.state_integrity import (
    ResetClass,
    apply_reset_plan,
    build_reset_plan,
    classify_hrdm_run,
    classify_transient_state,
)


class StateIntegrityTests(unittest.TestCase):
    def test_known_wp39_signature_is_synthetic(self) -> None:
        decision = classify_hrdm_run({
            "run_id": "test-run",
            "title": "WP39 End-to-End Test Role",
            "company": "CareerHub Test Harness",
            "job_url": "https://careerhub.local/wp39-e2e-test-6",
            "paths": {"json": "reports/hrdm/active/job/pid/HRDM_result.json"},
        })
        self.assertEqual(decision.reset_class, ResetClass.SYNTHETIC_DELETE)

    def test_single_test_marker_requires_review(self) -> None:
        decision = classify_hrdm_run({"run_id": "maybe", "title": "WP39 Test Role", "company": "Real Employer"})
        self.assertEqual(decision.reset_class, ResetClass.ORPHAN_REVIEW)

    def test_genuine_analysis_is_preserved(self) -> None:
        decision = classify_hrdm_run({
            "run_id": "real-1",
            "title": "Strategic Development Lead",
            "company": "Example Municipality",
            "job_url": "https://example.org/jobs/42",
        })
        self.assertEqual(decision.reset_class, ResetClass.PRESERVE)

    def test_transient_classifier_is_conservative(self) -> None:
        self.assertEqual(classify_transient_state("a", "QUEUED").reset_class, ResetClass.TRANSIENT_CLEAR)
        self.assertEqual(classify_transient_state("b", "RUNNING").reset_class, ResetClass.PRESERVE)
        self.assertEqual(classify_transient_state("c", "mystery").reset_class, ResetClass.UNKNOWN_BLOCK)

    def test_apply_deletes_only_strong_synthetic_run_and_linked_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_manifest(root)
            synthetic_dir = root / "reports/hrdm/active/test-job/test-pid"
            genuine_dir = root / "reports/hrdm/active/real-job/real-pid"
            synthetic_dir.mkdir(parents=True)
            genuine_dir.mkdir(parents=True)
            for name in ("HRDM_result.json", "HRDM_report.md"):
                (synthetic_dir / name).write_text("synthetic", encoding="utf-8")
            (genuine_dir / "HRDM_result.json").write_text("real", encoding="utf-8")

            ledger = {
                "schema_version": "1.0",
                "runs": [
                    {
                        "run_id": "synthetic",
                        "title": "WP39 End-to-End Test Role",
                        "company": "CareerHub Test Harness",
                        "job_url": "https://careerhub.local/wp39-e2e-test-6",
                        "paths": {
                            "json": "reports/hrdm/active/test-job/test-pid/HRDM_result.json",
                            "markdown": "reports/hrdm/active/test-job/test-pid/HRDM_report.md",
                        },
                    },
                    {
                        "run_id": "real",
                        "title": "Strategic Development Lead",
                        "company": "Example Municipality",
                        "job_url": "https://example.org/jobs/42",
                        "paths": {"json": "reports/hrdm/active/real-job/real-pid/HRDM_result.json"},
                    },
                ],
            }
            ledger_path = root / "data/hrdm_ledger.json"
            ledger_path.parent.mkdir(parents=True)
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")

            plan = build_reset_plan(root)
            self.assertFalse(plan.blocked)
            result = apply_reset_plan(root, plan)
            self.assertEqual(result["removed_runs"], 1)
            self.assertEqual(result["preserved_runs"], 1)
            self.assertFalse((synthetic_dir / "HRDM_result.json").exists())
            self.assertTrue((genuine_dir / "HRDM_result.json").exists())
            saved = json.loads(ledger_path.read_text(encoding="utf-8"))
            self.assertEqual([run["run_id"] for run in saved["runs"]], ["real"])

    def test_unsafe_linked_path_blocks_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_manifest(root)
            ledger_path = root / "data/hrdm_ledger.json"
            ledger_path.parent.mkdir(parents=True)
            ledger_path.write_text(json.dumps({
                "schema_version": "1.0",
                "runs": [{
                    "run_id": "synthetic",
                    "title": "WP39 End-to-End Test Role",
                    "company": "CareerHub Test Harness",
                    "job_url": "https://careerhub.local/test",
                    "paths": {"json": "profile/candidate_verified.yaml"},
                }],
            }), encoding="utf-8")
            plan = build_reset_plan(root)
            self.assertTrue(plan.blocked)
            with self.assertRaises(RuntimeError):
                apply_reset_plan(root, plan)

    def test_unreferenced_result_is_review_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_manifest(root)
            ledger_path = root / "data/hrdm_ledger.json"
            ledger_path.parent.mkdir(parents=True)
            ledger_path.write_text('{"schema_version":"1.0","runs":[]}', encoding="utf-8")
            orphan = root / "reports/hrdm/active/orphan/pid/HRDM_result.json"
            orphan.parent.mkdir(parents=True)
            orphan.write_text("{}", encoding="utf-8")
            plan = build_reset_plan(root)
            review = [d for d in plan.decisions if d.reset_class is ResetClass.ORPHAN_REVIEW]
            self.assertEqual(len(review), 1)
            self.assertTrue(orphan.exists())

    @staticmethod
    def _write_manifest(root: Path) -> None:
        (root / "careerhub.yaml").write_text(
            """schema_version: '1.0'
profile_id: test-profile
state:
  hrdm_ledger: data/hrdm_ledger.json
artifacts:
  hrdm_reports: reports/hrdm/active
  hrdm_history: reports/hrdm/history
""",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
