import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScriptImportPathTests(unittest.TestCase):
    def test_bind_web_action_direct_execution_resolves_src_package(self):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/bind_web_action.py"), "--help"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--manifest", result.stdout)
        self.assertNotIn("'careerhub' is not a package", result.stderr)


if __name__ == "__main__":
    unittest.main()
