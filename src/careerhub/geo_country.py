from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class CountryAdapterError(RuntimeError):
    pass


def load_country_registry(path: str | Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if data.get("schema_version") != "1.0":
        raise CountryAdapterError("Unsupported country registry schema")
    return data


def adapter_for(country_code: str, registry: dict) -> dict:
    code = str(country_code or "").upper()
    cfg = (registry.get("countries") or {}).get(code)
    if cfg:
        return dict(cfg)
    return {
        "status": "google_only",
        "adapter": None,
        "administrative_matrix": False,
        "functional_labour_market": False,
        "fine_statistical_areas": False,
    }


def enrich_geo(geo: dict, registry: dict, country_data: dict[str, Any] | None = None) -> dict:
    """Attach country-adapter metadata without replacing provider geography.

    Detailed country identifiers are accepted only from supplied authoritative
    country data; absence remains unknown rather than being inferred.
    """
    hierarchy = geo.get("hierarchy") or {}
    code = str(hierarchy.get("country_code") or "").upper()
    cfg = adapter_for(code, registry)
    result = {
        "country_code": code or None,
        "adapter": cfg.get("adapter"),
        "status": cfg.get("status"),
        "administrative_matrix": bool(cfg.get("administrative_matrix")),
        "functional_labour_market": bool(cfg.get("functional_labour_market")),
        "fine_statistical_areas": bool(cfg.get("fine_statistical_areas")),
        "source_authority": cfg.get("source_authority"),
        "source_urls": list(cfg.get("source_urls") or []),
        "county_code": None,
        "municipality_code": None,
        "regso_code": None,
        "deso_code": None,
        "labour_market_code": None,
    }
    if country_data:
        for key in ("county_code","municipality_code","regso_code","deso_code","labour_market_code"):
            if country_data.get(key) is not None:
                result[key] = country_data[key]
    return result


def progressive_drill(anchor: dict, *, radius_km: list[int] | None = None, travel_minutes: list[int] | None = None) -> list[dict]:
    """Return one normalized widening plan; execution providers consume the plan."""
    steps = [{"mode": "exact_anchor", "anchor": anchor}]
    for km in radius_km or [10, 25, 50, 100]:
        steps.append({"mode": "radius", "km": int(km), "anchor": anchor})
    for minutes in travel_minutes or [30, 45, 60]:
        steps.append({"mode": "travel_time", "minutes": int(minutes), "anchor": anchor})
    steps.extend([
        {"mode": "functional_labour_market", "anchor": anchor},
        {"mode": "admin1", "anchor": anchor},
        {"mode": "country", "anchor": anchor},
        {"mode": "remote", "anchor": anchor},
    ])
    return steps
