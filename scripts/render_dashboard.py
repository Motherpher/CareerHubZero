#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from careerhub.dashboard import render_html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instance", help="Path to profiled instance.yaml")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    instance = Path(args.instance).resolve()
    output = Path(args.output) if args.output else instance.parent / "dashboard" / "index.html"
    print(render_html(instance, output))


if __name__ == "__main__":
    main()
