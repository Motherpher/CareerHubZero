from __future__ import annotations

from typing import Any


def _flatten_geo(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        if value.strip():
            out.append(value.strip())
    elif isinstance(value, list):
        for item in value:
            out.extend(_flatten_geo(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {"note", "notes"}:
                continue
            out.extend(_flatten_geo(item))
    return list(dict.fromkeys(out))


def lane_bucket(lane: dict) -> str:
    lane_id = str(lane.get("lane_id") or "").strip().lower()
    if lane_id in {"core", "adjacent", "bridge"}:
        return lane_id
    priority = lane.get("priority")
    if isinstance(priority, str):
        p = priority.strip().lower()
        if p == "core":
            return "core"
        if p in {"adjacent", "experimental"}:
            return "adjacent" if p == "adjacent" else "bridge"
    try:
        p = int(priority)
        return "core" if p <= 1 else "adjacent" if p == 2 else "bridge"
    except (TypeError, ValueError):
        return "core"


def normalize_search(search: dict) -> dict:
    """Normalize all supported 2.x search-profile shapes into one runtime contract."""
    geographies = search.get("geographies") or {}
    geo_terms = _flatten_geo(geographies)

    country = "SE"
    raw_country = geographies.get("country") if isinstance(geographies, dict) else None
    if raw_country:
        country = str(raw_country).upper()
    elif not any(x.lower() in {"sweden", "sverige", "sweden-wide"} for x in geo_terms):
        # Current source set is Sweden-first. Country adapters will replace this
        # fallback when the global geography runtime is complete.
        country = "SE"

    location = ""
    if isinstance(geographies, dict):
        location = str(geographies.get("location") or "").strip()
        primary = geographies.get("primary")
        if not location and isinstance(primary, list) and primary:
            first = str(primary[0]).strip()
            if first.lower() not in {"sweden", "sverige", "sweden-wide"}:
                location = first

    raw_lanes = search.get("lanes") or []
    normalized_lanes: list[dict] = []
    if isinstance(raw_lanes, dict):
        for lane_id, lane in raw_lanes.items():
            row = dict(lane or {})
            row["lane_id"] = lane_id
            row["bucket"] = lane_id if lane_id in {"core", "adjacent", "bridge"} else lane_bucket(row)
            row["queries"] = list(row.get("queries") or row.get("titles") or [])
            normalized_lanes.append(row)
    elif isinstance(raw_lanes, list):
        for lane in raw_lanes:
            row = dict(lane or {})
            row["bucket"] = lane_bucket(row)
            row["queries"] = list(row.get("queries") or row.get("titles") or [])
            normalized_lanes.append(row)

    overlay = search.get("user_search_overlay") or {}
    return {
        "country": country,
        "location": location,
        "target_geographies": geo_terms,
        "remote_allowed": bool(geographies.get("remote_allowed", True)) if isinstance(geographies, dict) else True,
        "max_per_query": int(search.get("max_per_query") or 20),
        "max_total": int(search.get("max_total") or 120),
        "lanes": normalized_lanes,
        "search_overlay": str(overlay.get("specific_wishes_or_needs") or "").strip(),
        "intent": str(search.get("intent") or ""),
        "negative_filters": list(search.get("negative_filters") or []),
        "triage_rule": str(search.get("triage_rule") or ""),
    }


def lane_queries(lane: dict, verified_candidate_terms: list[str], overlay: str) -> list[str]:
    queries = [str(x).strip() for x in lane.get("queries") or [] if str(x).strip()]
    if lane.get("bucket") == "core":
        # Verified evidence broadens discovery but never creates candidate claims.
        queries.extend(str(x).strip() for x in verified_candidate_terms[:12] if str(x).strip())
    if overlay:
        queries.append(overlay)
    return list(dict.fromkeys(queries))
