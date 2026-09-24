from __future__ import annotations

from pathlib import Path
import json
import yaml


class InstanceError(RuntimeError):
    pass


ALLOWED_CAREER_SOURCE_TYPES = {
    "cv",
    "professional_profile",
    "employment_record",
    "qualification",
    "certification",
    "portfolio_work_sample",
    "employer_reference",
    "verified_project_record",
}

FORBIDDEN_PROFILE_KEYS = {
    "private_life",
    "personal_life",
    "family",
    "children",
    "relationship",
    "marital_status",
    "health",
    "medical",
    "medical_history",
    "religion",
    "ethnicity",
    "sexual_orientation",
    "political_affiliation",
    "personal_finance",
    "private_notes",
    "career_preferences",
    "specific_wishes_or_needs",
}


def _load(path: Path):
    if not path.exists():
        raise InstanceError(f"Missing required file: {path}")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def _walk_keys(value, prefix=""):
    if isinstance(value, dict):
        for key, child in value.items():
            key_s = str(key)
            path = f"{prefix}.{key_s}" if prefix else key_s
            yield path, key_s
            yield from _walk_keys(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{prefix}[{index}]")


def validate_profile_policy(profile: dict, search: dict | None = None) -> list[str]:
    """Hard policy: only verified career-source evidence may shape candidate matching.

    User wishes/needs are allowed only in the search profile as a search-only overlay.
    They are never candidate evidence and may never enter the matchable profile.
    """
    errors: list[str] = []
    if not isinstance(profile, dict):
        return ["Candidate profile must be an object."]

    for path, key in _walk_keys(profile):
        if key.lower() in FORBIDDEN_PROFILE_KEYS:
            errors.append(f"Forbidden non-career/private-life field in candidate profile: {path}")

    sources = profile.get("career_sources", [])
    if not isinstance(sources, list):
        errors.append("career_sources must be a list.")
        sources = []

    verified_source_ids: set[str] = set()
    seen_source_ids: set[str] = set()
    for idx, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"career_sources[{idx}] must be an object.")
            continue
        source_id = str(source.get("id") or "").strip()
        source_type = str(source.get("source_type") or "").strip()
        verification_status = str(source.get("verification_status") or "").strip()
        if not source_id:
            errors.append(f"career_sources[{idx}] is missing id.")
        elif source_id in seen_source_ids:
            errors.append(f"Duplicate career source id: {source_id}")
        else:
            seen_source_ids.add(source_id)
        if source_type not in ALLOWED_CAREER_SOURCE_TYPES:
            errors.append(
                f"career_sources[{idx}] has non-career or unsupported source_type: {source_type or '<missing>'}"
            )
        if verification_status != "verified":
            errors.append(
                f"career_sources[{idx}] must have verification_status=verified before it can enter the profile."
            )
        if source_id and source_type in ALLOWED_CAREER_SOURCE_TYPES and verification_status == "verified":
            verified_source_ids.add(source_id)

    evidence = profile.get("evidence", [])
    if not isinstance(evidence, list):
        errors.append("evidence must be a list.")
        evidence = []

    evidence_ids: set[str] = set()
    for idx, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{idx}] must be an object.")
            continue
        evidence_id = str(item.get("id") or "").strip()
        if evidence_id:
            evidence_ids.add(evidence_id)
        if item.get("status") != "verified":
            errors.append(f"evidence[{idx}] must have status=verified.")
        source_ids = item.get("source_ids", [])
        if not isinstance(source_ids, list) or not source_ids:
            errors.append(f"evidence[{idx}] must reference at least one verified career source.")
            continue
        invalid = [sid for sid in source_ids if sid not in verified_source_ids]
        if invalid:
            errors.append(
                f"evidence[{idx}] references non-verified/non-career source ids: {', '.join(map(str, invalid))}"
            )

    positioning = profile.get("positioning", {})
    if positioning and isinstance(positioning, dict):
        derived = positioning.get("derived_from_evidence_ids", [])
        if derived:
            invalid = [eid for eid in derived if eid not in evidence_ids]
            if invalid:
                errors.append(
                    "positioning.derived_from_evidence_ids contains ids not present in verified evidence: "
                    + ", ".join(map(str, invalid))
                )

    if search is not None:
        overlay = search.get("user_search_overlay", {}) if isinstance(search, dict) else {}
        if overlay:
            if overlay.get("source") != "user_input":
                errors.append("user_search_overlay.source must be user_input.")
            if overlay.get("scope") != "search_only":
                errors.append("user_search_overlay.scope must be search_only.")
            if not isinstance(overlay.get("specific_wishes_or_needs", ""), str):
                errors.append("user_search_overlay.specific_wishes_or_needs must be a string.")

    return errors


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

    policy_errors = validate_profile_policy(loaded["profile"], loaded["search"])
    if policy_errors:
        raise InstanceError("Candidate-profile policy violation:\n- " + "\n- ".join(policy_errors))

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

    if not errors:
        try:
            profile = _load(root / cfg["profile"]["path"])
            search = _load(root / cfg["search"]["path"])
            if str(search.get("version") or "") != "2.1":
                errors.append("Stable profile nodes must use search_profile version 2.1.")
            errors.extend(validate_profile_policy(profile, search))
        except InstanceError as exc:
            errors.append(str(exc))

    return errors


