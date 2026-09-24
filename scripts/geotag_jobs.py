#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from careerhub.geography import GooglePlacesGeocoder, build_map_payload, geotag_vault


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Geotag CareerHub job-vault records and optionally emit a zoom-aware map payload."
    )
    ap.add_argument("vault", type=Path, help="Path to job_vault.json")
    ap.add_argument("--output", type=Path, help="Write tagged vault here; defaults to in-place")
    ap.add_argument("--region-code", help="Optional 2-letter region bias, e.g. SE")
    ap.add_argument(
        "--retag",
        action="store_true",
        help="Re-geotag jobs that already contain a tagged geo object",
    )
    ap.add_argument(
        "--allow-company-place-fallback",
        action="store_true",
        help="Allow employer + location Google lookup. Off by default to avoid assigning the wrong office.",
    )
    ap.add_argument("--map-output", type=Path, help="Optional JSON output for map rendering")
    ap.add_argument("--zoom", type=float, default=6.0, help="Zoom used for --map-output")
    ap.add_argument(
        "--latest-only",
        action="store_true",
        help="Map only jobs present in the latest source scan",
    )
    args = ap.parse_args()

    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        raise SystemExit("GOOGLE_MAPS_API_KEY is required")

    vault = json.loads(args.vault.read_text(encoding="utf-8"))
    geocoder = GooglePlacesGeocoder(api_key)
    tagged = geotag_vault(
        vault,
        geocoder,
        region_code=args.region_code,
        only_missing=not args.retag,
        allow_company_place_fallback=args.allow_company_place_fallback,
    )

    destination = args.output or args.vault
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(tagged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote tagged vault: {destination}")

    if args.map_output:
        jobs = tagged.get("jobs", [])
        if args.latest_only:
            jobs = [j for j in jobs if j.get("in_latest_scan")]
        payload = build_map_payload(jobs, args.zoom)
        args.map_output.parent.mkdir(parents=True, exist_ok=True)
        args.map_output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote map payload: {args.map_output}")


if __name__ == "__main__":
    main()
