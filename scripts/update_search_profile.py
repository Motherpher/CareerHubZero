#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

# Direct execution from scripts/ otherwise places scripts/careerhub.py ahead of
# the canonical src/careerhub package on sys.path. Pin src/ first so this helper
# behaves identically in GitHub Actions and local execution.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / 'src'
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
else:
    sys.path.remove(str(SRC_ROOT))
    sys.path.insert(0, str(SRC_ROOT))

from careerhub.instance import load_profile_node, validate_profile_node_paths


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.replace('\n', ',').split(',') if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--anchors', default='')
    parser.add_argument('--remote-allowed', choices=['true', 'false'], default='false')
    parser.add_argument('--engagement-types', default='')
    parser.add_argument('--saved-need', default='')
    args = parser.parse_args()

    manifest = Path(args.manifest).resolve()
    errors = validate_profile_node_paths(manifest)
    if errors:
        raise SystemExit('CareerHub profile-node validation failed:\n- ' + '\n- '.join(errors))
    ctx = load_profile_node(manifest)
    search_path = ctx['paths']['search']
    data = yaml.safe_load(search_path.read_text(encoding='utf-8')) or {}

    geographies = data.setdefault('geographies', {})
    geographies['anchors'] = split_values(args.anchors)
    geographies['remote_allowed'] = args.remote_allowed == 'true'
    data['engagement_types'] = split_values(args.engagement_types)
    overlay = data.setdefault('user_search_overlay', {})
    overlay.setdefault('source', 'user_input')
    overlay.setdefault('scope', 'search_only')
    overlay['specific_wishes_or_needs'] = args.saved_need.strip()

    search_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print(f'Updated Search Profile: {search_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
