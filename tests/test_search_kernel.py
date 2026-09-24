import unittest

from careerhub.search_contract import normalize_search, lane_queries


class SearchKernelTests(unittest.TestCase):
    def test_legacy_and_canonical_lane_shapes_collapse(self):
        canonical = {
            "geographies": {"primary": ["Stockholm", "Sweden"]},
            "lanes": [
                {"lane_id": "L1", "priority": "core", "titles": ["strateg", "utredare"]},
                {"lane_id": "L2", "priority": "adjacent", "queries": ["analyst"]},
            ],
            "user_search_overlay": {"specific_wishes_or_needs": "hybrid"}
        }
        runtime = normalize_search(canonical)
        self.assertEqual(runtime["location"], "Stockholm")
        self.assertEqual(runtime["lanes"][0]["bucket"], "core")
        self.assertEqual(runtime["lanes"][0]["queries"], ["strateg", "utredare"])
        self.assertEqual(runtime["search_overlay"], "hybrid")

    def test_verified_terms_expand_core_only(self):
        core = {"bucket": "core", "queries": ["strateg"]}
        adjacent = {"bucket": "adjacent", "queries": ["analyst"]}
        self.assertIn("evaluation", lane_queries(core, ["evaluation"], "") )
        self.assertNotIn("evaluation", lane_queries(adjacent, ["evaluation"], "") )

    def test_overlay_is_query_input_not_candidate_data(self):
        lane = {"bucket": "core", "queries": ["strateg"]}
        q = lane_queries(lane, [], "remote part time")
        self.assertEqual(q[-1], "remote part time")


if __name__ == "__main__":
    unittest.main()
