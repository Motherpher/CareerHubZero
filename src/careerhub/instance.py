from __future__ import annotations

from pathlib import Path
import json
import yaml


class InstanceError(RuntimeError):
    pass


def _load(path: Path):
    if not path.exists():
        raise InstanceError(f"Missing required file: {path}")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def load_instance(instance_file: str | Path) -> dict:
    instance_file = Path(instance_file).resolve()
    cfg = _load(instance_file)
    root = instance_file.parent
    required = {
        "profile": cfg["profile"]["path"],
        "search": cfg["search"]["path"],
        "job_vault": cfg["state"]["job_vault"],
        "applications": cfg["state"]["applications"],
    }
    loaded = {"instance": cfg, "root": root}
    for key, rel in required.items():
        loaded[key] = _load(root / rel)
    return loaded


def validate_instance_paths(instance_file: str | Path) -> list[str]:
    instance_file = Path(instance_file).resolve()
    cfg = _load(instance_file)
    root = instance_file.parent
    errors: list[str] = []
    checks = [
        cfg.get("profile", {}).get("path"),
        cfg.get("search", {}).get("path"),
        cfg.get("state", {}).get("job_vault"),
        cfg.get("state", {}).get("applications"),
    ]
    for rel in [x for x in checks if x]:
        if not (root / rel).exists():
            errors.append(f"Missing configured path: {rel}")
    return errors
