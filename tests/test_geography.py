import unittest

from careerhub.geography import build_map_payload, geotag_job, geotag_vault


class FakeGeocoder:
    def __init__(self):
        self.calls = []

    def search(self, query, region_code=None):
        self.calls.append((query, region_code))
        if query == "Stockholm, Stockholms län":
            return {
                "id": "stockholm",
                "displayName": {"text": "Stockholm"},
                "formattedAddress": "Stockholm, Sweden",
                "location": {"latitude": 59.3293, "longitude": 18.0686},
                "types": ["locality", "political"],
                "addressComponents": [
                    {"longText": "Stockholm", "shortText": "Stockholm", "types": ["locality"]},
                    {"longText": "Stockholms län", "shortText": "AB", "types": ["administrative_area_level_1"]},
                    {"longText": "Sweden", "shortText": "SE", "types": ["country"]},
                ],
            }
        if query == "Sveavägen 1, Stockholm":
            return {
                "id": "sveavagen-1",
                "displayName": {"text": "Sveavägen 1"},
                "formattedAddress": "Sveavägen 1, 111 57 Stockholm, Sweden",
                "location": {"latitude": 59.3372, "longitude": 18.0624},
                "types": ["street_address"],
                "addressComponents": [
                    {"longText": "Stockholm", "shortText": "Stockholm", "types": ["locality"]},
                    {"longText": "Stockholms län", "shortText": "AB", "types": ["administrative_area_level_1"]},
                    {"longText": "111 57", "shortText": "111 57", "types": ["postal_code"]},
                    {"longText": "Sweden", "shortText": "SE", "types": ["country"]},
                ],
            }
        return None


class GeographyTests(unittest.TestCase):
    def test_city_only_job_keeps_locality_precision(self):
        job = {
            "id": "city",
            "title": "Communicator",
            "location": "Stockholm, Stockholms län",
            "work_mode": "Arbete på plats",
        }
        tagged = geotag_job(job, FakeGeocoder(), region_code="SE")
        self.assertEqual(tagged["geo"]["precision"], "locality")
        self.assertEqual(tagged["geo"]["scope"], "area")
        self.assertEqual(tagged["geo"]["hierarchy"]["country_code"], "SE")

    def test_exact_address_becomes_precise_point(self):
        job = {
            "id": "exact",
            "title": "Editor",
            "workplace_address": "Sveavägen 1, Stockholm",
            "location": "Stockholm, Stockholms län",
            "in_latest_scan": True,
            "scan_count": 1,
        }
        tagged = geotag_job(job, FakeGeocoder(), region_code="SE")
        self.assertEqual(tagged["geo"]["precision"], "premise")
        self.assertEqual(tagged["geo"]["scope"], "point")
        self.assertEqual(tagged["geo"]["location_basis"], "workplace_address")

    def test_company_lookup_is_off_by_default(self):
        geo = FakeGeocoder()
        job = {"company": "Example AB", "location": "Stockholm, Stockholms län"}
        geotag_job(job, geo, region_code="SE")
        self.assertEqual(geo.calls[0][0], "Stockholm, Stockholms län")

    def test_source_coordinates_win_without_google_call(self):
        geo = FakeGeocoder()
        job = {"latitude": 59.0, "longitude": 18.0, "location": "Stockholm"}
        tagged = geotag_job(job, geo)
        self.assertEqual(tagged["geo"]["provider"], "source")
        self.assertEqual(tagged["geo"]["precision"], "source_coordinates")
        self.assertEqual(geo.calls, [])

    def test_remote_without_location_is_not_given_fake_point(self):
        tagged = geotag_job({"id": "remote", "work_mode": "remote"}, FakeGeocoder())
        self.assertEqual(tagged["geo"]["status"], "remote")
        self.assertIsNone(tagged["geo"]["point"])

    def test_zoomed_map_splits_precise_jobs_but_keeps_coarse_city_cluster(self):
        vault = {
            "jobs": [
                {
                    "id": "city",
                    "title": "Communicator",
                    "location": "Stockholm, Stockholms län",
                    "in_latest_scan": True,
                    "scan_count": 2,
                },
                {
                    "id": "exact",
                    "title": "Editor",
                    "workplace_address": "Sveavägen 1, Stockholm",
                    "location": "Stockholm, Stockholms län",
                    "in_latest_scan": True,
                    "scan_count": 1,
                },
            ]
        }
        tagged = geotag_vault(vault, FakeGeocoder(), region_code="SE")

        city_view = build_map_payload(tagged["jobs"], zoom=8)
        self.assertEqual(city_view["level"], "locality")
        self.assertEqual(city_view["clusters"][0]["count"], 2)
        self.assertEqual(city_view["clusters"][0]["new_count"], 1)

        close_view = build_map_payload(tagged["jobs"], zoom=12)
        self.assertEqual(close_view["mode"], "mixed")
        self.assertEqual(len(close_view["points"]), 1)
        self.assertEqual(close_view["points"][0]["properties"]["job_id"], "exact")
        self.assertEqual(close_view["clusters"][0]["count"], 1)


if __name__ == "__main__":
    unittest.main()
