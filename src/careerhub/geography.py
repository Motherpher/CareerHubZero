from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Callable

import requests


PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

PRECISION_RANK = {
    "unknown": 0,
    "country": 1,
    "admin1": 2,
    "admin2": 3,
    "locality": 4,
    "district": 5,
    "postal_code": 6,
    "street": 7,
    "premise": 8,
    "source_coordinates": 9,
}

POINT_PRECISIONS = {"street", "premise", "source_coordinates"}


class GeographyError(RuntimeError):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _valid_coordinates(lat: Any, lng: Any) -> bool:
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        return False
    return -90 <= lat_f <= 90 and -180 <= lng_f <= 180


def _source_coordinates(job: dict) -> tuple[float, float] | None:
    candidates = [
        (job.get("latitude"), job.get("longitude")),
        (job.get("lat"), job.get("lng")),
    ]
    coords = job.get("coordinates")
    if isinstance(coords, dict):
        candidates.append((coords.get("lat") or coords.get("latitude"), coords.get("lng") or coords.get("longitude")))
    for lat, lng in candidates:
        if _valid_coordinates(lat, lng):
            return float(lat), float(lng)
    return None


def location_query(job: dict, allow_company_place_fallback: bool = False) -> tuple[str, str]:
    """Return the strongest location query already supported by the vacancy.

    Never invent a street address. Company + locality lookup is disabled by default
    because an employer may have several offices.
    """
    for field in ("workplace_address", "street_address", "address"):
        value = _clean(job.get(field))
        if value:
            return value, field

    location = _clean(job.get("location"))
    if allow_company_place_fallback and location and _clean(job.get("company")):
        return f"{_clean(job.get('company'))}, {location}", "company+location"
    if location:
        return location, "location"

    city = _clean(job.get("city"))
    if city:
        return city, "city"
    return "", "none"


def _component(place: dict, wanted: str) -> tuple[str | None, str | None]:
    for item in place.get("addressComponents", []) or []:
        types = set(item.get("types", []) or [])
        if wanted in types:
            return item.get("longText"), item.get("shortText")
    return None, None


def classify_precision(place_types: list[str] | None) -> str:
    types = set(place_types or [])
    if types & {"street_address", "premise", "subpremise", "establishment", "point_of_interest"}:
        return "premise"
    if "route" in types:
        return "street"
    if "postal_code" in types:
        return "postal_code"
    if types & {"neighborhood", "sublocality", "sublocality_level_1", "sublocality_level_2"}:
        return "district"
    if types & {"locality", "postal_town"}:
        return "locality"
    if "administrative_area_level_2" in types:
        return "admin2"
    if "administrative_area_level_1" in types:
        return "admin1"
    if "country" in types:
        return "country"
    return "unknown"


def confidence_for_precision(precision: str) -> float:
    return {
        "source_coordinates": 1.00,
        "premise": 0.95,
        "street": 0.90,
        "postal_code": 0.82,
        "district": 0.78,
        "locality": 0.72,
        "admin2": 0.65,
        "admin1": 0.55,
        "country": 0.45,
        "unknown": 0.20,
    }.get(precision, 0.20)


