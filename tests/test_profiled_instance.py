import json
import tempfile
import unittest
from pathlib import Path

import yaml

from careerhub.dashboard import build_dashboard_data
from careerhub.instance import InstanceError, load_instance, validate_instance_paths, validate_profile_policy


def valid_profile():
    return {
        "identity": {"name": "Example"},
        "career_sources": [
            {
                "id": "cv-2026",
                "source_type": "cv",
                "reference": "profile/sources/cv-2026.pdf",
                "verification_status": "verified",
            }
        ],
        "evidence": [
            {
                "id": "ev-001",
                "claim": "Verified career capability",
                "status": "verified",
                "source_ids": ["cv-2026"],
            }
        ],
        "positioning": {
            "headline": "Example",
            "functional_core": ["Verified career capability"],
            "derived_from_evidence_ids": ["ev-001"],
        },
        "verification_queue": [],
    }


def valid_search():
    return {
        "version": "2.0",
        "intent": "Find relevant work",
        "geographies": {},
        "lanes": [],
        "triage_rule": "Verified evidence defines fit.",
        "user_search_overlay": {
            "source": "user_input",
            "scope": "search_only",
            "specific_wishes_or_needs": "",
        },
    }


class ProfiledInstanceTests(unittest.TestCase):
    def _write_instance(self, root: Path, profile: dict, search: dict) -> Path:
        (root / "profile").mkdir()
        (root / "config").mkdir()
        (root / "data").mkdir()
        (root / "profile" / "candidate.yaml").write_text(
            yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
        )
        (root / "config" / "search_profile.yaml").write_text(
            yaml.safe_dump(search, sort_keys=False), encoding="utf-8"
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
                "engine": {
                    "repository": "Motherpher/CareerHubZero",
                    "version": "0.2.3-alpha",
                },
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
        return instance

    def test_profiled_instance_loads_verified_career_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            instance = self._write_instance(root, valid_profile(), valid_search())

            self.assertEqual(validate_instance_paths(instance), [])
            loaded = load_instance(instance)
            self.assertEqual(loaded["profile"]["identity"]["name"], "Example")
            self.assertEqual(set(loaded), {"instance", "root", "profile", "search", "job_vault", "applications"})
            dashboard = build_dashboard_data(instance)
            self.assertEqual(dashboard["applications"], 1)
            self.assertEqual(dashboard["status_counts"]["applied"], 1)

    def test_unverified_source_cannot_enter_matchable_profile(self):
        profile = valid_profile()
        profile["career_sources"][0]["verification_status"] = "unverified"
        errors = validate_profile_policy(profile, valid_search())
        self.assertTrue(any("verification_status=verified" in error for error in errors))

    def test_private_life_fields_are_hard_blocked(self):
        profile = valid_profile()
        profile["family"] = {"children": 2}
        errors = validate_profile_policy(profile, valid_search())
        self.assertTrue(any("Forbidden non-career/private-life field" in error for error in errors))

    def test_user_wishes_are_search_only(self):
        search = valid_search()
        search["user_search_overlay"]["specific_wishes_or_needs"] = "Helst nära kollektivtrafik och gärna deltid."
        self.assertEqual(validate_profile_policy(valid_profile(), search), [])

        profile = valid_profile()
        profile["specific_wishes_or_needs"] = "This must not be profile evidence"
        errors = validate_profile_policy(profile, search)
        self.assertTrue(any("specific_wishes_or_needs" in error for error in errors))

    def test_instance_load_fails_on_policy_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = valid_profile()
            profile["health"] = {"note": "must never enter profile"}
            instance = self._write_instance(root, profile, valid_search())
            with self.assertRaises(InstanceError):
                load_instance(instance)


if __name__ == "__main__":
    unittest.main()
