"""WP40.1 profile-state integrity and conservative reset planning.

The reset contract is intentionally asymmetric: CareerHub may identify strongly
synthetic/test residue automatically, but uncertain or orphaned material is never
auto-deleted. Apply mode refuses unsafe paths and preserves all unclassified
career/evidence state.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml


class ResetClass(StrEnum):
    PRESERVE = "PRESERVE"
    SYNTHETIC_DELETE = "SYNTHETIC_DELETE"
    TRANSIENT_CLEAR = "TRANSIENT_CLEAR"
    ORPHAN_REVIEW = "ORPHAN_REVIEW"
    UNKNOWN_BLOCK = "UNKNOWN_BLOCK"


@dataclass(frozen=True)
class ResetDecision:
    reset_class: ResetClass
    object_type: str
    object_id: str
    reason: str
    paths: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["reset_class"] = self.reset_class.value
        data["paths"] = list(self.paths)
        return data


@dataclass
class ResetPlan:
    profile_id: str
    profile_root: str
    ledger_path: str
    decisions: list[ResetDecision]

    @property
    def blocked(self) -> bool:
        return any(item.reset_class is ResetClass.UNKNOWN_BLOCK for item in self.decisions)

    def to_dict(self) -> dict[str, Any]:
        counts = {item.value: 0 for item in ResetClass}
        for decision in self.decisions:
            counts[decision.reset_class.value] += 1
        return {
            "schema_version": "1.0",
            "profile_id": self.profile_id,
            "profile_root": self.profile_root,
            "ledger_path": self.ledger_path,
            "blocked": self.blocked,
            "counts": counts,
            "decisions": [item.to_dict() for item in self.decisions],
        }


_TITLE_TEST = re.compile(r"\bWP\d+(?:[.-]\d+)?\b.*(?:end[- ]to[- ]end|e2e|test role|test)", re.I)
_TEST_COMPANY = re.compile(r"careerhub\s+test\s+harness", re.I)
_TEST_URL = re.compile(r"(?:careerhub\.local|localhost).*(?:test|e2e|wp\d+)", re.I)


def classify_hrdm_run(run: Any) -> ResetDecision:
    if not isinstance(run, dict):
        return ResetDecision(ResetClass.UNKNOWN_BLOCK, "hrdm_run", "unknown", "HRDM ledger entry is not an object.")

    run_id = str(run.get("run_id") or run.get("process_id") or run.get("job_id") or "").strip()
    title = str(run.get("title") or run.get("role") or "").strip()
    company = str(run.get("company") or "").strip()
    job_url = str(run.get("job_url") or "").strip()
    paths = run.get("paths") if isinstance(run.get("paths"), dict) else {}
    linked_paths = tuple(str(value) for value in paths.values() if isinstance(value, str) and value.strip())

    if not run_id:
        return ResetDecision(ResetClass.UNKNOWN_BLOCK, "hrdm_run", "unknown", "HRDM run has no stable identifier.", linked_paths)

    markers: list[str] = []
    if _TITLE_TEST.search(title):
        markers.append("synthetic test title")
    if _TEST_COMPANY.search(company):
        markers.append("CareerHub test-harness employer")
    if _TEST_URL.search(job_url):
        markers.append("local/test vacancy URL")

    if len(markers) >= 2:
        return ResetDecision(
            ResetClass.SYNTHETIC_DELETE,
            "hrdm_run",
            run_id,
            "Strong synthetic residue markers: " + "; ".join(markers),
            linked_paths,
        )
    if markers:
        return ResetDecision(
            ResetClass.ORPHAN_REVIEW,
            "hrdm_run",
            run_id,
            "Only one synthetic marker is present; manual review required: " + markers[0],
            linked_paths,
        )

    return ResetDecision(ResetClass.PRESERVE, "hrdm_run", run_id, "No strong synthetic/test signature detected.", linked_paths)


def classify_transient_state(object_id: str, state: str) -> ResetDecision:
    normalized = state.strip().upper()
    if normalized in {"PREPARING", "WAITING_FOR_EXECUTION", "QUEUED"}:
        return ResetDecision(ResetClass.TRANSIENT_CLEAR, "transient_state", object_id, f"Non-terminal UI/process state: {normalized}.")
    if normalized in {"RUNNING", "COMPLETED", "FAILED"}:
        return ResetDecision(ResetClass.PRESERVE, "transient_state", object_id, f"Execution state {normalized} is not safe to clear automatically.")
    return ResetDecision(ResetClass.UNKNOWN_BLOCK, "transient_state", object_id, f"Unknown transient state: {normalized or '<empty>'}.")


def _load_manifest(profile_root: Path) -> dict[str, Any]:
    manifest_path = profile_root / "careerhub.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing CareerHub manifest: {manifest_path}")
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("careerhub.yaml must contain an object.")
    return data


def _safe_relative_path(profile_root: Path, raw: str, allowed_roots: tuple[Path, ...]) -> Path | None:
    candidate = (profile_root / raw).resolve()
    root = profile_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if any(candidate == allowed or allowed in candidate.parents for allowed in allowed_roots):
        return candidate
    return None


def build_reset_plan(profile_root: Path) -> ResetPlan:
    profile_root = profile_root.resolve()
    manifest = _load_manifest(profile_root)
    profile_id = str(manifest.get("profile_id") or "").strip()
    if not profile_id:
        raise ValueError("CareerHub manifest is missing profile_id.")

    state = manifest.get("state") if isinstance(manifest.get("state"), dict) else {}
    artifacts = manifest.get("artifacts") if isinstance(manifest.get("artifacts"), dict) else {}
    ledger_rel = str(state.get("hrdm_ledger") or "data/hrdm_ledger.json")
    ledger_path = (profile_root / ledger_rel).resolve()
    try:
        ledger_path.relative_to(profile_root)
    except ValueError as exc:
        raise ValueError("HRDM ledger path escapes the profile root.") from exc

    allowed_roots = tuple(
        (profile_root / str(value)).resolve()
        for key in ("hrdm_reports", "hrdm_history")
        if (value := artifacts.get(key))
    )
    if not allowed_roots:
        raise ValueError("Manifest has no HRDM artifact roots.")

    if ledger_path.exists():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    else:
        ledger = {"schema_version": "1.0", "runs": []}
    runs = ledger.get("runs", []) if isinstance(ledger, dict) else []
    if not isinstance(runs, list):
        raise ValueError("HRDM ledger runs must be an array.")

    decisions: list[ResetDecision] = []
    referenced_files: set[Path] = set()
    for run in runs:
        decision = classify_hrdm_run(run)
        unsafe: list[str] = []
        safe_paths: list[str] = []
        for raw in decision.paths:
            resolved = _safe_relative_path(profile_root, raw, allowed_roots)
            if resolved is None:
                unsafe.append(raw)
            else:
                referenced_files.add(resolved)
                safe_paths.append(raw)
        if unsafe:
            decision = ResetDecision(
                ResetClass.UNKNOWN_BLOCK,
                decision.object_type,
                decision.object_id,
                "Run references paths outside declared HRDM artifact roots: " + ", ".join(unsafe),
                tuple(safe_paths + unsafe),
            )
        decisions.append(decision)

    # Any result artifact not referenced by the ledger is a review item, never an auto-delete.
    for artifact_root in allowed_roots:
        if not artifact_root.exists():
            continue
        for result_file in artifact_root.rglob("HRDM_result.json"):
            resolved = result_file.resolve()
            if resolved not in referenced_files:
                decisions.append(
                    ResetDecision(
                        ResetClass.ORPHAN_REVIEW,
                        "hrdm_artifact",
                        str(result_file.parent.relative_to(profile_root)),
                        "HRDM result artifact is not referenced by the current ledger.",
                        (str(result_file.relative_to(profile_root)),),
                    )
                )

    return ResetPlan(profile_id, str(profile_root), str(ledger_path.relative_to(profile_root)), decisions)


def apply_reset_plan(profile_root: Path, plan: ResetPlan) -> dict[str, Any]:
    profile_root = profile_root.resolve()
    if plan.blocked:
        raise RuntimeError("Reset plan contains UNKNOWN_BLOCK items; refusing apply mode.")
    manifest = _load_manifest(profile_root)
    state = manifest.get("state") if isinstance(manifest.get("state"), dict) else {}
    ledger_path = (profile_root / str(state.get("hrdm_ledger") or "data/hrdm_ledger.json")).resolve()
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {"schema_version": "1.0", "runs": []}
    runs = ledger.get("runs", []) if isinstance(ledger, dict) else []

    delete_ids = {
        decision.object_id
        for decision in plan.decisions
        if decision.object_type == "hrdm_run" and decision.reset_class is ResetClass.SYNTHETIC_DELETE
    }
    kept_runs = []
    removed_runs = 0
    for run in runs:
        run_id = str(run.get("run_id") or run.get("process_id") or run.get("job_id") or "") if isinstance(run, dict) else ""
        if run_id in delete_ids:
            removed_runs += 1
        else:
            kept_runs.append(run)

    removed_files = 0
    for decision in plan.decisions:
        if decision.reset_class is not ResetClass.SYNTHETIC_DELETE:
            continue
        for raw in decision.paths:
            target = (profile_root / raw).resolve()
            if target.is_file():
                target.unlink()
                removed_files += 1
                cursor = target.parent
                while cursor != profile_root and cursor.exists() and not any(cursor.iterdir()):
                    cursor.rmdir()
                    cursor = cursor.parent
            elif target.is_dir():
                shutil.rmtree(target)
                removed_files += 1

    ledger["runs"] = kept_runs
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "profile_id": plan.profile_id,
        "removed_runs": removed_runs,
        "removed_artifacts": removed_files,
        "preserved_runs": len(kept_runs),
    }
