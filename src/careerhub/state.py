from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dateutil import parser as dtparser

from .models import Job


TERMINAL_STATUSES = {"offer", "denied", "withdrawn", "archived"}
APPLIED_STATUSES = {
    "applied", "contacted", "portfolio", "interview_1", "interview_2",
    "interview_3", "interview_4", "interview_5", "meeting_1", "meeting_2",
    "meeting_3", "meeting_4", "meeting_5", "offer", "denied",
}
STATUS_LABELS = {
    "saved": "Valt",
    "preparing": "Förbereds",
    "ready": "Redo att söka",
    "applied": "Ansökan skickad",
    "contacted": "Kontakt",
    "portfolio": "Arbetsprov / test",
    "interview_1": "Intervju 1",
    "interview_2": "Intervju 2",
    "interview_3": "Intervju 3",
    "interview_4": "Intervju 4",
    "interview_5": "Intervju 5",
    "meeting_1": "Möte 1",
    "meeting_2": "Möte 2",
    "meeting_3": "Möte 3",
    "meeting_4": "Möte 4",
    "meeting_5": "Möte 5",
    "offer": "Erbjudande",
    "denied": "Avslutad",
    "withdrawn": "Avstår",
    "archived": "Arkiverad",
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _deadline_state(value: str) -> tuple[str, int | None]:
    if not value:
        return "unknown", None
    try:
        d = dtparser.parse(str(value))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        days = (d.date() - datetime.now(timezone.utc).date()).days
        if days < 0:
            return "expired", days
        if days <= 3:
            return "urgent", days
        if days <= 7:
            return "soon", days
        return "open", days
    except Exception:
        return "unknown", None


def merge_job_vault(path: Path, jobs: list[Job]) -> dict:
    now = utcnow()
    vault = read_json(path, {"schema_version": "1.0", "updated_at": None, "jobs": []})
    existing = {j.get("id"): j for j in vault.get("jobs", []) if j.get("id")}
    current_ids = set()

    for job in jobs:
        data = job.public_dict()
        jid = data["id"]
        current_ids.add(jid)
        old = existing.get(jid, {})
        state, days = _deadline_state(data.get("deadline", ""))
        record = {
            **old,
            **data,
            "first_seen": old.get("first_seen") or now,
            "last_seen": now,
            "scan_count": int(old.get("scan_count") or 0) + 1,
            "in_latest_scan": True,
            "deadline_state": state,
            "days_to_deadline": days,
        }
        existing[jid] = record

    for jid, record in existing.items():
        if jid not in current_ids:
            record["in_latest_scan"] = False
            state, days = _deadline_state(record.get("deadline", ""))
            record["deadline_state"] = state if state != "open" else "historic"
            record["days_to_deadline"] = days

    records = list(existing.values())
    records.sort(key=lambda x: (
        not bool(x.get("in_latest_scan")),
        -(float(x.get("triage_score") or 0)),
        x.get("deadline") or "9999",
    ))
    payload = {
        "schema_version": "1.0",
        "updated_at": now,
        "total_jobs_ever_seen": len(records),
        "current_jobs": sum(1 for x in records if x.get("in_latest_scan")),
        "jobs": records,
    }
    write_json(path, payload)
    return payload


def load_cases(path: Path) -> dict:
    return read_json(path, {"schema_version": "1.0", "updated_at": None, "cases": []})


def save_cases(path: Path, data: dict):
    data["updated_at"] = utcnow()
    write_json(path, data)


def choose_case(
    path: Path,
    job: Job,
    issue_number: int,
    issue_url: str,
    priority: int = 3,
) -> dict:
    data = load_cases(path)
    now = utcnow()
    priority = max(1, min(5, int(priority or 3)))
    cases = data.setdefault("cases", [])
    existing = next((c for c in cases if c.get("issue_number") == issue_number), None)
    if existing is None:
        existing = next((c for c in cases if c.get("job_id") == job.id and c.get("status") not in TERMINAL_STATUSES), None)

    entry = {
        "job_id": job.id,
        "issue_number": issue_number,
        "issue_url": issue_url,
        "title": job.title,
        "company": job.company,
        "url": job.url,
        "lane": job.lane,
        "deadline": job.deadline,
        "location": job.location,
        "priority": priority,
        "status": "ready",
        "chosen_at": now,
        "status_updated_at": now,
        "next_action": "Läs ansökningsunderlaget och sök när du vill",
        "next_action_date": job.deadline or "",
        "notification_log": [],
        "history": [
            {"at": now, "status": "saved", "event": "Jobbet analyserades"},
            {"at": now, "status": "ready", "event": "Ansökningsunderlaget är klart"},
        ],
    }
    if existing:
        keep_history = existing.get("history", [])
        keep_log = existing.get("notification_log", [])
        existing.update(entry)
        existing["history"] = keep_history or entry["history"]
        existing["notification_log"] = keep_log
        result = existing
    else:
        cases.append(entry)
        result = entry

    save_cases(path, data)
    return result


def update_case(
    path: Path,
    issue_number: int,
    status: str,
    event_date: str = "",
    next_action: str = "",
    next_action_date: str = "",
) -> dict:
    data = load_cases(path)
    case = next((c for c in data.get("cases", []) if int(c.get("issue_number") or 0) == int(issue_number)), None)
    if not case:
        raise ValueError(f"CareerHub case issue #{issue_number} was not found.")

    now = utcnow()
    status = status.strip().lower()
    if status not in STATUS_LABELS:
        raise ValueError(f"Unknown CareerHub status: {status}")

    case["status"] = status
    case["status_updated_at"] = now
    if status == "applied" and not case.get("applied_at"):
        case["applied_at"] = event_date or now
    if next_action:
        case["next_action"] = next_action
    else:
        case["next_action"] = default_next_action(status)
    if next_action_date:
        case["next_action_date"] = next_action_date
    case.setdefault("history", []).append({
        "at": event_date or now,
        "status": status,
        "event": STATUS_LABELS[status],
    })
    save_cases(path, data)
    return case


def update_priority(path: Path, issue_number: int, priority: int) -> dict:
    data = load_cases(path)
    case = next((c for c in data.get("cases", []) if int(c.get("issue_number") or 0) == int(issue_number)), None)
    if not case:
        raise ValueError(f"CareerHub case issue #{issue_number} was not found.")
    case["priority"] = max(1, min(5, int(priority)))
    case["status_updated_at"] = utcnow()
    save_cases(path, data)
    return case


def default_next_action(status: str) -> str:
    return {
        "saved": "Förbered ansökan",
        "preparing": "Slutför ansökningsunderlaget",
        "ready": "Sök när du vill",
        "applied": "Avvakta eller följ upp",
        "contacted": "Förbered nästa kontakt",
        "portfolio": "Genomför arbetsprov eller test",
        "interview_1": "Förbered nästa intervju eller uppföljning",
        "interview_2": "Förbered nästa intervju eller uppföljning",
        "interview_3": "Förbered nästa steg",
        "interview_4": "Förbered nästa steg",
        "interview_5": "Avvakta beslut eller följ upp",
        "meeting_1": "Förbered nästa möte eller uppföljning",
        "meeting_2": "Förbered nästa möte eller uppföljning",
        "meeting_3": "Förbered nästa steg",
        "meeting_4": "Förbered nästa steg",
        "meeting_5": "Avvakta beslut eller följ upp",
        "offer": "Gå igenom erbjudandet",
        "denied": "Avsluta och spara det du vill ta med dig",
        "withdrawn": "Avsluta",
        "archived": "Ingen åtgärd",
    }.get(status, "")


def case_counts(data: dict) -> dict:
    cases = data.get("cases", [])
    return {
        "chosen": sum(1 for c in cases if c.get("status") not in TERMINAL_STATUSES),
        "applied": sum(1 for c in cases if c.get("status") in APPLIED_STATUSES and c.get("status") not in TERMINAL_STATUSES),
        "interviews": sum(1 for c in cases if str(c.get("status", "")).startswith(("interview_", "meeting_"))),
        "offers": sum(1 for c in cases if c.get("status") == "offer"),
    }


def rank_label(priority: int) -> str:
    return {5: "Sök", 4: "Mycket intressant", 3: "Intressant", 2: "Svagare träff", 1: "Avvakta"}.get(int(priority or 3), "Intressant")
