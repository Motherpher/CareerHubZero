import tempfile
import unittest
from pathlib import Path

from careerhub.hrdm_trace import create_reverse_trace, finalize_reverse_trace, validate_process_id
from careerhub.hybridianesque import finalize_hyfilter


class HRDMCoreTests(unittest.TestCase):
    def test_full_reverse_trace_final_pid(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = create_reverse_trace(counter_path=Path(tmp)/"seq.json", hy_filter_usage=False)
            self.assertEqual(trace["final_output_state"], "OPEN")
            self.assertTrue(validate_process_id(trace["process_id"]))
            self.assertEqual(len(trace["step_process_ids"]), 9)
            final = finalize_reverse_trace(trace, success=True)
            self.assertEqual(final["final_output_state"], "FINAL")
            self.assertTrue(final["process_id"].endswith("-FINAL"))
            self.assertTrue(final["bank_eligible_outputs"])

    def test_hybridianesque_auto_activation(self):
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
        automatic = finalize_hyfilter(value, None)
        self.assertEqual(automatic["status"], "active")
        self.assertTrue(automatic["activated"])
        self.assertEqual(automatic["activation_mode"], "automatic")
        self.assertEqual(automatic["confidence"], "high")
        self.assertEqual(automatic["participating_logics"], ["A", "B"])

    def test_hybridianesque_does_not_activate_without_evidence_threshold(self):
        value = {
            "recommended": True,
            "criteria": {
                "plural_logics":{"met":True,"evidence":["a"]},
                "structural_asymmetry":{"met":True,"evidence":[]},
                "constitutive_translation":{"met":True,"evidence":[]},
                "materialized_output":{"met":False,"evidence":[]},
            },
            "participating_logics":["A","B"],
        }
        automatic = finalize_hyfilter(value, "Auto")
        self.assertEqual(automatic["status"], "not_recommended")
        self.assertFalse(automatic["activated"])
        self.assertEqual(automatic["participating_logics"], [])


if __name__ == "__main__":
    unittest.main()
