import json
import tempfile
import unittest
from pathlib import Path

from careerhub.learning import collect_outcome_events, derive_hypotheses, learning_bonus
from careerhub.models import Job
from careerhub.state import choose_case, update_case, append_case_event, load_cases


class LearningLoopTests(unittest.TestCase):
    def test_learning_projects_from_case_history_without_mutating_profile(self):
        data = {
            "cases": [
                {
                    "job_id": "a",
                    "title": "Strategist",
                    "company": "Org",
                    "location": "Stockholm",
                    "lane": "core",
                    "history": [
                        {"at": "2026-01-01", "status": "applied"},
                        {"at": "2026-01-10", "status": "interview_1"},
                        {"at": "2026-01-20", "status": "offer"},
                    ],
                }
            ]
        }
        events = collect_outcome_events(data)
        hypotheses = derive_hypotheses(events)
        role = hypotheses["dimensions"]["role_family"]["strategist"]
        self.assertEqual(role["sample_size"], 3)
        self.assertGreater(role["score"], 0)
        self.assertGreater(role["confidence"], 0)

    def test_learning_bonus_changes_ranking_signal_only(self):
        hypotheses = {
            "dimensions": {
                "role_family": {
                    "strategist": {"score": 0.5, "sample_size": 4, "confidence": 0.44}
                },
                "employer_type": {},
                "geography_key": {},
                "search_lane": {},
            }
        }
        job = Job(source="x", title="Strategist")
        bonus, reasons = learning_bonus(job, hypotheses)
        self.assertGreater(bonus, 0)
        self.assertTrue(any("learning:role_family" in x for x in reasons))

    def test_case_history_is_single_event_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "applications.json"
            job = Job(source="x", title="Analyst", company="Org", url="https://example.org/job")
            choose_case(path, job, 1, "https://example.org/issue/1", 3)
            update_case(path, 1, "applied")
            append_case_event(path, 1, "interview", source="employer", note="Interview booked")
            data = load_cases(path)
            history = data["cases"][0]["history"]
            self.assertTrue(any(x.get("event_type") == "applied" for x in history))
            self.assertTrue(any(x.get("event_type") == "interview" for x in history))

    def test_case_full_outcome_lifecycle_is_one_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "applications.json"
            job = Job(source="x", title="Strategist", company="Org", url="https://example.org/job")
            choose_case(path, job, 7, "https://example.org/issue/7", 4)
            from careerhub.state import bind_analysis
            bind_analysis(
                path,
                7,
                "HRDM-R-20260924-0001-S09-A-R01-FINAL",
                external_use_allowed=True,
                report_paths={"pdf": "reports/r.pdf"},
                application_paths={"docx": "output/a.docx"},
            )
            update_case(path, 7, "applied")
            update_case(path, 7, "interview_1")
            update_case(path, 7, "offer")
            case = load_cases(path)["cases"][0]
            self.assertEqual(case["status"], "offer")
            events = [x.get("event_type") for x in case["history"]]
            self.assertIn("selected_hrdm", events)
            self.assertIn("applied", events)
            self.assertIn("interview", events)
            self.assertIn("offer", events)
            self.assertEqual(case["hrdm_process_id"], "HRDM-R-20260924-0001-S09-A-R01-FINAL")


if __name__ == "__main__":
    unittest.main()
