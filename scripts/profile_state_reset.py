#!/usr/bin/env python3
"""Plan or apply a conservative CareerHub profile-state reset.

Dry-run is the default. Apply mode is intentionally explicit and refuses any
plan containing UNKNOWN_BLOCK. Genuine profile/evidence/application state is not
part of this tool's mutation surface.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from careerhub.state_integrity import apply_reset_plan, build_reset_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile_root", help="CareerHub profile root containing careerhub.yaml")
    parser.add_argument("--apply", action="store_true", help="Apply only safe SYNTHETIC_DELETE decisions")
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args()

    root = Path(args.profile_root).resolve()
    plan = build_reset_plan(root)
    report = plan.to_dict()
    report["mode"] = "apply" if args.apply else "dry-run"

    if args.apply:
        report["result"] = apply_reset_plan(root, plan)

    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
