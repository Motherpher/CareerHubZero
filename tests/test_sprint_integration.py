import json
import tempfile
import unittest
from pathlib import Path

from careerhub.country_adapters import SwedenAdapter, get_country_adapter
from careerhub.hub import render_applications, render_control_room, render_job_vault
from careerhub.state import bind_analysis, choose_case, load_cases
from careerhub.models import Job


class SprintIntegrationTests(unittest.TestCase):
    def test_sweden_adapter_is_country_enrichment_not_second_geo_truth(self):
        adapter = get_country_adapter("SE")
        self.assertIsInstance(adapter, SwedenAdapter)
        geo = {
            "hierarchy": {
                "country_code": "SE",
                "admin1": "Stockholms län",
                "locality": "Stockholm",
            },
            "point": {},
        }
        enriched = adapter.enrich(geo)
        self.assertEqual(enriched["adapter"], "scb")
        self.assertEqual(enriched["county_code"], "01")
        self.assertEqual(enriched["municipality_name"], "Stockholm")
        self.assertFalse(enriched["completeness"]["municipality"])

    def test_case_binds_one_hrdm_and_application_artifact_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "applications.json"
            job = Job(source="x", title="Strategist", company="Org", url="https://example.org/job")
            choose_case(path, job, 4, "https://example.org/issues/4", 4)
            case = bind_analysis(
                path,
                4,
                "HRDM-R-20260924-0001-S09-A-R01-FINAL",
                external_use_allowed=True,
                report_paths={"pdf": "reports/a.pdf"},
                application_paths={"docx": "output/a.docx"},
            )
            self.assertEqual(case["status"], "ready")
            self.assertEqual(case["hrdm_process_id"], "HRDM-R-20260924-0001-S09-A-R01-FINAL")
            self.assertTrue(case["external_use_allowed"])
            self.assertEqual(load_cases(path)["cases"][0]["application_paths"]["docx"], "output/a.docx")

    def test_one_hub_surface_derives_from_canonical_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = {
                "total_jobs_ever_seen": 1,
                "jobs": [{
                    "id": "a",
                    "title": "Strategist",
                    "company": "Org",
                    "location": "Stockholm",
                    "triage_score": 82,
                    "deadline": "2026-10-01",
                    "in_latest_scan": True,
                    "first_seen": "2026-09-24",
                    "last_seen": "2026-09-24",
                    "triage_reasons": ["title/role fit 90%"],
                }],
            }
            cases = {"cases": []}
            ledger = {"runs": []}
            render_job_vault(root / "JOB_VAULT.md", vault)
            render_applications(root / "APPLICATIONS.md", cases)
            render_control_room(
                root / "CONTROL_ROOM.md",
                profile_name="Example",
                language="en",
                vault=vault,
                cases=cases,
                hrdm_ledger=ledger,
            )
            text = (root / "CONTROL_ROOM.md").read_text(encoding="utf-8")
            self.assertIn("Find jobs → Analyse? → Apply", text)
            self.assertIn("Strategist", text)
            self.assertIn("Career learning", text)


if __name__ == "__main__":
    unittest.main()
