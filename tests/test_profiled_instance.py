import json
import tempfile
import unittest
from pathlib import Path

import yaml

from careerhub.dashboard import build_dashboard_data
from careerhub.instance import load_instance, validate_instance_paths


class ProfiledInstanceTests(unittest.TestCase):
    def test_profiled_instance_loads_base_contract_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "profile").mkdir()
            (root / "config").mkdir()
            (root / "data").mkdir()
            (root / "profile" / "candidate.yaml").write_text(
                yaml.safe_dump({"identity": {"name": "Example"}, "positioning": {"master_headline": "Example"}}),
                encoding="utf-8",
            )
            (root / "config" / "search_profile.yaml").write_text(
                yaml.safe_dump({"lanes": []}), encoding="utf-8"
            )
            (root / "data" / "job_vault.json").write_text(
                json.dumps({"jobs": []}), encoding="utf-8"
            )
            (root / "data" / "applications.json").write_text(
                json.dumps({"cases": [{"status": "applied"}]}), encoding="utf-8"
            )

            cfg = {
                "careerhub": {
                    "instance_id": "example",
                    "engine": {"repository": "Motherpher/CareerHubZero", "version": "0.2.1-alpha"},
                },
                "profile": {"path": "profile/candidate.yaml"},
                "search": {"path": "config/search_profile.yaml"},
                "state": {
                    "job_vault": "data/job_vault.json",
                    "applications": "data/applications.json",
                },
            }
            instance = root / "instance.yaml"
            instance.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

            self.assertEqual(validate_instance_paths(instance), [])
            loaded = load_instance(instance)
            self.assertEqual(loaded["profile"]["identity"]["name"], "Example")
            self.assertEqual(set(loaded), {"instance", "root", "profile", "search", "job_vault", "applications"})
            dashboard = build_dashboard_data(instance)
            self.assertEqual(dashboard["applications"], 1)
            self.assertEqual(dashboard["status_counts"]["applied"], 1)


if __name__ == "__main__":
    unittest.main()
