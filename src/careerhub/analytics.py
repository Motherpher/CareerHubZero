from __future__ import annotations

from collections import Counter, defaultdict

INTERVIEW_STAGES = {"interview_1", "interview_2", "interview_3", "interview_4", "interview_5", "interview_deep"}
POSITIVE_STAGES = {"qualified_contact", *INTERVIEW_STAGES, "case_or_test", "references", "offer", "assignment"}


def market_response(events: list[dict]) -> dict:
    by_stage = Counter(e.get("stage") for e in events if e.get("stage"))
    by_surface = defaultdict(Counter)
    by_lane = defaultdict(Counter)
    inbound = outbound = 0
    for event in events:
        stage = event.get("stage")
        if event.get("surface_id"):
            by_surface[event["surface_id"]][stage] += 1
        if event.get("lane_id"):
            by_lane[event["lane_id"]][stage] += 1
        if event.get("direction") == "inbound":
            inbound += 1
        elif event.get("direction") == "outbound":
            outbound += 1
    return {
        "event_count": len(events),
        "by_stage": dict(by_stage),
        "by_surface": {k: dict(v) for k, v in by_surface.items()},
        "by_lane": {k: dict(v) for k, v in by_lane.items()},
        "qualified_response_count": sum(by_stage[s] for s in POSITIVE_STAGES),
        "interview_count": sum(by_stage[s] for s in INTERVIEW_STAGES),
        "offer_count": by_stage["offer"],
        "assignment_count": by_stage["assignment"],
        "inbound_count": inbound,
        "outbound_count": outbound,
    }
