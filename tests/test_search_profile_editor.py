import pytest

from scripts.update_search_profile import apply_lane_updates


def base_profile():
    return {
        'lanes': [
            {
                'lane_id': 'core',
                'name': 'Old core name',
                'bucket': 'core',
                'priority': 1,
                'queries': ['old term'],
            },
            {
                'lane_id': 'bridge',
                'name': 'Old bridge name',
                'bucket': 'bridge',
                'priority': 3,
                'queries': ['extra'],
            },
        ]
    }


def test_lane_editor_updates_name_and_queries_only():
    data = base_profile()
    apply_lane_updates(
        data,
        '[{"lane_id":"core","name":"Editorial / press","queries":["journalist","editor"]}]',
    )
    lane = data['lanes'][0]
    assert lane['name'] == 'Editorial / press'
    assert lane['queries'] == ['journalist', 'editor']
    assert lane['lane_id'] == 'core'
    assert lane['bucket'] == 'core'
    assert lane['priority'] == 1


def test_lane_editor_rejects_unknown_lane_id():
    data = base_profile()
    with pytest.raises(SystemExit, match='Unknown lane_id'):
        apply_lane_updates(data, '[{"lane_id":"invented","name":"New","queries":["term"]}]')


def test_lane_editor_requires_search_terms():
    data = base_profile()
    with pytest.raises(SystemExit, match='at least one search term'):
        apply_lane_updates(data, '[{"lane_id":"core","name":"Core","queries":[]}]')
