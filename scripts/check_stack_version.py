#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]


def canonical_version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def registry() -> dict:
    return yaml.safe_load((ROOT / "stack/registry.yaml").read_text(encoding="utf-8"))


def local_check() -> list[str]:
    version = canonical_version()
    errors = []
    release = ROOT / "stack/releases" / f"{version}.yaml"
    if not release.exists():
        errors.append(f"Missing release ledger: {release.relative_to(ROOT)}")
    else:
        data = yaml.safe_load(release.read_text(encoding="utf-8"))
        if str(data.get("version")) != version:
            errors.append("Release ledger version does not match VERSION")
    init_text = (ROOT / "src/careerhub/__init__.py").read_text(encoding="utf-8")
    if "0.1.0-alpha" in init_text or "0.2." in init_text:
        errors.append("Package version must not be independently hard-coded")
    reg = registry()
    ids = [x["instance_id"] for x in reg.get("instances", [])]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate instance_id in stack registry")
    return errors


def gh_get(repo: str, path: str, token: str):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}, timeout=20)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def remote_check(token: str) -> list[str]:
    version = canonical_version()
    errors = []
    reg = registry()
    for inst in reg.get("instances", []):
        if inst.get("status") != "active":
            continue
        repo = inst["repository"]
        item = gh_get(repo, inst["instance_path"], token)
        if not item:
            errors.append(f"{repo}: missing {inst['instance_path']}")
            continue
        cfg = yaml.safe_load(base64.b64decode(item["content"]).decode("utf-8"))
        engine = cfg.get("careerhub", {}).get("engine", {})
        if engine.get("repository") != reg["engine_repository"]:
            errors.append(f"{repo}: wrong engine repository {engine.get('repository')!r}")
        if str(engine.get("version")) != version:
            errors.append(f"{repo}: engine version {engine.get('version')!r} != {version!r}")
        lock = gh_get(repo, inst["lock_path"], token)
        if not lock:
            errors.append(f"{repo}: missing generated {inst['lock_path']}")
        for forbidden in inst.get("forbidden_motor_paths", []):
            if gh_get(repo, forbidden, token):
                errors.append(f"{repo}: local motor path present: {forbidden}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--remote", action="store_true")
    args = ap.parse_args()
    errors = local_check()
    if args.remote:
        token = os.getenv("CAREERHUB_STACK_TOKEN", "")
        if not token:
            errors.append("CAREERHUB_STACK_TOKEN is required for remote stack verification")
        else:
            errors.extend(remote_check(token))
    if errors:
        for error in errors:
            print("ERROR", error)
        raise SystemExit(1)
    print("CareerHub stack version check OK:", canonical_version())


if __name__ == "__main__":
    main()
