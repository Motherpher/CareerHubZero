#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from careerhub.instance import load_instance, validate_instance_paths, InstanceError


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instance", help="Path to profiled instance.yaml")
    args = ap.parse_args()
    errors = validate_instance_paths(args.instance)
    if errors:
        for e in errors:
            print("ERROR", e)
        raise SystemExit(1)
    try:
        data = load_instance(args.instance)
    except (InstanceError, KeyError, ValueError) as exc:
        print("ERROR", exc)
        raise SystemExit(1)
    print("Instance OK:", data["instance"]["careerhub"]["instance_id"])


if __name__ == "__main__":
    main()
