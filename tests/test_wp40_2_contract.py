from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WP402ContractTests(unittest.TestCase):
    def test_library_schema_uses_governed_lifecycle(self) -> None:
        schema = json.loads((ROOT / "schemas/source_library.schema.json").read_text(encoding="utf-8"))
        status = schema["properties"]["sources"]["items"]["properties"]["status"]
        values = set(status["enum"])
        self.assertTrue({"UPLOADED", "INGESTING", "INDEXED", "ACTIVE", "INACTIVE", "INGEST_FAILED", "ERASED"}.issubset(values))

    def test_analysis_completion_requires_repository_persistence(self) -> None:
        text = (ROOT / "web-shell/site/app/api/action/status/route.ts").read_text(encoding="utf-8")
        self.assertIn("persisted_hrdm_path", text)
        self.assertIn("Profile materialization workflow succeeded, but the canonical HRDM result was not persisted", text)
        self.assertIn("state: 'COMPLETED'", text)

    def test_semantic_workflow_emits_evidence_use_manifest(self) -> None:
        workflow = (ROOT / ".github/workflows/careerhub-semantic.yml").read_text(encoding="utf-8")
        adapter = (ROOT / "scripts/web_analysis.py").read_text(encoding="utf-8")
        self.assertIn("evidence_use_manifest.json", workflow)
        self.assertIn("library_evidence", workflow)
        self.assertIn("source_id", workflow)
        self.assertIn('"hash"', adapter)
        self.assertIn("source_hashes", adapter)

    def test_normal_analysis_ui_uses_product_language(self) -> None:
        paths = [
            ROOT / "web-shell/site/app/analyse/page.tsx",
            ROOT / "web-shell/site/app/analyse/AnalyseClient.tsx",
            ROOT / "web-shell/site/app/analyse/[actionId]/page.tsx",
            ROOT / "web-shell/site/app/analyse/[actionId]/AnalysisResultClient.tsx",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        self.assertIn("Analyse job opening", combined)
        self.assertIn("Job analysis", combined)
        self.assertNotIn("Run HRDM-R", combined)
        self.assertNotIn("HRDM-R analysis", combined)
        self.assertNotIn("Hybridianesque is evaluated", combined)

    def test_global_process_tray_is_mounted(self) -> None:
        layout = (ROOT / "web-shell/site/app/layout.tsx").read_text(encoding="utf-8")
        tray = (ROOT / "web-shell/site/app/_components/GlobalProcessTray.tsx").read_text(encoding="utf-8")
        self.assertIn("<GlobalProcessTray", layout)
        self.assertIn("careerhub.active.analysis", tray)
        self.assertIn("/api/action/status?action_id=", tray)
        self.assertIn("2–5 minutes", tray)


if __name__ == "__main__":
    unittest.main()
