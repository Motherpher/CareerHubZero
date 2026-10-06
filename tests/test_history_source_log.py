from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import history_source_log as hsl


class HistorySourceLogTests(unittest.TestCase):
    def test_fingerprint_is_order_independent(self) -> None:
        a = [
            {"status": "M", "path": "site/app/page.tsx"},
            {"status": "A", "path": "tests/test_x.py"},
        ]
        b = list(reversed(a))
        self.assertEqual(hsl.change_fingerprint(a), hsl.change_fingerprint(b))

    def test_wp_inference_normalises_branch_style(self) -> None:
        refs = hsl.infer_wp_refs("wp40-0/history-source-gate", "WP39 close-loop")
        self.assertEqual(refs, ["WP39", "WP40.0"])

    def test_subsystem_inference(self) -> None:
        changes = [
            {"status": "M", "path": "site/app/analyse/AnalyseClient.tsx"},
            {"status": "M", "path": ".github/workflows/validate.yml"},
            {"status": "A", "path": "tests/test_history_source_log.py"},
        ]
        self.assertEqual(
            hsl.infer_subsystems(changes),
            ["ci_operations", "test_regression", "web_surface"],
        )

    def test_capture_and_validate_real_git_diff(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._git(root, "init")
            self._git(root, "config", "user.email", "test@example.com")
            self._git(root, "config", "user.name", "History Test")
            (root / "README.md").write_text("baseline\n", encoding="utf-8")
            self._git(root, "add", "README.md")
            self._git(root, "commit", "-m", "baseline")
            base = self._git(root, "rev-parse", "HEAD")

            (root / "site/app").mkdir(parents=True)
            (root / "site/app/page.tsx").write_text("export default 1\n", encoding="utf-8")
            self._git(root, "add", "site/app/page.tsx")
            self._git(root, "commit", "-m", "WP40.0 add source logger fixture")
            source_head = self._git(root, "rev-parse", "HEAD")

            old_env = dict(os.environ)
            try:
                os.environ["GITHUB_REPOSITORY"] = "Motherpher/CareerHubZero"
                os.environ["GITHUB_HEAD_REF"] = "wp40-0/test"
                event = hsl.build_event(
                    base=base,
                    head=source_head,
                    root=root,
                    work_packages=["WP40.0"],
                    summary="Test sourced history",
                )
            finally:
                os.environ.clear()
                os.environ.update(old_env)

            event_path = root / "stack/history/events/test.yaml"
            event_path.parent.mkdir(parents=True)
            event_path.write_text(
                yaml.safe_dump(event, sort_keys=False, allow_unicode=True), encoding="utf-8"
            )
            self._git(root, "add", "stack/history/events/test.yaml")
            self._git(root, "commit", "-m", "history: record fixture change")
            head = self._git(root, "rev-parse", "HEAD")

            ok, messages = hsl.validate_history(base, head, root)
            self.assertTrue(ok, messages)

            event["changes"]["fingerprint"] = "sha256:broken"
            event_path.write_text(
                yaml.safe_dump(event, sort_keys=False, allow_unicode=True), encoding="utf-8"
            )
            self._git(root, "add", "stack/history/events/test.yaml")
            self._git(root, "commit", "-m", "history: break fixture")
            broken_head = self._git(root, "rev-parse", "HEAD")
            ok, _ = hsl.validate_history(base, broken_head, root)
            self.assertFalse(ok)

    @staticmethod
    def _git(root: Path, *args: str) -> str:
        env = dict(os.environ)
        env.setdefault("GIT_AUTHOR_DATE", "2026-10-07T00:00:00+00:00")
        env.setdefault("GIT_COMMITTER_DATE", "2026-10-07T00:00:00+00:00")
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        ).stdout.strip()


if __name__ == "__main__":
    unittest.main()
