import unittest
from pathlib import Path


HIVE = Path(__file__).parents[1] / "hive" / "queries.hql"


class HiveQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = HIVE.read_text(encoding="utf-8").lower()

    def test_schema_has_event_fields_and_shell_partition(self):
        for token in ("event_id string", "tca_utc timestamp", "miss_distance_km double",
                      "relative_velocity_km_s double", "partitioned by (altitude_shell int)"):
            self.assertIn(token, self.text)

    def test_rollup_is_null_explicit_and_not_satcat(self):
        self.assertIn("coalesce(primary_operator, '(unknown)')", self.text)
        self.assertIn("coalesce(chaser_operator, '(unknown)')", self.text)
        self.assertIn("insert overwrite table conjunction_rollup_by_shell_operator", self.text)
        self.assertNotIn("satcat", self.text)
        self.assertIn("empty input produces zero output rows", self.text)
