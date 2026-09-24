import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

from careerhub.hrdm_reports import archive_expired_reports, render_report_indexes, save_report_bundle, write_ledger
from careerhub.hrdm_trace import create_reverse_trace, finalize_reverse_trace, validate_process_id
from careerhub.hybridianesque import finalize_hyfilter
from careerhub.instance import load_profile_node, validate_profile_node_paths
from careerhub.search_contract import normalize_search


def valid_profile():
    return {
        "identity": {"name": "Example"},
        "career_sources": [
            {
                "id": "cv",
                "source_type": "cv",
                "reference": "cv.pdf",
                "verification_status": "verified",
            }
        ],
        "evidence": [
            {
                "id": "ev-1",
                "claim": "Verified capability",
                "status": "verified",
                "source_ids": ["cv"],
            }
        ],
        "positioning": {
            "headline": "Example",
            "functional_core": ["Verified capability"],
            "derived_from_evidence_ids": ["ev-1"],
        },
        "verification_queue": [],
    }


class UnifiedBodyTests(unittest.TestCase):
    def _node(self, root: Path) -> Path:
        (root / "profile").mkdir()
        (root / "config").mkdir()
        (root / "data").mkdir()
        (root / "profile/candidate.yaml").write_text(yaml.safe_dump(valid_profile()), encoding="utf-8")
        search = {
            "version": "2.1",
            "intent": "Find work",
            "geographies": {
                "country": "SE",
                "anchors": ["Stockholm"],
                "remote_allowed": True,
                "remote_scopes": ["SE"],
                "progressive_widening": ["anchor", "country", "remote"],
            },
            "lanes": [
                {"lane_id": "L1", "name": "Strategy", "bucket": "core", "priority": 1, "queries": ["strateg"]},
                {"lane_id": "L2", "name": "Analysis", "bucket": "adjacent", "priority": 2, "queries": ["analyst"]},
            ],
            "negative_filters": [],
            "triage_rule": "Verified evidence defines fit.",
            "user_search_overlay": {
                "source": "user_input",
                "scope": "search_only",
                "specific_wishes_or_needs": "",
            },
        }
        (root / "config/search_profile.yaml").write_text(yaml.safe_dump(search), encoding="utf-8")
        (root / "data/job_vault.json").write_text(json.dumps({"jobs": []}), encoding="utf-8")
        (root / "data/applications.json").write_text(json.dumps({"cases": []}), encoding="utf-8")
        manifest = {
            "schema_version": "1.0",
            "profile_id": "example",
            "profile": {"path": "profile/candidate.yaml"},
            "search": {"path": "config/search_profile.yaml"},
            "state": {
                "job_vault": "data/job_vault.json",
                "applications": "data/applications.json",
                "hrdm_ledger": "data/hrdm_ledger.json",
            },
            "artifacts": {
                "hrdm_reports": "reports/hrdm/active",
                "hrdm_history": "reports/hrdm/history",
            },
            "ui": {"language": "sv"},
        }
        path = root / "careerhub.yaml"
        path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        return path

    def test_versionless_manifest_loads_and_creates_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._node(root)
            self.assertEqual(validate_profile_node_paths(manifest), [])
            loaded = load_profile_node(manifest)
            self.assertEqual(loaded["manifest"]["profile_id"], "example")
            self.assertTrue((root / "data/hrdm_ledger.json").exists())
            self.assertNotIn("engine", loaded["manifest"])
            self.assertNotIn("version", loaded["manifest"])

    def test_search_shapes_normalize_to_runtime_lanes(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._node(Path(tmp))
            loaded = load_profile_node(manifest)
            runtime = normalize_search(loaded["search"])
            self.assertEqual(runtime["location"], "Stockholm")
            self.assertEqual(runtime["country"], "SE")
            self.assertEqual(runtime["lanes"][0]["bucket"], "core")
            self.assertEqual(runtime["lanes"][0]["queries"], ["strateg"])
            self.assertEqual(runtime["lanes"][1]["bucket"], "adjacent")

    def test_hrdm_trace_uses_canonical_process_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = create_reverse_trace(
                counter_path=Path(tmp) / "runseq.json",
                hy_filter_usage=False,
            )
            self.assertTrue(trace["process_id_validation_status"])
            self.assertTrue(validate_process_id(trace["process_id"]))
            self.assertTrue(trace["process_id"].endswith("-S09-A-R01-OPEN"))
            self.assertEqual(trace["final_output_state"], "OPEN")
            self.assertEqual(len(trace["step_process_ids"]), 9)
            final = finalize_reverse_trace(trace, success=True)
            self.assertTrue(final["process_id"].endswith("-S09-A-R01-FINAL"))
            self.assertEqual(final["final_output_state"], "FINAL")
            incomplete = finalize_reverse_trace(trace, success=False, warnings=["analysis unavailable"])
            self.assertTrue(incomplete["process_id"].endswith("-S09-A-R01-WARN"))
            self.assertEqual(incomplete["bank_eligible_outputs"], [])

    def test_hybridianesque_requires_explicit_yes_for_deep_filter(self):
        candidate = {
            "recommended": True,
            "why": "All four criteria are present.",
            "criteria": {
                "plural_logics": {"met": True, "evidence": ["A/B"]},
                "structural_asymmetry": {"met": True, "evidence": ["authority"]},
                "constitutive_translation": {"met": True, "evidence": ["translation"]},
                "materialized_output": {"met": True, "evidence": ["protocol"]},
            },
            "participating_logics": ["institution", "community"],
            "asymmetries": ["decision power"],
            "translation_relations": ["community to institution"],
            "process_to_output": ["dialogue to protocol"],
            "overload_or_misframing": [],
            "failure_modes": [],
            "risk_remaining": [],
            "framing_if_active": "A bounded mediation function.",
        }
        awaiting = finalize_hyfilter(candidate, None)
        self.assertEqual(awaiting["status"], "awaiting_user_decision")
        self.assertEqual(awaiting["participating_logics"], [])

        active = finalize_hyfilter(candidate, "Yes")
        self.assertEqual(active["status"], "active")
        self.assertEqual(active["participating_logics"], ["institution", "community"])

    def test_expired_report_moves_off_active_shelf_but_stays_in_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / "reports/hrdm/active/job/pid"
            active.mkdir(parents=True)
            report = active / "HRDM_report.md"
            report.write_text("historic report", encoding="utf-8")
            ledger_path = root / "data/hrdm_ledger.json"
            ledger = {
                "schema_version": "1.0",
                "runs": [{
                    "run_id": "run-1",
                    "process_id": "HRDM-R-20260101-0001-S09-A-R01-FINAL",
                    "job_id": "job",
                    "title": "Role",
                    "company": "Employer",
                    "deadline": "2026-01-01",
                    "created_at": "2025-12-01T00:00:00+00:00",
                    "status": "active",
                    "hy_filter": {"status": "not_recommended"},
                    "paths": {"markdown": "reports/hrdm/active/job/pid/HRDM_report.md"},
                }],
            }
            write_ledger(ledger_path, ledger)
            moved = archive_expired_reports(
                root,
                ledger_path,
                now=datetime(2026, 9, 24, tzinfo=timezone.utc),
            )
            self.assertEqual(moved, 1)
            data = json.loads(ledger_path.read_text(encoding="utf-8"))
            self.assertEqual(data["runs"][0]["status"], "archived")
            self.assertEqual(data["runs"][0]["archive_reason"], "deadline_passed")
            self.assertFalse(report.exists())
            self.assertTrue((root / data["runs"][0]["paths"]["markdown"]).exists())
            active_index, history_index = render_report_indexes(root, ledger_path)
            self.assertIn("0 aktiva rapporter", active_index.read_text(encoding="utf-8"))
            self.assertIn("Role", history_index.read_text(encoding="utf-8"))

    def test_hrdm_bank_only_final_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "data/hrdm_ledger.json"
            base_trace = create_reverse_trace(
                counter_path=root / "data/runseq.json",
                hy_filter_usage=False,
            )
            incomplete_trace = finalize_reverse_trace(
                base_trace,
                success=False,
                warnings=["semantic execution unavailable"],
            )
            incomplete = {
                "process_id": incomplete_trace["process_id"],
                "job": {"id": "job-a", "title": "Role", "company": "Org", "deadline": "2026-10-01"},
                "signals": [], "concept_clusters": [],
                "hidden_need": {"statement": "", "confidence": "low", "rationale": []},
                "field_logic": {}, "function_core": {"chain": "", "summary": ""},
                "dod": {"alpha": "", "zenith": "", "dimensions": {}, "average": 0, "classification": "Low"},
                "assessment_zones": [],
                "candidate_positioning": {},
                "hybridianesque": {"recommended": False, "status": "not_recommended", "user_decision": None},
                "hcc": {"risks": [], "commentary": ""},
                "application_strategy": {},
                "trace": incomplete_trace,
            }
            entry = save_report_bundle(root, incomplete, ledger)
            self.assertEqual(entry["status"], "incomplete")
            self.assertFalse(entry["bankable"])
            self.assertNotIn("docx", entry["paths"])
            self.assertNotIn("pdf", entry["paths"])

            success_trace = finalize_reverse_trace(
                create_reverse_trace(counter_path=root / "data/runseq.json", hy_filter_usage=False),
                success=True,
            )
            final = dict(incomplete)
            final["process_id"] = success_trace["process_id"]
            final["trace"] = success_trace
            final["job"] = {"id": "job-b", "title": "Role B", "company": "Org", "deadline": "2026-10-01"}
            final_entry = save_report_bundle(root, final, ledger)
            self.assertEqual(final_entry["status"], "active")
            self.assertTrue(final_entry["bankable"])
            self.assertTrue((root / final_entry["paths"]["docx"]).exists())
            self.assertTrue((root / final_entry["paths"]["pdf"]).exists())


if __name__ == "__main__":
    unittest.main()
