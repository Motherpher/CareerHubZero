import tempfile
import unittest
from pathlib import Path

from careerhub.hrdm_trace import create_reverse_trace, validate_process_id
from careerhub.hybridianesque import finalize_hyfilter


class HRDMCoreTests(unittest.TestCase):
    def test_full_reverse_trace_final_pid(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = create_reverse_trace(counter_path=Path(tmp)/"seq.json", hy_filter_usage=False)
            self.assertEqual(trace["final_output_state"], "FINAL")
            self.assertTrue(validate_process_id(trace["process_id"]))
            self.assertEqual(len(trace["step_process_ids"]), 9)

    def test_hybridianesque_enclosure(self):
        value = {
            "recommended": True,
            "why": "Four criteria met",
            "criteria": {
                "plural_logics":{"met":True,"evidence":["a"]},
                "structural_asymmetry":{"met":True,"evidence":["b"]},
                "constitutive_translation":{"met":True,"evidence":["c"]},
                "materialized_output":{"met":True,"evidence":["d"]},
            },
            "participating_logics":["A","B"],
        }
        waiting = finalize_hyfilter(value, None)
        self.assertEqual(waiting["status"], "awaiting_user_decision")
        self.assertEqual(waiting["participating_logics"], [])
        active = finalize_hyfilter(value, "Yes")
        self.assertEqual(active["status"], "active")


if __name__ == "__main__":
    unittest.main()
