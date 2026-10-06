import json
import tempfile
import unittest
from pathlib import Path

from careerhub.hrdm import _strictify_openai_schema
from careerhub.hrdm_trace import create_reverse_trace, finalize_reverse_trace, validate_process_id
from careerhub.hybridianesque import finalize_hyfilter


ROOT = Path(__file__).resolve().parents[1]


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

    def test_openai_schema_adapter_closes_every_object(self):
        canonical = json.loads((ROOT / "core/hrdm/hrdm_result.schema.json").read_text(encoding="utf-8"))
        strict = _strictify_openai_schema(canonical)

        def assert_strict(node, path="$"):
            if isinstance(node, list):
                for index, item in enumerate(node):
                    assert_strict(item, f"{path}[{index}]")
                return
            if not isinstance(node, dict):
                return
            if node.get("type") == "object":
                self.assertIs(node.get("additionalProperties"), False, path)
                properties = node.get("properties")
                self.assertIsInstance(properties, dict, path)
                self.assertEqual(set(node.get("required", [])), set(properties), path)
            for key, value in node.items():
                assert_strict(value, f"{path}.{key}")

        assert_strict(strict)
        self.assertEqual(strict["properties"]["job"]["properties"], {})
        field_logic = strict["properties"]["field_logic"]
        self.assertEqual(field_logic["additionalProperties"], False)
        self.assertIn("dominant_logics", field_logic["properties"])
        self.assertIn("summary", field_logic["properties"])


if __name__ == "__main__":
    unittest.main()
