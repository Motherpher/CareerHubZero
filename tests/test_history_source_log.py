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
            {"status": "M", "path": "site/app/page.tsx", "delta_sha256": "sha256:a"},
            {"status": "A", "path": "tests/test_x.py", "delta_sha256": "sha256:b"},
        ]
        b = list(reversed(a))
        self.assertEqual(hsl.change_fingerprint(a), hsl.change_fingerprint(b))

    def test_fingerprint_changes_when_content_delta_changes(self) -> None:
        a = [{"status": "M", "path": "same.txt", "delta_sha256": "sha256:a"}]
        b = [{"status": "M", "path": "same.txt", "delta_sha256": "sha256:b"}]
        self.assertNotEqual(hsl.change_fingerprint(a), hsl.change_fingerprint(b))

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

    def test_normalized_delta_survives_unrelated_base_movement(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)
            (root / "same.txt").write_text("a\nb\nc\n", encoding="utf-8")
            (root / "other.txt").write_text("one\n", encoding="utf-8")
            self._commit_all(root, "baseline")
            base = self._git(root, "rev-parse", "HEAD")

            self._git(root, "checkout", "-b", "feature")
            (root / "same.txt").write_text("a\nB\nc\n", encoding="utf-8")
            self._commit_all(root, "WP40.0 feature")
            feature = self._git(root, "rev-parse", "HEAD")
            original = hsl.substantive_changes(hsl.collect_changes(base, feature, cwd=root))

            self._git(root, "checkout", "master")
            (root / "other.txt").write_text("two\n", encoding="utf-8")
            self._commit_all(root, "unrelated main change")
            moved_base = self._git(root, "rev-parse", "HEAD")
            self._git(root, "merge", "--no-ff", "feature", "-m", "merge feature")
            merged = self._git(root, "rev-parse", "HEAD")
            merged_delta = hsl.substantive_changes(hsl.collect_changes(moved_base, merged, cwd=root))

            self.assertEqual(hsl.change_fingerprint(original), hsl.change_fingerprint(merged_delta))

    def test_capture_and_validate_real_git_diff(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)
            (root / "README.md").write_text("baseline\n", encoding="utf-8")
            self._commit_all(root, "baseline")
            base = self._git(root, "rev-parse", "HEAD")

            (root / "site/app").mkdir(parents=True)
            (root / "site/app/page.tsx").write_text("export default 1\n", encoding="utf-8")
            self._commit_all(root, "WP40.0 add source logger fixture")
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

            self.assertTrue(event["changes"]["files"][0]["delta_sha256"].startswith("sha256:"))
            event_path = root / "stack/history/events/test.yaml"
            event_path.parent.mkdir(parents=True)
            event_path.write_text(yaml.safe_dump(event, sort_keys=False, allow_unicode=True), encoding="utf-8")
            self._commit_all(root, "history: record fixture change")
            head = self._git(root, "rev-parse", "HEAD")

            ok, messages = hsl.validate_history(base, head, root)
            self.assertTrue(ok, messages)

            event["changes"]["fingerprint"] = "sha256:broken"
            event_path.write_text(yaml.safe_dump(event, sort_keys=False, allow_unicode=True), encoding="utf-8")
            self._commit_all(root, "history: break fixture")
            broken_head = self._git(root, "rev-parse", "HEAD")
            ok, _ = hsl.validate_history(base, broken_head, root)
            self.assertFalse(ok)

    def test_bootstrap_event_can_list_files_without_per_file_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)
            (root / "README.md").write_text("baseline\n", encoding="utf-8")
            self._commit_all(root, "baseline")
            base = self._git(root, "rev-parse", "HEAD")

            (root / "CHANGELOG.md").write_text("# Change\n", encoding="utf-8")
            self._commit_all(root, "WP40.0 bootstrap change")
            source_head = self._git(root, "rev-parse", "HEAD")
            actual = hsl.substantive_changes(hsl.collect_changes(base, source_head, cwd=root))
            fingerprint = hsl.change_fingerprint(actual)

            event = {
                "schema_version": "1.1",
                "event_id": "PR-BOOTSTRAP",
                "summary": "bootstrap",
                "work_packages": ["WP40.0"],
                "subsystems": ["development_history"],
                "source": {
                    "repository": "Motherpher/CareerHubZero",
                    "base_sha": base,
                    "head_sha": source_head,
                },
                "changes": {
                    "fingerprint": fingerprint,
                    "file_count": 1,
                    "files": [{"status": "A", "path": "CHANGELOG.md"}],
                },
                "commits": [],
            }
            event_path = root / "stack/history/events/bootstrap.yaml"
            event_path.parent.mkdir(parents=True)
            event_path.write_text(yaml.safe_dump(event, sort_keys=False), encoding="utf-8")
            self._commit_all(root, "history: add bootstrap event")
            head = self._git(root, "rev-parse", "HEAD")

            ok, messages = hsl.validate_history(base, head, root)
            self.assertTrue(ok, messages)

    def _init_repo(self, root: Path) -> None:
        self._git(root, "init")
        self._git(root, "config", "user.email", "test@example.com")
        self._git(root, "config", "user.name", "History Test")

    def _commit_all(self, root: Path, message: str) -> None:
        self._git(root, "add", "-A")
        self._git(root, "commit", "-m", message)

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
