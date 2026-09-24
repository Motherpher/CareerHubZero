from __future__ import annotations

import os
import unicodedata
from typing import Any, Protocol

import requests

SCB_WFS = "https://geodata.scb.se/geoserver/stat/wfs"

SWEDEN_COUNTIES = {
    "01": "Stockholms län",
    "03": "Uppsala län",
    "04": "Södermanlands län",
    "05": "Östergötlands län",
    "06": "Jönköpings län",
    "07": "Kronobergs län",
    "08": "Kalmar län",
    "09": "Gotlands län",
    "10": "Blekinge län",
    "12": "Skåne län",
    "13": "Hallands län",
    "14": "Västra Götalands län",
    "17": "Värmlands län",
    "18": "Örebro län",
    "19": "Västmanlands län",
    "20": "Dalarnas län",
    "21": "Gävleborgs län",
    "22": "Västernorrlands län",
    "23": "Jämtlands län",
    "24": "Västerbottens län",
    "25": "Norrbottens län",
}

# Authoritative source descriptors are stored with the adapter so provenance
# follows the enrichment result rather than being duplicated into map/UI state.
SCB_SOURCES = {
    "admin_2026": "https://www.scb.se/hitta-statistik/regional-statistik-och-kartor/regionala-indelningar/lan-och-kommuner/",
    "regso_2025": "https://www.scb.se/vara-tjanster/oppna-data/oppna-geodata/regso/",
    "deso_2025": "https://www.scb.se/vara-tjanster/oppna-data/oppna-geodata/demografiska-statistikomraden-deso/",
}


class CountryAdapter(Protocol):
    country_code: str
    def enrich(self, geo: dict[str, Any]) -> dict[str, Any]: ...


def _norm(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).strip().casefold()
    return " ".join(text.split())


def _county_code(name: str) -> str | None:
    target = _norm(name)
    for code, label in SWEDEN_COUNTIES.items():
        if _norm(label) == target:
            return code
    return None


def _feature_properties(feature: dict | None) -> dict:
    return dict((feature or {}).get("properties") or {})


class SwedenAdapter:
    country_code = "SE"

    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        # Layer names are deployment-configurable because SCB may change
        # GeoServer identifiers independently of the stable CareerHub contract.
        self.regso_layer = os.getenv("SCB_REGSO_WFS_LAYER", "")
        self.deso_layer = os.getenv("SCB_DESO_WFS_LAYER", "")

    def _wfs_point(self, layer: str, lat: float, lng: float) -> dict | None:
        if not layer:
            return None
        # BBOX point query avoids assuming the geometry-property name.
        eps = 0.00002
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeNames": layer,
            "outputFormat": "application/json",
            "srsName": "EPSG:4326",
            "bbox": f"{lng-eps},{lat-eps},{lng+eps},{lat+eps},EPSG:4326",
            "count": 2,
        }
        response = requests.get(SCB_WFS, params=params, timeout=self.timeout)
        response.raise_for_status()
        features = response.json().get("features") or []
        return features[0] if features else None

    def enrich(self, geo: dict[str, Any]) -> dict[str, Any]:
        hierarchy = geo.get("hierarchy") or {}
        point = geo.get("point") or {}
        admin1 = str(hierarchy.get("admin1") or "")
        locality = str(hierarchy.get("locality") or "")
        county_code = _county_code(admin1)
        out: dict[str, Any] = {
            "adapter": "scb",
            "adapter_version": "SE-2026/2025",
            "country_code": "SE",
            "county_code": county_code,
            "county_name": SWEDEN_COUNTIES.get(county_code or ""),
            "municipality_code": None,
            "municipality_name": locality or None,
            "regso_code": None,
            "deso_code": None,
            "local_labour_market_code": None,
            "sources": SCB_SOURCES,
            "completeness": {
                "county": bool(county_code),
                "municipality": False,
                "regso": False,
                "deso": False,
                "local_labour_market": False,
            },
        }

        lat, lng = point.get("lat"), point.get("lng")
        try:
            lat_f, lng_f = float(lat), float(lng)
        except (TypeError, ValueError):
            return out

        for key, layer in (("regso", self.regso_layer), ("deso", self.deso_layer)):
            try:
                props = _feature_properties(self._wfs_point(layer, lat_f, lng_f))
            except Exception as exc:
                out.setdefault("warnings", []).append(f"{key}_lookup_failed:{exc.__class__.__name__}")
                continue
            if not props:
                continue
            # Attribute names differ across SCB geodata releases; retain raw
            # properties for audit and extract common identifiers defensively.
            lower = {str(k).casefold(): v for k, v in props.items()}
            code = (
                lower.get(f"{key}kod")
                or lower.get(f"{key}_kod")
                or lower.get(f"{key}code")
                or lower.get(key)
            )
            out[f"{key}_code"] = str(code) if code not in (None, "") else None
            out["completeness"][key] = bool(out[f"{key}_code"])
            out[f"{key}_properties"] = props

        return out


class GoogleOnlyAdapter:
    def __init__(self, country_code: str):
        self.country_code = country_code

    def enrich(self, geo: dict[str, Any]) -> dict[str, Any]:
        return {
            "adapter": "google_only",
            "country_code": self.country_code,
            "sources": {},
            "completeness": {},
        }


def get_country_adapter(country_code: str | None) -> CountryAdapter:
    code = str(country_code or "").upper()
    if code == "SE":
        return SwedenAdapter()
    return GoogleOnlyAdapter(code)


def enrich_country_matrix(geo: dict[str, Any]) -> dict[str, Any]:
    hierarchy = geo.get("hierarchy") or {}
    adapter = get_country_adapter(hierarchy.get("country_code"))
    return adapter.enrich(geo)
