from __future__ import annotations

from collections import defaultdict
from typing import Any

POSITIVE = {
    "viewed": 0.15,
    "selected_hrdm": 0.35,
    "applied": 0.55,
    "contacted": 0.75,
    "test": 0.95,
    "interview": 1.20,
    "offer": 1.60,
}
NEGATIVE = {
    "ignored": -0.10,
    "user_rejected": -0.30,
    "denied": -0.45,
    "withdrawn": -0.20,
}
EVENT_WEIGHT = {**POSITIVE, **NEGATIVE}

DIMENSIONS = ("role_family", "employer_type", "geography_key", "search_lane")


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def collect_outcome_events(cases_data: dict) -> list[dict]:
    """Project the canonical case histories into learning events.

    Case history remains the stored truth. This function creates an in-memory
    learning projection and does not mutate candidate evidence.
    """
    events: list[dict] = []
    for case in cases_data.get("cases", []):
        context = {
            "job_id": str(case.get("job_id") or ""),
            "role_family": _norm(case.get("role_family") or case.get("title")),
            "employer_type": _norm(case.get("employer_type")),
            "geography_key": _norm(case.get("geography_key") or case.get("location")),
            "search_lane": _norm(case.get("lane")),
        }
        for row in case.get("history", []):
            event_type = _event_type(row.get("event_type") or row.get("status"))
            if not event_type:
                continue
            events.append({
                "at": row.get("at"),
                "event_type": event_type,
                "source": row.get("source") or ("employer" if event_type in {"contacted","test","interview","offer","denied"} else "user"),
                **context,
            })
    return events


def _event_type(value: Any) -> str | None:
    v = _norm(value)
    mapping = {
        "saved": "selected_hrdm",
        "preparing": "selected_hrdm",
        "ready": "selected_hrdm",
        "applied": "applied",
        "contacted": "contacted",
        "portfolio": "test",
        "interview_1": "interview",
        "interview_2": "interview",
        "interview_3": "interview",
        "interview_4": "interview",
        "interview_5": "interview",
        "meeting_1": "interview",
        "meeting_2": "interview",
        "meeting_3": "interview",
        "meeting_4": "interview",
        "meeting_5": "interview",
        "offer": "offer",
        "denied": "denied",
        "withdrawn": "withdrawn",
        "archived": "archived",
        "user_rejected": "user_rejected",
        "ignored": "ignored",
        "viewed": "viewed",
    }
    return mapping.get(v)


def derive_hypotheses(events: list[dict]) -> dict:
    """Return explainable, bounded search hypotheses from outcome history."""
    buckets: dict[str, dict[str, list[float]]] = {
        dim: defaultdict(list) for dim in DIMENSIONS
    }
    for event in events:
        weight = EVENT_WEIGHT.get(event.get("event_type"))
        if weight is None:
            continue
        for dim in DIMENSIONS:
            key = _norm(event.get(dim))
            if key:
                buckets[dim][key].append(weight)

    result = {"schema_version": "1.0", "dimensions": {}, "event_count": len(events)}
    for dim, values in buckets.items():
        rows = {}
        for key, weights in values.items():
            n = len(weights)
            raw = sum(weights)
            # Conservative shrinkage: small samples remain weak.
            confidence = round(n / (n + 5.0), 4)
            score = round((raw / max(1, n)) * confidence, 4)
            rows[key] = {
                "score": max(-1.0, min(1.0, score)),
                "sample_size": n,
                "confidence": confidence,
                "provenance": {"events": n, "weighted_sum": round(raw, 4)},
            }
        result["dimensions"][dim] = rows
    return result


def learning_bonus(job: Any, hypotheses: dict) -> tuple[float, list[str]]:
    """Project learning into ranking only. Never changes candidate evidence."""
    dims = hypotheses.get("dimensions", {})
    candidates = {
        "role_family": _norm((getattr(job, "provider_meta", {}) or {}).get("role_family") or getattr(job, "title", "")),
        "employer_type": _norm((getattr(job, "provider_meta", {}) or {}).get("employer_type")),
        "geography_key": _norm((getattr(job, "provider_meta", {}) or {}).get("geography_key") or getattr(job, "location", "")),
        "search_lane": _norm((getattr(job, "provider_meta", {}) or {}).get("search_lane_id") or getattr(job, "lane", "")),
    }
    score = 0.0
    reasons = []
    for dim, key in candidates.items():
        if not key:
            continue
        row = (dims.get(dim) or {}).get(key)
        if not row:
            continue
        contribution = float(row.get("score") or 0) * 8.0
        score += contribution
        reasons.append(
            f"learning:{dim}={key} {contribution:+.2f} "
            f"(n={row.get('sample_size')}, conf={row.get('confidence')})"
        )
    return max(-8.0, min(8.0, score)), reasons
