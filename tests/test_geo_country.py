import unittest

from careerhub.geo_country import adapter_for, enrich_geo, progressive_drill


class GeoCountryTests(unittest.TestCase):
    def setUp(self):
        self.registry = {
            "schema_version": "1.0",
            "countries": {
                "SE": {
                    "status":"supported_matrix",
                    "adapter":"scb",
                    "administrative_matrix":True,
                    "functional_labour_market":True,
                    "fine_statistical_areas":True,
                    "source_authority":"SCB",
                }
            }
        }

    def test_sweden_adapter_does_not_replace_google_point(self):
        geo = {"point":{"lat":59.3,"lng":18.0},"hierarchy":{"country_code":"SE","locality":"Stockholm"}}
        enriched = enrich_geo(geo, self.registry, {"municipality_code":"0180"})
        self.assertEqual(geo["point"]["lat"], 59.3)
        self.assertEqual(enriched["adapter"], "scb")
        self.assertEqual(enriched["municipality_code"], "0180")

    def test_unknown_country_falls_back_cleanly(self):
        cfg = adapter_for("FR", self.registry)
        self.assertEqual(cfg["status"], "google_only")
        self.assertIsNone(cfg["adapter"])

    def test_progressive_drill_is_one_widening_plan(self):
        steps = progressive_drill({"place_id":"x"}, radius_km=[25], travel_minutes=[45])
        self.assertEqual([x["mode"] for x in steps], [
            "exact_anchor","radius","travel_time","functional_labour_market","admin1","country","remote"
        ])


if __name__ == "__main__":
    unittest.main()
