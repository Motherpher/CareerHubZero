import json
import tempfile
import unittest
from pathlib import Path

from careerhub.models import Job
from careerhub.state import choose_case, bind_analysis, update_case, append_case_event, load_cases


class StateMachineTests(unittest.TestCase):
    def test_one_case_carries_analysis_application_and_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"applications.json"
            job = Job(source="test",title="Role",company="Employer",url="https://example.com/1",lane="core",deadline="2026-12-01")
            choose_case(path, job, 1, "https://github.com/x/issues/1", 4)
            bind_analysis(path, 1, "HRDM-R-20260925-0001-S09-A-R01-FINAL",
                          external_use_allowed=True,
                          report_paths={"pdf":"report.pdf"},
                          application_paths={"docx":"application.docx"})
            update_case(path, 1, "applied")
            append_case_event(path, 1, "interview", source="employer")
            case = load_cases(path)["cases"][0]
            self.assertEqual(case["status"], "applied")
            self.assertTrue(case["external_use_allowed"])
            self.assertEqual(case["hrdm_report_paths"]["pdf"], "report.pdf")
            self.assertIn("application.docx", case["application_paths"]["docx"])
            self.assertTrue(any(x.get("event_type") == "interview" for x in case["history"]))


if __name__ == "__main__":
    unittest.main()
