import tempfile
import unittest
from pathlib import Path

from careerhub.hrdm_reports import inject_hrdm_panel


class HubSurfaceTests(unittest.TestCase):
    def test_hrdm_panel_is_single_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"CONTROL_ROOM.md"
            p.write_text("# CareerHub\n\n## 3 · Sök\n",encoding="utf-8")
            inject_hrdm_panel(p)
            inject_hrdm_panel(p)
            text=p.read_text(encoding="utf-8")
            self.assertEqual(text.count("CAREERHUB:HRDM:START"),1)
            self.assertIn("HRDM_REPORTS.md",text)
            self.assertIn("HRDM_LEDGER.md",text)


if __name__ == "__main__":
    unittest.main()
