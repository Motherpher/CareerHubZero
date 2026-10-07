from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WP403ContractTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_search_workspace_has_required_filter_contract(self) -> None:
        text = self.text("web-shell/site/lib/search-workspace.ts")
        for token in (
            "permanent", "temporary", "fulltime", "parttime", "consulting",
            "onsite", "hybrid", "remote",
            "publishedPresetDays", "7, 30, 60, 90", "180",
            "search-state/", "dismissed.json",
        ):
            self.assertIn(token, text)

    def test_search_api_uses_profile_context_and_preserves_source_failure_semantics(self) -> None:
        text = self.text("web-shell/site/app/api/search/route.ts")
        self.assertIn("resolveRuntimeProfileContext", text)
        self.assertIn("application_deadline", text)
        self.assertIn("sourceHealth: 'FAILED'", text)
        self.assertIn("No result delta was recorded", text)
        self.assertIn("dismissedResults", text)
        self.assertIn("comparisonKey", text)
        self.assertIn("filters", text)

    def test_dismissal_api_is_profile_scoped_and_reversible(self) -> None:
        text = self.text("web-shell/site/app/api/search/dismiss/route.ts")
        self.assertIn("resolveRuntimeProfileContext", text)
        self.assertIn("dismissalStatePath(profileId)", text)
        self.assertIn("readState(context.profileId)", text)
        self.assertIn("export async function POST", text)
        self.assertIn("export async function DELETE", text)
        self.assertIn("restored: true", text)

    def test_search_ui_contains_practical_filters_and_restore_path(self) -> None:
        text = self.text("web-shell/site/app/find/SearchRunner.tsx")
        for token in (
            "jobTypes", "workModes", "publishedPresetDays", 'type="date"',
            "Last week", "Last month", "2 months", "3 months",
            "dismiss(result)", "restore(result)", "Show", "dismissed",
            "checked", "match filters", "Analyse job",
        ):
            self.assertIn(token, text)

    def test_search_to_analyse_uses_existing_durable_route(self) -> None:
        text = self.text("web-shell/site/app/find/SearchRunner.tsx")
        self.assertIn("function analyseHref", text)
        self.assertIn("return `/analyse?${params.toString()}`", text)
        self.assertIn("job_url", text)

    def test_run_filters_do_not_write_search_profile(self) -> None:
        runner = self.text("web-shell/site/app/find/SearchRunner.tsx")
        route = self.text("web-shell/site/app/api/search/route.ts")
        self.assertNotIn("search_profile_update", runner)
        self.assertNotIn("search_profile_update", route)
        self.assertIn("loadSearchProfile", route)

    def test_search_session_schema_matches_runtime_version(self) -> None:
        schema = self.text("schemas/search_session.schema.json")
        self.assertIn('"const": "1.1"', schema)
        self.assertIn('"comparison_key"', schema)
        self.assertIn('"filters"', schema)
        self.assertIn('"source_health"', schema)


if __name__ == "__main__":
    unittest.main()
