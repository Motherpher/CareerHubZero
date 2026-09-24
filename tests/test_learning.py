import copy
import unittest

from careerhub.learning import derive_learning_signals, apply_learning_to_jobs


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.cases = {
            "cases": [
                {
                    "job_id": "a",
                    "lane": "core",
                    "location": "Stockholm",
                    "history": [
                        {"at": "2026-01-01", "event_type": "selected_hrdm", "source": "user"},
                        {"at": "2026-01-02", "event_type": "applied", "source": "user"},
                        {"at": "2026-01-10", "event_type": "interview", "source": "employer"},
                    ],
                },
                {
                    "job_id": "b",
                    "lane": "bridge",
                    "location": "Uppsala",
                    "history": [
                        {"at": "2026-01-01", "event_type": "user_rejected", "source": "user"},
                    ],
                },
            ]
        }

    def test_learning_is_search_hypotheses_only(self):
        original = copy.deepcopy(self.cases)
        result = derive_learning_signals(self.cases)
        self.assertFalse(result["policy"]["candidate_evidence_mutation"])
        self.assertEqual(self.cases, original)

    def test_positive_outcomes_raise_related_jobs(self):
        learning = derive_learning_signals(self.cases)
        jobs = [
            {"id": "1", "lane": "core", "location": "Stockholm", "triage_score": 60},
            {"id": "2", "lane": "bridge", "location": "Uppsala", "triage_score": 60},
        ]
        ranked = apply_learning_to_jobs(jobs, learning)
        self.assertEqual(ranked[0]["id"], "1")
        self.assertGreater(ranked[0]["triage_score"], ranked[0]["base_triage_score"])

    def test_adjustment_is_bounded(self):
        learning = {
            "signals": [{"dimension": "role_family", "key": "core", "score": 99, "observations": 100, "confidence": 1}]
        }
        row = apply_learning_to_jobs([{"id":"1","lane":"core","triage_score":50}], learning)[0]
        self.assertEqual(row["learning_adjustment"], 10.0)


if __name__ == "__main__":
    unittest.main()
