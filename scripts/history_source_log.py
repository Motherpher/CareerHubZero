#!/usr/bin/env python3
"""Capture and validate sourced CareerHubZero development-history events.

Events are bound to the substantive *content delta*, not merely changed paths or
commit SHAs. Delta fingerprints deliberately ignore Git hunk coordinates and
blob-index lines so they survive squash merges and unrelated base movement while
still changing when the actual added/deleted content changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

EVENT_DIR = Path("stack/history/events")
EVENT_PREFIX = "stack/history/events/"
SCHEMA_VERSION = "1.1"

SUBSYSTEM_RULES: tuple[tuple[str, str], ...] = (
    ("site/", "web_surface"),
    ("src/careerhub/search", "search"),
    ("src/careerhub/sources", "search_sources"),
    ("src/careerhub/hrdm", "hrdm_analysis"),
    ("core/hrdm/", "hrdm_analysis"),
    ("src/careerhub/library", "library_evidence"),
    ("schemas/source_library", "library_evidence"),
    ("src/careerhub/geo", "geography"),
    ("schemas/job_geo", "geography"),
    ("src/careerhub/application", "application_state"),
    ("schemas/case", "application_state"),
    ("schemas/outcome_event", "application_state"),
    (".github/workflows/", "ci_operations"),
    ("scripts/", "developer_tooling"),
    ("tests/", "test_regression"),
    ("docs/history/", "development_history"),
    ("stack/history/", "development_history"),
    ("docs/", "documentation"),
    ("schemas/", "contracts_schemas"),
)


def run_git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def resolve_sha(ref: str, cwd: Path | None = None) -> str:
    return run_git("rev-parse", ref, cwd=cwd)


def repository_root(cwd: Path | None = None) -> Path:
    return Path(run_git("rev-parse", "--show-toplevel", cwd=cwd))


def is_history_event(path: str) -> bool:
    return path.startswith(EVENT_PREFIX) and path.endswith((".yml", ".yaml"))


def normalize_patch(patch: str) -> str:
    """Normalize volatile Git metadata while preserving the actual delta."""
    lines: list[str] = []
    for line in patch.splitlines():
        if line.startswith("index "):
            continue
        if line.startswith("@@"):
            lines.append("@@")
            continue
        lines.append(line)
    return "\n".join(lines).rstrip() + ("\n" if lines else "")


def delta_sha256(base: str, head: str, item: dict[str, str], cwd: Path | None = None) -> str:
    paths = [item["path"]]
    if item.get("old_path") and item["old_path"] != item["path"]:
        paths.insert(0, item["old_path"])
    patch = run_git(
        "diff",
        "--no-ext-diff",
        "--no-color",
        "--unified=0",
        "--find-renames",
        base,
        head,
        "--",
        *paths,
        cwd=cwd,
    )
    normalized = normalize_patch(patch)
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def collect_changes(base: str, head: str, cwd: Path | None = None) -> list[dict[str, str]]:
    output = run_git("diff", "--name-status", "--find-renames", base, head, cwd=cwd)
    changes: list[dict[str, str]] = []
    if not output:
        return changes
    for line in output.splitlines():
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") and len(parts) == 3:
            item = {"status": status, "old_path": parts[1], "path": parts[2]}
        elif len(parts) >= 2:
            item = {"status": status, "path": parts[-1]}
        else:
            raise ValueError(f"Unable to parse git change line: {line!r}")
        item["delta_sha256"] = delta_sha256(base, head, item, cwd=cwd)
        changes.append(item)
    return changes


def substantive_changes(changes: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [item for item in changes if not is_history_event(item["path"])]


def change_fingerprint(changes: Iterable[dict[str, str]]) -> str:
    canonical: list[str] = []
    for item in changes:
        canonical.append(
            "\t".join(
                [
                    item.get("status", ""),
                    item.get("old_path", ""),
                    item.get("path", ""),
                    item.get("delta_sha256", ""),
                ]
            )
        )
    canonical.sort()
    payload = "\n".join(canonical).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def collect_commits(base: str, head: str, cwd: Path | None = None) -> list[dict[str, str]]:
    fmt = "%H%x1f%aI%x1f%an%x1f%s"
    output = run_git("log", "--reverse", f"--format={fmt}", f"{base}..{head}", cwd=cwd)
    commits: list[dict[str, str]] = []
    if not output:
        return commits
    for line in output.splitlines():
        sha, authored_at, author, subject = line.split("\x1f", 3)
        commits.append({"sha": sha, "authored_at": authored_at, "author": author, "subject": subject})
    return commits


def normalize_wp_ref(value: str) -> str:
    text = value.strip().upper().replace("_", "-")
    match = re.fullmatch(r"(?:SIL-|OCT-)?WP(\d+)(?:[.-](\d+))?", text)
    if not match:
        return text
    major, minor = match.groups()
    return f"WP{int(major)}" + (f".{int(minor)}" if minor is not None else "")


def infer_wp_refs(*texts: str) -> list[str]:
    found: set[str] = set()
    pattern = re.compile(r"\b(?:SIL-|OCT-)?WP\d+(?:[.-]\d+)?\b", re.IGNORECASE)
    branch_pattern = re.compile(r"(?:^|[/_-])wp(\d+)[.-](\d+)(?:$|[/_-])", re.IGNORECASE)
    for text in texts:
        if not text:
            continue
        for match in pattern.findall(text):
            found.add(normalize_wp_ref(match))
        for major, minor in branch_pattern.findall(text):
            found.add(f"WP{int(major)}.{int(minor)}")
    return sorted(found)


def infer_subsystems(changes: Iterable[dict[str, str]]) -> list[str]:
    subsystems: set[str] = set()
    for item in changes:
        path = item["path"]
        matched = False
        for prefix, subsystem in SUBSYSTEM_RULES:
            if path.startswith(prefix):
                subsystems.add(subsystem)
                matched = True
        if not matched:
            subsystems.add("repository_core")
    return sorted(subsystems)


def read_github_event(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    event_path = Path(path)
    if not event_path.exists():
        return {}
    return json.loads(event_path.read_text(encoding="utf-8"))


def source_context(event: dict[str, Any], base_sha: str, head_sha: str) -> dict[str, Any]:
    pr = event.get("pull_request") or {}
    repo = event.get("repository") or {}
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repository = os.environ.get("GITHUB_REPOSITORY") or repo.get("full_name") or "unknown"
    run_id = os.environ.get("GITHUB_RUN_ID")
    pr_number = pr.get("number") or event.get("number")
    source: dict[str, Any] = {
        "repository": repository,
        "event_name": os.environ.get("GITHUB_EVENT_NAME", "local"),
        "base_sha": base_sha,
        "head_sha": head_sha,
        "branch": os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME") or "",
        "actor": os.environ.get("GITHUB_ACTOR", "local"),
    }
    if pr_number:
        source["pull_request"] = {
            "number": int(pr_number),
            "title": pr.get("title", ""),
            "url": pr.get("html_url") or f"{server}/{repository}/pull/{pr_number}",
        }
    if run_id:
        source["workflow_run"] = {"id": int(run_id), "url": f"{server}/{repository}/actions/runs/{run_id}"}
    return source


def default_event_id(source: dict[str, Any], head_sha: str) -> str:
    pr = source.get("pull_request") or {}
    return f"PR-{pr['number']}" if pr.get("number") else f"CHG-{head_sha[:12]}"


def default_output_path(event_id: str, root: Path) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", event_id).strip("-").lower()
    return root / EVENT_DIR / f"{safe}.yaml"


def build_event(
    *,
    base: str,
    head: str,
    root: Path,
    event_json: dict[str, Any] | None = None,
    summary: str = "",
    decision_context: str = "",
    work_packages: Iterable[str] = (),
    failure_ids: Iterable[str] = (),
    event_id: str | None = None,
) -> dict[str, Any]:
    base_sha = resolve_sha(base, cwd=root)
    head_sha = resolve_sha(head, cwd=root)
    all_changes = collect_changes(base_sha, head_sha, cwd=root)
    changes = substantive_changes(all_changes)
    commits = collect_commits(base_sha, head_sha, cwd=root)
    event_json = event_json or {}
    source = source_context(event_json, base_sha, head_sha)
    pr = event_json.get("pull_request") or {}
    inference_texts = [source.get("branch", ""), pr.get("title", ""), pr.get("body", "")]
    inference_texts.extend(commit["subject"] for commit in commits)
    inferred_wps = infer_wp_refs(*inference_texts)
    explicit_wps = [normalize_wp_ref(value) for value in work_packages if value.strip()]
    wps = sorted(set(explicit_wps) | set(inferred_wps))
    if not changes:
        raise ValueError("No substantive changes to capture; history-event files are self-exempt.")
    if not wps:
        raise ValueError("No WP reference found. Supply --wp so every development change has a scope owner.")
    if not summary:
        summary = pr.get("title", "") or (commits[-1]["subject"] if commits else "Sourced development change")
    head_time = run_git("show", "-s", "--format=%cI", head_sha, cwd=root)
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": event_id or default_event_id(source, head_sha),
        "recorded_at": head_time or datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "decision_context": decision_context,
        "work_packages": wps,
        "failure_ids": sorted(set(failure_ids)),
        "subsystems": infer_subsystems(changes),
        "source": source,
        "changes": {
            "fingerprint": change_fingerprint(changes),
            "file_count": len(changes),
            "files": changes,
        },
        "commits": commits,
        "provenance_contract": {
            "source_derived": True,
            "historical_snapshot": False,
            "coverage_basis": "normalized_content_delta",
        },
    }


def load_event(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"History event must be a mapping: {path}")
    return data


def validate_event_shape(event: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    for key in ("event_id", "summary", "work_packages", "subsystems", "source", "changes", "commits"):
        if key not in event:
            errors.append(f"{path}: missing {key}")
    if not event.get("work_packages"):
        errors.append(f"{path}: work_packages must not be empty")
    source = event.get("source") or {}
    for key in ("repository", "base_sha", "head_sha"):
        if not source.get(key):
            errors.append(f"{path}: source.{key} is required")
    changes = event.get("changes") or {}
    if not changes.get("fingerprint"):
        errors.append(f"{path}: changes.fingerprint is required")
    files = changes.get("files")
    if not isinstance(files, list):
        errors.append(f"{path}: changes.files must be a list")
    else:
        for item in files:
            if not item.get("delta_sha256"):
                errors.append(f"{path}: every changed file requires delta_sha256")
    return errors


def candidate_event_paths(base: str, head: str, root: Path) -> list[Path]:
    paths: list[Path] = []
    for item in collect_changes(base, head, cwd=root):
        path = item["path"]
        if is_history_event(path) and not item["status"].startswith("D"):
            full = root / path
            if full.exists():
                paths.append(full)
    return paths


def validate_history(base: str, head: str, root: Path) -> tuple[bool, list[str]]:
    base_sha = resolve_sha(base, cwd=root)
    head_sha = resolve_sha(head, cwd=root)
    changes = substantive_changes(collect_changes(base_sha, head_sha, cwd=root))
    if not changes:
        return True, ["No substantive changes; history-event-only diff is self-exempt."]
    expected = change_fingerprint(changes)
    event_paths = candidate_event_paths(base_sha, head_sha, root)
    if not event_paths:
        return False, [
            "Substantive change set has no changed stack/history/events/*.yaml record.",
            f"Expected fingerprint: {expected}",
        ]
    errors: list[str] = []
    for path in event_paths:
        try:
            event = load_event(path)
        except Exception as exc:  # pragma: no cover
            errors.append(f"{path}: {exc}")
            continue
        shape_errors = validate_event_shape(event, path)
        if shape_errors:
            errors.extend(shape_errors)
            continue
        if (event.get("changes") or {}).get("fingerprint") != expected:
            continue
        recorded_files = substantive_changes((event.get("changes") or {}).get("files") or [])
        if change_fingerprint(recorded_files) != expected:
            errors.append(f"{path}: recorded file deltas do not reproduce the event fingerprint")
            continue
        return True, [f"Sourced history coverage OK: {path.relative_to(root)} ({expected})"]
    errors.append(f"No changed history event matches substantive diff fingerprint {expected}")
    return False, errors


def capture_command(args: argparse.Namespace) -> int:
    root = repository_root(Path(args.cwd) if args.cwd else None)
    event_json = read_github_event(args.github_event or os.environ.get("GITHUB_EVENT_PATH"))
    event = build_event(
        base=args.base,
        head=args.head,
        root=root,
        event_json=event_json,
        summary=args.summary or "",
        decision_context=args.decision_context or "",
        work_packages=args.wp or [],
        failure_ids=args.failure or [],
        event_id=args.event_id,
    )
    output = Path(args.output) if args.output else default_output_path(event["event_id"], root)
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(event, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(output.relative_to(root))
    print(event["changes"]["fingerprint"])
    return 0


def validate_command(args: argparse.Namespace) -> int:
    root = repository_root(Path(args.cwd) if args.cwd else None)
    ok, messages = validate_history(args.base, args.head, root)
    for message in messages:
        print(message)
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", help="Repository path; defaults to current Git repository")
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture", help="Create/update a sourced history event")
    capture.add_argument("--base", required=True)
    capture.add_argument("--head", default="HEAD")
    capture.add_argument("--github-event", help="GitHub event JSON; defaults to GITHUB_EVENT_PATH")
    capture.add_argument("--event-id")
    capture.add_argument("--output")
    capture.add_argument("--summary")
    capture.add_argument("--decision-context")
    capture.add_argument("--wp", action="append", default=[])
    capture.add_argument("--failure", action="append", default=[])
    capture.set_defaults(func=capture_command)

    validate = sub.add_parser("validate", help="Require a sourced event for a substantive diff")
    validate.add_argument("--base", required=True)
    validate.add_argument("--head", default="HEAD")
    validate.set_defaults(func=validate_command)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
