from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ActionCompletenessTests(unittest.TestCase):
    def assert_file_contains(self, relative: str, *needles: str) -> None:
        path = ROOT / relative
        self.assertTrue(path.exists(), f"Missing required action surface: {relative}")
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            self.assertIn(needle, text, f"{relative} is missing required action marker: {needle}")

    def test_search_is_executable_and_persistable(self):
        self.assert_file_contains(
            "web-shell/site/app/find/SearchRunner.tsx",
            "Run search",
            "Analyse in CareerHub",
        )
        self.assert_file_contains(
            "web-shell/site/app/find/SearchProfileEditor.tsx",
            "Save Search Profile defaults",
            "search_profile_update",
        )
        self.assert_file_contains(
            "web-shell/site/app/api/search/route.ts",
            "Platsbanken",
            "search-sessions",
            "NEW",
            "CHANGED",
        )

    def test_analyse_has_complete_drill_controls(self):
        self.assert_file_contains(
            "web-shell/site/app/analyse/AnalyseClient.tsx",
            "Job URL",
            "Paste job text",
            "Search / application lane",
            "Hybridianesque is evaluated automatically",
            "Run HRDM-R and prepare application",
            "/api/action/status",
        )
        self.assert_file_contains(
            "web-shell/site/app/analyse/HrdmReport.tsx",
            "Hybridianesque relevance statement",
            "Activated automatically",
            "HCC reverse commentary",
        )

    def test_apply_and_track_are_actionable(self):
        self.assert_file_contains(
            "web-shell/site/app/apply/page.tsx",
            "Download application",
            "Update status",
        )
        self.assert_file_contains(
            "web-shell/site/app/track/TrackClient.tsx",
            "Status",
            "Priority",
            "Next action",
            "Update application",
        )

    def test_library_has_governed_upload_sequence(self):
        self.assert_file_contains(
            "web-shell/site/app/library/LibraryClient.tsx",
            "Document class",
            "Initial state",
            "Request evidence review",
            "Reload CareerHub Library",
            "Erase",
        )
        self.assert_file_contains(
            "web-shell/site/app/api/library/route.ts",
            "document_class",
            "initial_state",
        )

    def test_profile_has_review_and_rebuild_controls(self):
        self.assert_file_contains(
            "web-shell/site/app/profile/ProfileActions.tsx",
            "Add or update evidence",
            "Request profile rebuild",
            "Request review",
        )

    def test_motor_action_bridge_is_managed(self):
        self.assert_file_contains(
            "web-shell/site/app/api/action/route.ts",
            "analyse_role",
            "search_profile_update",
            "track_status",
            "profile_review",
            "library_review",
            "executionPreflight",
        )
        self.assert_file_contains(
            "web-shell/site/app/api/action/status/route.ts",
            "WAITING_FOR_EXECUTION",
            "RUNNING",
            "COMPLETED",
            "FAILED",
        )
        self.assert_file_contains(
            "templates/profile-workflows/careerhub-operations.yml",
            "analyse_role",
            "search_profile_update",
            "track_status",
            "profile_review",
            "library_review",
            "Verify HRDM semantic dependency",
        )
        self.assert_file_contains(
            "scripts/sync_web_shell.py",
            "careerhub-operations.yml",
        )


if __name__ == "__main__":
    unittest.main()
