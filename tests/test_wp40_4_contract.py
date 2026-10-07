from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class WP404ContractTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_help_workspace_is_searchable_and_covers_core_user_questions(self) -> None:
        page = self.text("web-shell/site/app/help/page.tsx")
        client = self.text("web-shell/site/app/help/HelpClient.tsx")
        self.assertIn("HelpClient", page)
        self.assertIn('current="help"', page)
        for token in (
            "Search help", "Sök i hjälp", "Search Profile", "NEW", "SEEN", "CHANGED",
            "0 new jobs", "ACTIVE", "2–5 minutes", "Recent analyses", "profile-scoped",
            "source warning", "background", "stable result page",
        ):
            self.assertIn(token, client)

    def test_help_uses_product_language_not_internal_execution_commands(self) -> None:
        client = self.text("web-shell/site/app/help/HelpClient.tsx")
        self.assertNotIn("HRDM-R", client)
        self.assertNotIn("Hybridianesque", client)
        self.assertNotIn("Motor", client)

    def test_contextual_help_is_available_from_shared_workspace_header(self) -> None:
        header = self.text("web-shell/site/app/_components/WorkspaceHeader.tsx")
        for token in ("helpAnchors", "profile", "search", "analyse", "apply", "track", "library", "/help#"):
            self.assertIn(token, header)
        self.assertIn("Hjälp", header)
        self.assertIn("Help", header)

    def test_home_has_top_level_help_entry(self) -> None:
        home = self.text("web-shell/site/app/page.tsx")
        self.assertIn('href="/help"', home)
        self.assertIn("Open Help and common questions", home)

    def test_fleet_registry_has_exact_three_active_profile_bindings(self) -> None:
        registry = yaml.safe_load((ROOT / "stack/registry.yaml").read_text(encoding="utf-8"))
        profiles = {item["profile_id"]: item for item in registry["profiles"]}
        self.assertEqual(set(profiles), {"linus-fast", "weronika-perez-borjas", "grace"})
        expected = {
            "linus-fast": "motherpher/careerhub-linusf",
            "weronika-perez-borjas": "motherpher/wpb",
            "grace": "motherpher/gracey",
        }
        for profile_id, repository in expected.items():
            self.assertEqual(profiles[profile_id]["repository"].lower(), repository)
            self.assertEqual(profiles[profile_id]["status"], "active")
            self.assertFalse(profiles[profile_id]["migration"]["legacy_motor_present"])

    def test_managed_shell_distribution_includes_help_route(self) -> None:
        sync = self.text("scripts/sync_web_shell.py")
        managed = self.text("web-shell/site/.careerhub-managed.json")
        self.assertIn('"app"', managed)
        self.assertIn("shutil.copytree(src, dst)", sync)
        self.assertTrue((ROOT / "web-shell/site/app/help/page.tsx").exists())
        self.assertTrue((ROOT / "web-shell/site/app/help/HelpClient.tsx").exists())

    def test_production_profile_binding_remains_fail_closed(self) -> None:
        context = self.text("web-shell/site/lib/profile-context.ts")
        self.assertIn("CareerHub production profile is missing its repository binding", context)
        self.assertIn("CareerHub profile/repository mismatch", context)
        self.assertIn("VERCEL_GIT_REPO_OWNER", context)
        self.assertIn("VERCEL_GIT_REPO_SLUG", context)


if __name__ == "__main__":
    unittest.main()
