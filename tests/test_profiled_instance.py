import json
import tempfile
import unittest
from pathlib import Path

import yaml

from careerhub.analytics import market_response
from careerhub.instance import load_instance, validate_instance_paths


class MarketResponseTests(unittest.TestCase):
    def test_market_response_counts(self):
        events = [
            {"stage": "qualified_contact", "surface_id": "s1", "lane_id": "l1", "direction": "inbound"},
            {"stage": "interview_1", "surface_id": "s1", "lane_id": "l1", "direction": "outbound"},
            {"stage": "offer", "surface_id": "s2", "lane_id": "l2", "direction": "outbound"},
        ]
        result = market_response(events)
        self.assertEqual(result["event_count"], 3)
        self.assertEqual(result["qualified_response_count"], 3)
        self.assertEqual(result["interview_count"], 1)
        self.assertEqual(result["offer_count"], 1)
        self.assertEqual(result["inbound_count"], 1)
        self.assertEqual(result["outbound_count"], 2)

    def test_profiled_instance_loads_extended_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "profile").mkdir()
            (root / "config").mkdir()
            (root / "data").mkdir()
            (root / "profile" / "candidate.yaml").write_text(
                yaml.safe_dump({"identity": {"name": "Example"}, "positioning": {"master_headline": ""}}),
                encoding="utf-8",
            )
            (root / "profile" / "evidence_index.yaml").write_text(
                yaml.safe_dump({"sources": []}), encoding="utf-8"
            )
            (root / "config" / "search_profile.yaml").write_text(
                yaml.safe_dump({"lanes": []}), encoding="utf-8"
            )
            for name, payload in {
                "job_vault.json": {"jobs": []},
                "applications.json": {"applications": []},
                "response_ledger.json": {"events": []},
                "experiments.json": {"experiments": []},
            }.items():
                (root / "data" / name).write_text(json.dumps(payload), encoding="utf-8")

            cfg = {
                "careerhub": {
                    "instance_id": "example",
                    "engine": {"repository": "Motherpher/CareerHubZero", "version": "0.2.0-alpha"},
                },
                "profile": {
                    "path": "profile/candidate.yaml",
                    "evidence_index": "profile/evidence_index.yaml",
                },
                "search": {"path": "config/search_profile.yaml"},
                "state": {
                    "job_vault": "data/job_vault.json",
                    "applications": "data/applications.json",
                    "response_ledger": "data/response_ledger.json",
                    "experiments": "data/experiments.json",
                },
            }
            instance = root / "instance.yaml"
            instance.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

            self.assertEqual(validate_instance_paths(instance), [])
            loaded = load_instance(instance)
            self.assertEqual(loaded["profile"]["identity"]["name"], "Example")
            self.assertIn("response_ledger", loaded)
            self.assertIn("experiments", loaded)
            self.assertIn("evidence_index", loaded)


if __name__ == "__main__":
    unittest.main()
