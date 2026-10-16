import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from pyspark_mllib_exploratory_ranking import validate_candidates


class MllibReadinessTests(unittest.TestCase):
    def test_empty_and_single_inputs_are_not_training_data(self):
        self.assertEqual(validate_candidates([]), [])
        self.assertEqual(validate_candidates([{"distance_km": 1, "relative_velocity_km_s": 2}]), [])

    def test_units_missing_and_invalid_values(self):
        self.assertTrue(validate_candidates([{"distance_km": 1, "relative_velocity_km_s": 2, "distance_units": "m"}]))
        self.assertTrue(validate_candidates([{"distance_km": -1, "relative_velocity_km_s": 2}]))
        self.assertTrue(validate_candidates([{"distance_km": 1}]))
