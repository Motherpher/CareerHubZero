#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def main() -> None:
    errors: list[str] = []
    current = version()

    release = ROOT / "stack" / "releases" / f"{current}.yaml"
    if not release.exists():
        errors.append(f"Missing release ledger: {release.relative_to(ROOT)}")
    else:
        data = yaml.safe_load(release.read_text(encoding="utf-8")) or {}
        if str(data.get("version")) != current:
            errors.append("Release ledger version does not match VERSION")

    registry = yaml.safe_load((ROOT / "stack/registry.yaml").read_text(encoding="utf-8")) or {}
    if registry.get("architecture") != "unified_body":
        errors.append("Registry must declare architecture=unified_body")

    profiles = registry.get("profiles", [])
    ids = [p.get("profile_id") for p in profiles]
    if not profiles:
        errors.append("Registry has no active profiles")
    if len(ids) != len(set(ids)):
        errors.append("Duplicate profile_id in registry")

    for p in profiles:
        if p.get("status") == "active":
            if not p.get("repository"):
                errors.append(f"{p.get('profile_id')}: missing repository")
            if not p.get("manifest_path"):
                errors.append(f"{p.get('profile_id')}: missing manifest_path")

    schema = ROOT / "schemas/careerhub_manifest.schema.json"
    try:
        json.loads(schema.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Invalid profile-manifest schema: {exc}")

    init_text = (ROOT / "src/careerhub/__init__.py").read_text(encoding="utf-8")
    for stale in ("0.1.0-alpha", "0.2.0-alpha", "0.2.1-alpha"):
        if stale in init_text:
            errors.append("Package version must come from VERSION, not a hard-coded package constant")
            break

    if errors:
        for error in errors:
            print("ERROR", error)
        raise SystemExit(1)

    print("CareerHub unified body check OK:", current)
    print("Profiles:", ", ".join(str(x) for x in ids))


if __name__ == "__main__":
    main()
