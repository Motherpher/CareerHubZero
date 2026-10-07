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
        self.assert_file_contains("web-shell/site/app/find/SearchRunner.tsx", "Search jobs", "Analyse job", "/api/search/dismiss")
        self.assert_file_contains("web-shell/site/app/find/SearchProfileEditor.tsx", "Save Search Profile defaults", "search_profile_update")
        self.assert_file_contains("web-shell/site/app/api/search/route.ts", "Platsbanken", "search-sessions", "NEW", "CHANGED", "filters")

    def test_analyse_has_complete_drill_controls(self):
        self.assert_file_contains(
            "web-shell/site/app/analyse/AnalyseClient.tsx",
            "Job URL", "Paste job text", "Search / application lane", "Analyse job opening", "Job analysis", "/api/action/status", "2–5 minutes",
        )
        self.assert_file_contains("web-shell/site/app/analyse/HrdmReport.tsx", "Hybridianesque relevance statement", "Activated automatically", "HCC reverse commentary")

    def test_apply_and_track_are_actionable(self):
        self.assert_file_contains("web-shell/site/app/apply/page.tsx", "Download application", "Update status")
        self.assert_file_contains("web-shell/site/app/track/TrackClient.tsx", "Status", "Priority", "Next action", "Update application")

    def test_library_has_governed_upload_sequence(self):
        self.assert_file_contains(
            "web-shell/site/app/library/LibraryClient.tsx",
            "Document class", "After successful indexing", "ACTIVE — allow in Job Analysis", "Rebuild ACTIVE evidence index", "Erase",
        )
        self.assert_file_contains("web-shell/site/app/api/library/route.ts", "document_class", "initial_state", "ingestUpload", "setSourceStatus")
        self.assert_file_contains(
            "web-shell/site/lib/library-evidence.ts",
            "UPLOADED", "INGESTING", "INDEXED", "ACTIVE", "INACTIVE", "INGEST_FAILED", "ERASED", "source_hashes",
        )

    def test_profile_has_review_and_rebuild_controls(self):
        self.assert_file_contains("web-shell/site/app/profile/ProfileActions.tsx", "Add or update evidence", "Request profile rebuild", "Request review")

    def test_motor_action_bridge_is_managed(self):
        self.assert_file_contains(
            "web-shell/site/app/api/action/route.ts",
            "analyse_role", "search_profile_update", "track_status", "profile_review", "library_review", "executionPreflight",
            "@vercel/connect", "github/amber-bell", "subject: { type: 'app' }", "careerhub-semantic.yml", "issueSignedToken",
            "semanticResultPrefix", "central-semantic-motor", "evidence_use_manifest",
        )
        self.assert_file_contains("web-shell/site/package.json", '"@vercel/connect"', '"@vercel/blob"')
        self.assert_file_contains(
            "web-shell/site/app/api/action/status/route.ts",
            "@vercel/connect", "github/amber-bell", "subject: { type: 'app' }", "careerhub-semantic.yml", "materialize_analysis",
            "issueSignedToken", "persisted_hrdm_path", "canonical HRDM result was not persisted", "expected_path",
            "WAITING_FOR_EXECUTION", "RUNNING", "COMPLETED", "FAILED", "authSource",
        )
        self.assert_file_contains(
            ".github/workflows/careerhub-semantic.yml",
            "Verify central semantic dependency", "Execute canonical Job Analysis", "Semantic Job Analysis verified",
            "evidence_use_manifest.json", "Upload result bundle to profile private storage", "canonical_output", "root / 'output' / action_id", "OPENAI_API_KEY",
        )
        self.assert_file_contains(
            "templates/profile-workflows/careerhub-operations.yml",
            "analyse_role", "materialize_analysis", "materialize_semantic_bundle.py", "Mask materialization credential", "GITHUB_EVENT_PATH",
            "stage_if_exists", "git add -f", '"$CAREERHUB_ROOT/output/$ACTION_ID"', "search_profile_update", "track_status", "profile_review", "library_review",
        )
        self.assert_file_contains("scripts/materialize_semantic_bundle.py", "Bundle action mismatch", "Bundle path escapes profile root", "files_written")
        self.assert_file_contains("scripts/sync_web_shell.py", "careerhub-operations.yml")


if __name__ == "__main__":
    unittest.main()
