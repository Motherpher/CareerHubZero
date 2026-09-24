from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from math import sqrt
from typing import Any

POSITIVE_WEIGHT = {
    "viewed": 0.1,
    "selected_hrdm": 0.5,
    "applied": 1.0,
    "contacted": 1.4,
    "test": 1.7,
    "interview": 2.2,
    "offer": 4.0,
}
NEGATIVE_WEIGHT = {
    "ignored": -0.15,
    "user_rejected": -0.4,
    "denied": -0.7,
    "withdrawn": -0.2,
}
DIMENSIONS = ("role_family", "function_family", "employer_type", "arrangement", "geography")


@dataclass(frozen=True)
class LearningSignal:
    dimension: str
    key: str
    score: float
    observations: int
    positive_events: int
    negative_events: int
    confidence: float
    provenance: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "key": self.key,
            "score": round(self.score, 4),
            "observations": self.observations,
            "positive_events": self.positive_events,
            "negative_events": self.negative_events,
            "confidence": round(self.confidence, 4),
            "provenance": list(self.provenance),
        }


def _event_weight(event_type: str) -> float:
    if event_type in POSITIVE_WEIGHT:
        return POSITIVE_WEIGHT[event_type]
    return NEGATIVE_WEIGHT.get(event_type, 0.0)


def _case_dimensions(case: dict) -> dict[str, str]:
    return {
        "role_family": str(case.get("role_family") or case.get("lane") or "").strip(),
        "function_family": str(case.get("function_family") or "").strip(),
        "employer_type": str(case.get("employer_type") or "").strip(),
        "arrangement": str(case.get("arrangement") or case.get("work_mode") or "").strip(),
        "geography": str(case.get("geography") or case.get("location") or "").strip(),
    }


def derive_learning_signals(cases_data: dict) -> dict:
    """Derive bounded search-hypothesis signals from the canonical case event stream.

    This function never accepts or returns a candidate profile and therefore cannot
    mutate verified candidate evidence. It only produces search-hypothesis weights.
    """
    buckets: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {"sum": 0.0, "obs": 0, "pos": 0, "neg": 0, "prov": []}
    )

    for case in cases_data.get("cases", []):
        dims = _case_dimensions(case)
        case_ref = str(case.get("job_id") or case.get("issue_number") or case.get("title") or "case")
        for event in list(case.get("history") or []):
            et = str(event.get("event_type") or "").strip()
            weight = _event_weight(et)
            if weight == 0:
                continue
            for dim, value in dims.items():
                if not value:
                    continue
                bucket = buckets[(dim, value)]
                bucket["sum"] += weight
                bucket["obs"] += 1
                bucket["pos"] += int(weight > 0)
                bucket["neg"] += int(weight < 0)
                bucket["prov"].append(f"{case_ref}:{et}:{event.get('at','')}")

    signals = []
    for (dimension, key), row in buckets.items():
        obs = int(row["obs"])
        confidence = min(1.0, sqrt(obs) / 4.0)
        raw = float(row["sum"]) / max(1, obs)
        shrunk = raw * confidence
        signals.append(
            LearningSignal(
                dimension=dimension,
                key=key,
                score=shrunk,
                observations=obs,
                positive_events=int(row["pos"]),
                negative_events=int(row["neg"]),
                confidence=confidence,
                provenance=tuple(row["prov"]),
            ).as_dict()
        )

    signals.sort(key=lambda x: (-x["confidence"], -x["score"], x["dimension"], x["key"]))
    return {
        "schema_version": "1.0",
        "policy": {
            "scope": "search_hypotheses_only",
            "candidate_evidence_mutation": False,
            "small_sample_shrinkage": True,
        },
        "signals": signals,
    }


def signal_index(learning: dict) -> dict[tuple[str, str], dict]:
    return {
        (str(x.get("dimension")), str(x.get("key"))): x
        for x in learning.get("signals", [])
    }


def apply_learning_to_jobs(jobs: list[dict], learning: dict, max_adjustment: float = 10.0) -> list[dict]:
    """Apply learned market-response signals as a bounded ranking adjustment.

    The original triage score remains preserved in base_triage_score.
    """
    idx = signal_index(learning)
    result = []
    for job in jobs:
        row = deepcopy(job)
        dims = {
            "role_family": str(row.get("role_family") or row.get("lane") or "").strip(),
            "function_family": str(row.get("function_family") or "").strip(),
            "employer_type": str(row.get("employer_type") or "").strip(),
            "arrangement": str(row.get("arrangement") or row.get("work_mode") or "").strip(),
            "geography": str(row.get("geography") or row.get("location") or "").strip(),
        }
        contributions = []
        total = 0.0
        for dim, key in dims.items():
            if not key:
                continue
            signal = idx.get((dim, key))
            if not signal:
                continue
            contribution = float(signal.get("score") or 0.0) * 2.0
            total += contribution
            contributions.append({
                "dimension": dim,
                "key": key,
                "contribution": round(contribution, 4),
                "observations": signal.get("observations"),
                "confidence": signal.get("confidence"),
            })

        adjustment = max(-max_adjustment, min(max_adjustment, total))
        base = float(row.get("triage_score") or 0.0)
        row["base_triage_score"] = base
        row["learning_adjustment"] = round(adjustment, 2)
        row["learning_reasons"] = contributions
        row["triage_score"] = round(max(0.0, min(100.0, base + adjustment)), 1)
        result.append(row)

    result.sort(key=lambda x: (-float(x.get("triage_score") or 0.0), x.get("deadline") or "9999"))
    return result
