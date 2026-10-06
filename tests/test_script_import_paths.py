import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScriptImportPathTests(unittest.TestCase):
    def run_help(self, script: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script), "--help"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_bind_web_action_direct_execution_resolves_src_package(self):
        result = self.run_help("bind_web_action.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--manifest", result.stdout)
        self.assertNotIn("'careerhub' is not a package", result.stderr)

    def test_update_search_profile_direct_execution_resolves_src_package(self):
        result = self.run_help("update_search_profile.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--manifest", result.stdout)
        self.assertNotIn("'careerhub' is not a package", result.stderr)


if __name__ == "__main__":
    unittest.main()
