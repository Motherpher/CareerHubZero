import unittest

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


class SearchProfileLaneEditorTests(unittest.TestCase):
    def test_lane_editor_updates_name_and_queries_only(self):
        data = base_profile()
        apply_lane_updates(
            data,
            '[{"lane_id":"core","name":"Editorial / press","queries":["journalist","editor"]}]',
        )
        lane = data['lanes'][0]
        self.assertEqual(lane['name'], 'Editorial / press')
        self.assertEqual(lane['queries'], ['journalist', 'editor'])
        self.assertEqual(lane['lane_id'], 'core')
        self.assertEqual(lane['bucket'], 'core')
        self.assertEqual(lane['priority'], 1)

    def test_lane_editor_rejects_unknown_lane_id(self):
        data = base_profile()
        with self.assertRaisesRegex(SystemExit, 'Unknown lane_id'):
            apply_lane_updates(data, '[{"lane_id":"invented","name":"New","queries":["term"]}]')

    def test_lane_editor_requires_search_terms(self):
        data = base_profile()
        with self.assertRaisesRegex(SystemExit, 'at least one search term'):
            apply_lane_updates(data, '[{"lane_id":"core","name":"Core","queries":[]}]')


if __name__ == '__main__':
    unittest.main()
