#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]

VERSIONED_PREFIXES = (
    "src/",
    "core/",
    "schemas/",
    "scripts/",
    "stack/registry.yaml",
    "governance/household/",
    ".github/workflows/",
)
VERSIONED_FILES = {"requirements.txt"}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    args = ap.parse_args()

    changed = [x for x in git("diff", "--name-only", f"{args.base}...HEAD").splitlines() if x]
    body_changed = any(
        p in VERSIONED_FILES or any(p.startswith(prefix) for prefix in VERSIONED_PREFIXES)
        for p in changed
    )
    if not body_changed:
        print("No versioned CareerHub body change.")
        return

    current = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    ledger_path = ROOT / "stack" / "releases" / f"{current}.yaml"
    if not ledger_path.exists():
        raise SystemExit(f"Missing release ledger for current version: {ledger_path.relative_to(ROOT)}")
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) or {}
    if str(ledger.get("version")) != current:
        raise SystemExit("Current release ledger does not match VERSION.")

    try:
        previous = git("show", f"{args.base}:VERSION").strip()
    except subprocess.CalledProcessError:
        previous = ""

    if current != previous:
        print(f"Version governance OK: {previous or '<none>'} -> {current}")
        return

    # An explicitly open pre-release is the governed integration envelope for a
    # multi-commit sprint. This prevents artificial version inflation while
    # keeping closed/stable releases immutable.
    if current.endswith("-alpha") and ledger.get("development_open") is True and ledger.get("status") == "current":
        print(f"Version governance OK: continuing open integration line {current}.")
        return

    raise SystemExit(
        f"CareerHub body changed while release {current} is closed. "
        "Open a new pre-release/version before changing runtime/schema/workflow code."
    )


if __name__ == "__main__":
    main()
