#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

VERSIONED_PREFIXES = (
    "src/",
    "core/",
    "schemas/",
    "scripts/",
    "stack/registry.yaml",
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
    engine_changed = any(
        p in VERSIONED_FILES or any(p.startswith(prefix) for prefix in VERSIONED_PREFIXES)
        for p in changed
    )
    if not engine_changed:
        print("No versioned central-engine change.")
        return

    current = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    try:
        previous = git("show", f"{args.base}:VERSION").strip()
    except subprocess.CalledProcessError:
        previous = ""

    if current == previous:
        raise SystemExit(
            f"Central CareerHub changed but VERSION did not: still {current}. "
            "Every motor/schema/workflow change requires a version bump."
        )

    ledger = f"stack/releases/{current}.yaml"
    if ledger not in changed and not (ROOT / ledger).exists():
        raise SystemExit(f"Missing release ledger for new version: {ledger}")

    print(f"Version governance OK: {previous or '<none>'} -> {current}")


if __name__ == "__main__":
    main()
