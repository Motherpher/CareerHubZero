#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from careerhub.instance import load_profile_node, validate_profile_node_paths


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.replace('\n', ',').split(',') if item.strip()]


def apply_lane_updates(data: dict, raw_json: str) -> None:
    if not raw_json.strip():
        return
    try:
        updates = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise SystemExit(f'Invalid lane update JSON: {exc}') from exc
    if not isinstance(updates, list):
        raise SystemExit('Lane updates must be a JSON list.')

    lanes = data.get('lanes') or []
    if not isinstance(lanes, list):
        raise SystemExit('Search Profile lanes are not a list.')
    by_id = {str(lane.get('lane_id')): lane for lane in lanes if isinstance(lane, dict) and lane.get('lane_id')}

    for update in updates:
        if not isinstance(update, dict):
            raise SystemExit('Each lane update must be an object.')
        lane_id = str(update.get('lane_id') or '').strip()
        if lane_id not in by_id:
            raise SystemExit(f'Unknown lane_id: {lane_id or "<empty>"}')
        lane = by_id[lane_id]
        name = str(update.get('name') or '').strip()
        queries = update.get('queries', [])
        if not name:
            raise SystemExit(f'Lane {lane_id} must have a name.')
        if isinstance(queries, str):
            queries = split_values(queries)
        if not isinstance(queries, list):
            raise SystemExit(f'Lane {lane_id} queries must be a list.')
        cleaned_queries = [str(item).strip() for item in queries if str(item).strip()]
        if not cleaned_queries:
            raise SystemExit(f'Lane {lane_id} must contain at least one search term.')

        # User editing is deliberately limited to presentation and sourcing terms.
        # lane_id, bucket and priority remain governed by the existing architecture.
        lane['name'] = name
        lane['queries'] = cleaned_queries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--anchors', default='')
    parser.add_argument('--remote-allowed', choices=['true', 'false'], default='false')
    parser.add_argument('--engagement-types', default='')
    parser.add_argument('--saved-need', default='')
    parser.add_argument('--lanes-json', default='')
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
    apply_lane_updates(data, args.lanes_json)

    search_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print(f'Updated Search Profile: {search_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
