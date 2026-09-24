from __future__ import annotations

import json
import re
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None

PROCESS_ID_RE = re.compile(
    r"^HRDM-(?:F|R)-\d{8}-\d{4}-S\d{2}-[A-Z0-9]+-R\d{2}-(?:OPEN|PASS|WARN|FAIL|LOOP|LOCK|FINAL|VOID|REDO)$"
)

STATES = {"OPEN", "PASS", "WARN", "FAIL", "LOOP", "LOCK", "FINAL", "VOID", "REDO"}


def validate_process_id(pid: str) -> bool:
    return bool(PROCESS_ID_RE.fullmatch(str(pid or "")))


def generate_process_id(
    *,
    mode: str,
    rundate: str,
    runseq: int,
    step: int,
    sub: str = "A",
    rev: int = 1,
    state: str,
) -> str:
    mode = mode.upper()
    state = state.upper()
    sub = re.sub(r"[^A-Z0-9]", "", sub.upper()) or "A"
    if mode not in {"F", "R"}:
        raise ValueError("mode must be F or R")
    if not re.fullmatch(r"\d{8}", rundate):
        raise ValueError("rundate must be YYYYMMDD")
    if state not in STATES:
        raise ValueError(f"invalid HRDM state: {state}")
    pid = f"HRDM-{mode}-{rundate}-{int(runseq):04d}-S{int(step):02d}-{sub}-R{int(rev):02d}-{state}"
    if not validate_process_id(pid):
        raise ValueError(f"generated invalid Process-ID: {pid}")
    return pid


@contextmanager
def _locked_file(path: Path) -> Iterator[object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            handle.seek(0)
            yield handle
        finally:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def allocate_run_sequence(counter_path: Path, rundate: str) -> int:
    """Allocate the daily HRDM RUNSEQ.

    GitHub workflows also serialize state writes, but the file lock makes local/
    self-hosted execution safe within one filesystem.
    """
    with _locked_file(counter_path) as handle:
        raw = handle.read().strip()
        try:
            counters = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            counters = {}
        seq = int(counters.get(rundate, 0)) + 1
        counters[rundate] = seq
        handle.seek(0)
        handle.truncate()
        json.dump(counters, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
    return seq


def create_reverse_trace(
    *,
    counter_path: Path,
    hy_filter_usage: bool,
    warnings: list[str] | None = None,
    environment: str = "Standalone",
    piusite_usage: bool = False,
    hcc_authority: str = "HCC-Lite",
) -> dict:
    now = datetime.now(timezone.utc)
    rundate = now.strftime("%Y%m%d")
    runseq = allocate_run_sequence(counter_path, rundate)
    step_pids = {}
    for step in range(1, 9):
        step_pids[f"S{step:02d}"] = generate_process_id(
            mode="R", rundate=rundate, runseq=runseq, step=step, state="LOCK"
        )
    step_pids["S09"] = generate_process_id(
        mode="R", rundate=rundate, runseq=runseq, step=9, state="OPEN"
    )
    final_pid = step_pids["S09"]
    return {
        "run_id": str(uuid.uuid4()),
        "mode": "R",
        "timestamp": now.isoformat(),
        "environment": environment,
        "piusite_usage": bool(piusite_usage),
        "hy_filter_usage": bool(hy_filter_usage),
        "hcc_authority": hcc_authority,
        "downing_street_loop_count": 0,
        "final_output_state": "OPEN",
        "process_id_validation_status": all(validate_process_id(x) for x in step_pids.values()),
        "last_pid_rev": final_pid,
        "process_id": final_pid,
        "runseq": runseq,
        "step_process_ids": step_pids,
        "outstanding_warnings": list(warnings or []),
        "bank_eligible_outputs": [],
    }


def finalize_reverse_trace(
    trace: dict,
    *,
    success: bool,
    warnings: list[str] | None = None,
) -> dict:
    """Finalize the S09 state after semantic execution has actually completed."""
    result = dict(trace)
    current = str(result.get("process_id") or "")
    parts = current.split("-")
    if len(parts) != 8:
        raise ValueError(f"Cannot finalize malformed Process-ID: {current}")
    _, mode, rundate, runseq, step_token, sub, rev_token, _ = parts
    state = "FINAL" if success else "WARN"
    final_pid = generate_process_id(
        mode=mode,
        rundate=rundate,
        runseq=int(runseq),
        step=int(step_token.lstrip("S")),
        sub=sub,
        rev=int(rev_token.lstrip("R")),
        state=state,
    )
    step_ids = dict(result.get("step_process_ids") or {})
    step_ids["S09"] = final_pid
    result["step_process_ids"] = step_ids
    result["process_id"] = final_pid
    result["last_pid_rev"] = final_pid
    result["final_output_state"] = state
    result["process_id_validation_status"] = all(validate_process_id(x) for x in step_ids.values())
    result["outstanding_warnings"] = list(warnings or [])
    result["bank_eligible_outputs"] = (
        [
            "Final deconstructed ad map",
            "Final candidate positioning map",
            "Final DoD flagged meta-report",
            "Final HCC commentary",
        ]
        if success else []
    )
    return result