def load_profile_node(manifest_file: str | Path) -> dict:
    """Load the stable versionless careerhub.yaml profile-node contract."""
    manifest_file = Path(manifest_file).resolve()
    cfg = _load(manifest_file)
    root = manifest_file.parent

    required = {
        "profile": cfg["profile"]["path"],
        "search": cfg["search"]["path"],
        "job_vault": cfg["state"]["job_vault"],
        "applications": cfg["state"]["applications"],
        "hrdm_ledger": cfg["state"]["hrdm_ledger"],
    }
    loaded = {"manifest": cfg, "root": root}
    for key, rel in required.items():
        path = root / rel
        if key == "hrdm_ledger" and not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"schema_version": "1.0", "updated_at": None, "runs": []}, indent=2) + "\n",
                encoding="utf-8",
            )
        loaded[key] = _load(path)

    policy_errors = validate_profile_policy(loaded["profile"], loaded["search"])
    if policy_errors:
        raise InstanceError("Candidate-profile policy violation:\n- " + "\n- ".join(policy_errors))

    loaded["paths"] = {
        "profile": root / cfg["profile"]["path"],
        "search": root / cfg["search"]["path"],
        "job_vault": root / cfg["state"]["job_vault"],
        "applications": root / cfg["state"]["applications"],
        "hrdm_ledger": root / cfg["state"]["hrdm_ledger"],
        "hrdm_reports": root / cfg["artifacts"]["hrdm_reports"],
        "hrdm_history": root / cfg["artifacts"]["hrdm_history"],
    }
    return loaded


def validate_profile_node_paths(manifest_file: str | Path) -> list[str]:
    manifest_file = Path(manifest_file).resolve()
    cfg = _load(manifest_file)
    root = manifest_file.parent
    errors: list[str] = []

    if cfg.get("schema_version") != "1.0":
        errors.append("careerhub.yaml schema_version must be 1.0")
    if not cfg.get("profile_id"):
        errors.append("careerhub.yaml requires profile_id")

    checks = [
        cfg.get("profile", {}).get("path"),
        cfg.get("search", {}).get("path"),
        cfg.get("state", {}).get("job_vault"),
        cfg.get("state", {}).get("applications"),
    ]
    for rel in [x for x in checks if x]:
        if not (root / rel).exists():
            errors.append(f"Missing configured path: {rel}")

    ledger = cfg.get("state", {}).get("hrdm_ledger")
    if not ledger:
        errors.append("Missing state.hrdm_ledger")
    artifacts = cfg.get("artifacts", {})
    for key in ("hrdm_reports", "hrdm_history"):
        if not artifacts.get(key):
            errors.append(f"Missing artifacts.{key}")

    if not errors:
        try:
            profile = _load(root / cfg["profile"]["path"])
            search = _load(root / cfg["search"]["path"])
            errors.extend(validate_profile_policy(profile, search))
        except InstanceError as exc:
            errors.append(str(exc))
    return errors