class GooglePlacesGeocoder:
    """Small adapter around Google Places API (New) Text Search.

    Keep the requested field mask narrow: this is a geotagging operation, not
    a general place-data lookup.
    """

    def __init__(self, api_key: str, timeout: int = 15):
        if not api_key:
            raise GeographyError("GOOGLE_MAPS_API_KEY is required")
        self.api_key = api_key
        self.timeout = timeout

    def search(self, query: str, region_code: str | None = None) -> dict | None:
        body: dict[str, Any] = {"textQuery": query, "pageSize": 1}
        if region_code:
            body["regionCode"] = region_code.upper()
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,"
                "places.location,places.addressComponents,places.types"
            ),
        }
        response = requests.post(PLACES_TEXT_SEARCH_URL, json=body, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        places = response.json().get("places", [])
        return places[0] if places else None


def normalize_google_place(place: dict, query: str, basis: str) -> dict:
    location = place.get("location") or {}
    lat = location.get("latitude")
    lng = location.get("longitude")
    if not _valid_coordinates(lat, lng):
        raise GeographyError("Google place result does not contain valid coordinates")

    country_name, country_code = _component(place, "country")
    admin1_name, admin1_code = _component(place, "administrative_area_level_1")
    admin2_name, admin2_code = _component(place, "administrative_area_level_2")
    locality, _ = _component(place, "locality")
    if not locality:
        locality, _ = _component(place, "postal_town")
    district, _ = _component(place, "sublocality_level_1")
    if not district:
        district, _ = _component(place, "neighborhood")
    postal_code, _ = _component(place, "postal_code")

    precision = classify_precision(place.get("types"))
    display = place.get("displayName")
    if isinstance(display, dict):
        display = display.get("text")

    return {
        "status": "tagged",
        "provider": "google_places_new",
        "place_id": place.get("id"),
        "source_query": query,
        "location_basis": basis,
        "formatted_address": place.get("formattedAddress"),
        "display_name": display,
        "point": {"lat": float(lat), "lng": float(lng)},
        "precision": precision,
        "confidence": confidence_for_precision(precision),
        "scope": "point" if precision in POINT_PRECISIONS else "area",
        "hierarchy": {
            "country": country_name,
            "country_code": country_code,
            "admin1": admin1_name,
            "admin1_code": admin1_code,
            "admin2": admin2_name,
            "admin2_code": admin2_code,
            "locality": locality,
            "district": district,
            "postal_code": postal_code,
        },
        "country_matrix": {},
        "tagged_at": utc_now_iso(),
    }


def geotag_job(
    job: dict,
    geocoder: Any,
    *,
    region_code: str | None = None,
    allow_company_place_fallback: bool = False,
    country_enricher: Callable[[dict], dict] | None = None,
) -> dict:
    """Return a copy of a job with a normalized geo tag.

    Source-native coordinates win. Otherwise the strongest stated location is
    geocoded. Remote work remains a work-setting property and is not used to
    erase a stated geographic eligibility/workplace area.
    """
    result = deepcopy(job)
    existing = result.get("geo")
    if isinstance(existing, dict) and existing.get("status") == "tagged":
        return result

    coords = _source_coordinates(result)
    if coords:
        lat, lng = coords
        geo = {
            "status": "tagged",
            "provider": "source",
            "place_id": None,
            "source_query": None,
            "location_basis": "source_coordinates",
            "formatted_address": _clean(result.get("location")) or None,
            "display_name": _clean(result.get("location")) or None,
            "point": {"lat": lat, "lng": lng},
            "precision": "source_coordinates",
            "confidence": 1.0,
            "scope": "point",
            "hierarchy": {},
            "country_matrix": {},
            "tagged_at": utc_now_iso(),
        }
    else:
        query, basis = location_query(result, allow_company_place_fallback)
        if not query:
            result["geo"] = {
                "status": "remote" if _clean(result.get("work_mode")).lower() == "remote" else "unknown",
                "provider": None,
                "point": None,
                "precision": "unknown",
                "confidence": 0.0,
                "scope": "remote" if _clean(result.get("work_mode")).lower() == "remote" else "unknown",
                "hierarchy": {},
                "country_matrix": {},
                "tagged_at": utc_now_iso(),
            }
            return result
        place = geocoder.search(query, region_code=region_code)
        if not place:
            result["geo"] = {
                "status": "unresolved",
                "provider": "google_places_new",
                "source_query": query,
                "location_basis": basis,
                "point": None,
                "precision": "unknown",
                "confidence": 0.0,
                "scope": "unknown",
                "hierarchy": {},
                "country_matrix": {},
                "tagged_at": utc_now_iso(),
            }
            return result
        geo = normalize_google_place(place, query, basis)

    geo["work_setting"] = _clean(result.get("work_mode")) or None
    if country_enricher:
        enrichment = country_enricher(deepcopy(geo))
        if enrichment:
            geo["country_matrix"] = enrichment
    result["geo"] = geo
    return result


def geotag_vault(
    vault: dict,
    geocoder: Any,
    *,
    region_code: str | None = None,
    only_missing: bool = True,
    allow_company_place_fallback: bool = False,
    country_enricher: Callable[[dict], dict] | None = None,
) -> dict:
    result = deepcopy(vault)
    tagged_jobs = []
    for job in result.get("jobs", []):
        if only_missing and isinstance(job.get("geo"), dict) and job["geo"].get("status") == "tagged":
            tagged_jobs.append(job)
            continue
        tagged_jobs.append(
            geotag_job(
                job,
                geocoder,
                region_code=region_code,
                allow_company_place_fallback=allow_company_place_fallback,
                country_enricher=country_enricher,
            )
        )
    result["jobs"] = tagged_jobs
    result["geo_updated_at"] = utc_now_iso()
    return result


def is_newly_sourced(job: dict) -> bool:
    if not job.get("in_latest_scan"):
        return False
    try:
        return int(job.get("scan_count", 0)) <= 1
    except (TypeError, ValueError):
        return False


def _bucket_key(job: dict, level: str) -> tuple[str, str] | None:
    geo = job.get("geo") or {}
    hierarchy = geo.get("hierarchy") or {}
    if level == "country":
        code = hierarchy.get("country_code")
        label = hierarchy.get("country")
    elif level == "admin1":
        code = hierarchy.get("admin1_code") or hierarchy.get("admin1")
        label = hierarchy.get("admin1")
    else:
        code = hierarchy.get("locality")
        label = hierarchy.get("locality")
    if not label:
        return None
    return str(code or label), str(label)


def _centroid(items: list[dict]) -> dict | None:
    points = [(j.get("geo") or {}).get("point") for j in items]
    points = [p for p in points if isinstance(p, dict) and _valid_coordinates(p.get("lat"), p.get("lng"))]
    if not points:
        return None
    return {
        "lat": sum(float(p["lat"]) for p in points) / len(points),
        "lng": sum(float(p["lng"]) for p in points) / len(points),
    }


def aggregate_level(jobs: list[dict], level: str) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for job in jobs:
        key = _bucket_key(job, level)
        if key:
            grouped[key].append(job)

    clusters = []
    for (key, label), items in grouped.items():
        clusters.append(
            {
                "key": key,
                "label": label,
                "level": level,
                "count": len(items),
                "new_count": sum(1 for j in items if is_newly_sourced(j)),
                "point": _centroid(items),
                "job_ids": [j.get("id") for j in items if j.get("id")],
            }
        )
    return sorted(clusters, key=lambda x: (-x["count"], x["label"]))


def point_feature(job: dict) -> dict | None:
    geo = job.get("geo") or {}
    point = geo.get("point")
    if not isinstance(point, dict) or not _valid_coordinates(point.get("lat"), point.get("lng")):
        return None
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [float(point["lng"]), float(point["lat"])],
        },
        "properties": {
            "job_id": job.get("id"),
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "precision": geo.get("precision"),
            "confidence": geo.get("confidence"),
            "new": is_newly_sourced(job),
            "url": job.get("url"),
        },
    }


def build_map_payload(jobs: list[dict], zoom: float) -> dict:
    """Build a zoom-aware map payload.

    Low zoom uses administrative buckets. At street/city zoom, genuinely precise
    jobs become individual points while coarse locality-only jobs remain grouped.
    This prevents false street-level precision.
    """
    tagged = [j for j in jobs if (j.get("geo") or {}).get("status") == "tagged"]

    if zoom < 4:
        return {"mode": "aggregate", "level": "country", "clusters": aggregate_level(tagged, "country"), "points": []}
    if zoom < 7:
        return {"mode": "aggregate", "level": "admin1", "clusters": aggregate_level(tagged, "admin1"), "points": []}
    if zoom < 10:
        return {"mode": "aggregate", "level": "locality", "clusters": aggregate_level(tagged, "locality"), "points": []}

    precise = []
    coarse = []
    for job in tagged:
        precision = (job.get("geo") or {}).get("precision", "unknown")
        if precision in POINT_PRECISIONS:
            feature = point_feature(job)
            if feature:
                precise.append(feature)
        else:
            coarse.append(job)

    return {
        "mode": "mixed",
        "level": "point+locality",
        "clusters": aggregate_level(coarse, "locality"),
        "points": precise,
    }
