from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


def safe_target(root: Path, relative: str) -> Path:
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise SystemExit(f"Unsafe bundle path: {relative}")
    target = (root / relative_path).resolve()
    root_resolved = root.resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise SystemExit(f"Bundle path escapes profile root: {relative}") from exc
    return target


def materialize(bundle_path: Path, root: Path, expected_action_id: str = "") -> dict:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    action_id = str(bundle.get("action_id") or "")
    if expected_action_id and action_id != expected_action_id:
        raise SystemExit(f"Bundle action mismatch: expected {expected_action_id}, got {action_id}")
    if str(bundle.get("schema_version") or "") != "1.0":
        raise SystemExit("Unsupported semantic bundle schema version.")

    written: list[str] = []
    deleted: list[str] = []

    for item in bundle.get("files") or []:
        relative = str(item.get("path") or "").strip()
        if not relative:
            continue
        target = safe_target(root, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        encoding = str(item.get("encoding") or "base64")
        content = str(item.get("content") or "")
        if encoding == "base64":
            target.write_bytes(base64.b64decode(content))
        elif encoding == "utf-8":
            target.write_text(content, encoding="utf-8")
        else:
            raise SystemExit(f"Unsupported file encoding for {relative}: {encoding}")
        written.append(relative)

    for relative in bundle.get("deleted_paths") or []:
        relative = str(relative or "").strip()
        if not relative:
            continue
        target = safe_target(root, relative)
        if target.exists() and target.is_file():
            target.unlink()
            deleted.append(relative)

    return {
        "action_id": action_id,
        "written": written,
        "deleted": deleted,
        "files_written": len(written),
        "files_deleted": len(deleted),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--action-id", default="")
    args = parser.parse_args()
    result = materialize(Path(args.bundle), Path(args.root), args.action_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
