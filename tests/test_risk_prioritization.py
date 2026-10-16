import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from risk_prioritization import prioritize, rank_candidates


class RiskPrioritizationTests(unittest.TestCase):
    def test_closer_and_slower_candidate_scores_higher(self):
        near = prioritize({"distance_km": 1, "relative_velocity_km_s": 0.1})
        far = prioritize({"distance_km": 49, "relative_velocity_km_s": 0.9})
        self.assertGreater(near["prioritization_score"], far["prioritization_score"])

    def test_threshold_and_units_are_explicit(self):
        result = prioritize({"distance_km": 50, "relative_velocity_km_s": 1})
        self.assertEqual(result["prioritization_score"], 0.0)
        self.assertFalse(result["is_collision_probability"])

    def test_invalid_values_rejected(self):
        with self.assertRaises(ValueError):
            prioritize({"distance_km": -1, "relative_velocity_km_s": 0.1})

    def test_missing_and_nonfinite_values_rejected(self):
        for candidate in ({"distance_km": None, "relative_velocity_km_s": 0.1},
                          {"distance_km": float("nan"), "relative_velocity_km_s": 0.1},
                          {"distance_km": 1}):
            with self.assertRaises(ValueError):
                prioritize(candidate)

    def test_deterministic_tie_breaking(self):
        candidates = [{"object_a": "Z", "object_b": "Y", "distance_km": 10, "relative_velocity_km_s": 0.2},
                      {"object_a": "A", "object_b": "B", "distance_km": 10, "relative_velocity_km_s": 0.2}]
        ranked = rank_candidates(candidates)
        self.assertEqual(ranked[0]["object_a"], "A")

    def test_score_components_are_exposed(self):
        result = prioritize({"distance_km": 10, "relative_velocity_km_s": 0.2})
        self.assertIn("distance_component", result)
        self.assertIn("velocity_component", result)
