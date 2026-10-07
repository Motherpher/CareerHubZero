#!/usr/bin/env python3
"""Copy the canonical CareerHub web shell and operations bridge into a profile repository.

Only centrally managed paths are touched. Person-owned personalisation paths are never
removed or overwritten by this script. A protected profile CSS hook is initialised once
when missing so every profile can attach its own visual expression without patching
managed runtime files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "web-shell" / "site"
MANIFEST = SOURCE / ".careerhub-managed.json"
OPERATIONS_WORKFLOW = ROOT / "templates" / "profile-workflows" / "careerhub-operations.yml"


def digest_tree(path: Path) -> str:
    h = hashlib.sha256()
    if not path.exists():
        return "missing"
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(str(item.relative_to(path)).encode())
        h.update(item.read_bytes())
    return h.hexdigest()


def copy_managed(source: Path, target: Path, managed_paths: list[str]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for rel in managed_paths:
        src = source / rel
        dst = target / rel
        if not src.exists():
            raise FileNotFoundError(f"Managed source path missing: {src}")
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def find_repo_root(profile_root: Path) -> Path:
    cursor = profile_root
    while True:
        if (cursor / ".git").exists():
            return cursor
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    if profile_root.name.lower() == "careerhub":
        return profile_root.parent
    return profile_root


def ensure_profile_visual_hook(personal_components: Path) -> None:
    """Create the protected profile stylesheet once, never overwrite it afterwards."""
    personal_components.mkdir(parents=True, exist_ok=True)
    hook = personal_components / "profile.css"
    if not hook.exists():
        hook.write_text(
            "/* Profile-owned CareerHub visual layer. Preserved across CHZero shell syncs. */\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile_repo", help="Path to checked-out personalised CareerHub profile root")
    args = parser.parse_args()

    profile_root = Path(args.profile_repo).resolve()
    repo_root = find_repo_root(profile_root)
    target_site = profile_root / "site"
    personalisation = profile_root / "personalisation"
    personal_components = target_site / "personal"

    spec = json.loads(MANIFEST.read_text())
    managed_paths = spec["managed_paths"]

    # Initialise the first-class protected visual hook before integrity hashes are taken.
    # This is a one-time bootstrap only; existing profile-owned CSS is never changed.
    ensure_profile_visual_hook(personal_components)

    before = {
        "personalisation": digest_tree(personalisation),
        "site/personal": digest_tree(personal_components),
    }

    copy_managed(SOURCE, target_site, managed_paths)

    workflow_target = repo_root / ".github" / "workflows" / "careerhub-operations.yml"
    workflow_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OPERATIONS_WORKFLOW, workflow_target)

    after = {
        "personalisation": digest_tree(personalisation),
        "site/personal": digest_tree(personal_components),
    }

    if before != after:
        raise RuntimeError(
            "Protected personalised paths changed during central web-shell sync; aborting."
        )

    print(json.dumps({
        "status": "ok",
        "target": str(target_site),
        "managed_paths": managed_paths,
        "operations_workflow": str(workflow_target),
        "protected_hashes": after,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
