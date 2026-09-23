#!/usr/bin/env python3
from __future__ import annotations

import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com"


def version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def load_registry() -> dict:
    return yaml.safe_load((ROOT / "stack/registry.yaml").read_text(encoding="utf-8"))


def headers(token: str):
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


def get_file(repo: str, path: str, token: str):
    r = requests.get(f"{API}/repos/{repo}/contents/{path}", headers=headers(token), timeout=20)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def put_file(repo: str, path: str, content: str, token: str, message: str, sha: str | None = None):
    payload = {"message": message, "content": base64.b64encode(content.encode()).decode()}
    if sha:
        payload["sha"] = sha
    r = requests.put(f"{API}/repos/{repo}/contents/{path}", headers=headers(token), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    token = os.getenv("CAREERHUB_STACK_TOKEN", "")
    if not token:
        raise SystemExit("CAREERHUB_STACK_TOKEN is required")
    reg = load_registry()
    current = version()
    failures = []
    for inst in reg.get("instances", []):
        if inst.get("status") != "active" or not inst.get("auto_sync", False):
            continue
        repo = inst["repository"]
        item = get_file(repo, inst["instance_path"], token)
        if not item:
            failures.append(f"{repo}: missing instance file {inst['instance_path']}")
            continue
        cfg = yaml.safe_load(base64.b64decode(item["content"]).decode("utf-8"))
        cfg.setdefault("careerhub", {}).setdefault("engine", {})
        cfg["careerhub"]["engine"]["repository"] = reg["engine_repository"]
        cfg["careerhub"]["engine"]["version"] = current
        blockers = [p for p in inst.get("forbidden_motor_paths", []) if get_file(repo, p, token)]
        aligned = not blockers
        lock = {
            "schema_version": "1.0",
            "stack_id": reg["stack_id"],
            "instance_id": inst["instance_id"],
            "engine_repository": reg["engine_repository"],
            "engine_version": current,
            "synced_at": datetime.now(timezone.utc).isoformat(),
            "alignment": "aligned" if aligned else "blocked",
            "blockers": blockers,
            "generated_by": "Motherpher/CareerHubZero",
        }
        put_file(repo, inst["instance_path"], yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), token, f"CareerHub stack: sync engine {current}", item["sha"])
        lock_item = get_file(repo, inst["lock_path"], token)
        put_file(repo, inst["lock_path"], yaml.safe_dump(lock, sort_keys=False, allow_unicode=True), token, f"CareerHub stack: lock engine {current}", lock_item["sha"] if lock_item else None)
        print(json.dumps({"repository": repo, "version": current, "alignment": lock["alignment"], "blockers": blockers}))
        if blockers:
            failures.append(f"{repo}: local motor blocks stack alignment: {', '.join(blockers)}")
    if failures:
        for failure in failures:
            print("ERROR", failure)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
