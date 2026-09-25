#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from typing import Any

import requests

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
ROUTES_URL = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


def emit(name: str, status: str, **extra: Any) -> dict:
    row = {"gate": name, "status": status, **extra}
    print(json.dumps(row, ensure_ascii=False))
    return row


def google_place(key: str, query: str) -> dict:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.location,places.formattedAddress",
    }
    body = {"textQuery": query, "pageSize": 1, "regionCode": "SE"}
    r = requests.post(PLACES_URL, headers=headers, json=body, timeout=20)
    if r.status_code != 200:
        try:
            detail = r.json().get("error", {})
        except Exception:
            detail = {"message": r.text[:500]}
        raise RuntimeError(f"Places HTTP {r.status_code}: {detail.get('status') or detail.get('message')}")
    rows = r.json().get("places") or []
    if not rows:
        raise RuntimeError("Places returned no result")
    return rows[0]


def probe_google_maps() -> dict:
    key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        return emit("E02", "BLOCKED_MISSING_SECRET", secret="GOOGLE_MAPS_API_KEY")

    try:
        origin = google_place(key, "Stockholm Centralstation")
        destination = google_place(key, "Uppsala Centralstation")
        op = origin["location"]
        dp = destination["location"]
        body = {
            "origins": [{"waypoint": {"location": {"latLng": {"latitude": op["latitude"], "longitude": op["longitude"]}}}}],
            "destinations": [{"waypoint": {"location": {"latLng": {"latitude": dp["latitude"], "longitude": dp["longitude"]}}}}],
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "units": "METRIC",
            "regionCode": "SE",
        }
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": "originIndex,destinationIndex,status,condition,distanceMeters,duration",
        }
        r = requests.post(ROUTES_URL, headers=headers, json=body, timeout=30)
        if r.status_code != 200:
            try:
                detail = r.json().get("error", {})
            except Exception:
                detail = {"message": r.text[:500]}
            return emit(
                "E02",
                "BLOCKED_LIVE_API",
                stage="routes",
                http_status=r.status_code,
                provider_status=detail.get("status"),
                message=str(detail.get("message") or "")[:300],
            )
        rows = r.json() if isinstance(r.json(), list) else []
        if not rows:
            return emit("E02", "BLOCKED_LIVE_API", stage="routes", message="No route matrix rows")
        row = rows[0]
        status_code = int((row.get("status") or {}).get("code") or 0)
        if status_code != 0:
            return emit("E02", "BLOCKED_LIVE_API", stage="routes", route_status_code=status_code)
        return emit(
            "E02",
            "PASS",
            places="PASS",
            routes="PASS",
            sample_origin="Stockholm Centralstation",
            sample_destination="Uppsala Centralstation",
            distance_meters=row.get("distanceMeters"),
            duration=row.get("duration"),
        )
    except Exception as exc:
        return emit("E02", "BLOCKED_LIVE_API", stage="places_or_routes", error=f"{exc.__class__.__name__}: {str(exc)[:300]}")


def extract_output_text(payload: dict) -> str:
    chunks = []
    for item in payload.get("output") or []:
        for content in item.get("content") or []:
            if content.get("type") == "output_text" and content.get("text"):
                chunks.append(str(content["text"]))
    return "".join(chunks)


def probe_openai() -> dict:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return emit("E03", "BLOCKED_MISSING_SECRET", secret="OPENAI_API_KEY")

    model = os.getenv("CAREERHUB_MODEL", "").strip() or "gpt-5.6-sol"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "store": False,
        "input": "Return exactly CAREERHUB_GATE_OK",
        "max_output_tokens": 32,
    }
    try:
        r = requests.post(OPENAI_RESPONSES_URL, headers=headers, json=body, timeout=45)
        if r.status_code != 200:
            try:
                err = (r.json().get("error") or {})
            except Exception:
                err = {"message": r.text[:500]}
            return emit(
                "E03",
                "BLOCKED_LIVE_API",
                http_status=r.status_code,
                error_code=err.get("code"),
                error_type=err.get("type"),
                message=str(err.get("message") or "")[:300],
                model=model,
            )
        payload = r.json()
        text = extract_output_text(payload).strip()
        if "CAREERHUB_GATE_OK" not in text:
            return emit("E03", "BLOCKED_RESPONSE_MISMATCH", model=model, observed=text[:120])
        return emit("E03", "PASS", model=model, responses_api="PASS", observed="CAREERHUB_GATE_OK")
    except Exception as exc:
        return emit("E03", "BLOCKED_LIVE_API", error=f"{exc.__class__.__name__}: {str(exc)[:300]}", model=model)


def main() -> int:
    results = [probe_google_maps(), probe_openai()]
    print("CAREERHUB_EXTERNAL_GATES=" + json.dumps(results, ensure_ascii=False, separators=(",", ":")))
    return 0 if all(x["status"] == "PASS" for x in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
