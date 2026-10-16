import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from app.shell_screen import (brute_force_states, geocentric_altitude_km,
                               screen_states, screen_states_streaming, shell_index)


R = 6378.137


def state(name, altitude, x_offset=0.0, epoch="2026-01-01T00:00:00Z", norad=None):
    return {"object_id": name, "norad_id": norad or int(name[1:]), "epoch_utc": epoch,
            "position_km": (R + altitude + x_offset, 0.0, 0.0),
            "velocity_km_s": (0.0, 7.5, 0.01)}


class ShellScreenTests(unittest.TestCase):
    def test_same_shell_and_boundary_crossing_are_candidates(self):
        values = [state("A1", 500.0), state("B2", 500.0, 10.0), state("C3", 499.9, 20.0)]
        result = screen_states(values)
        self.assertEqual({(x["object_a"], x["object_b"]) for x in result}, {("A1", "B2"), ("A1", "C3"), ("B2", "C3")})

    def test_exact_boundary_belongs_to_higher_shell(self):
        self.assertEqual(shell_index(500.0, 50.0), 10)
        self.assertEqual(shell_index(499.999999, 50.0), 9)
        self.assertAlmostEqual(geocentric_altitude_km((R + 500.0, 0, 0)), 500.0)

    def test_duplicates_distance_and_epoch_are_handled(self):
        duplicate = state("A1", 500.0)
        values = [duplicate, dict(duplicate), state("B2", 500.0, 100.0), state("C3", 500.0, 1.0, "2026-01-01T00:10:00Z")]
        result = screen_states(values)
        self.assertEqual(len(result), 0)

    def test_matches_brute_force_reference(self):
        values = [state("A1", 500.0), state("B2", 500.0, 20.0), state("C3", 549.9, 20.0), state("D4", 700.0, 1.0)]
        bucketed = screen_states(values)
        brute = brute_force_states(values)
        self.assertEqual([(x["object_a"], x["object_b"], x["distance_km"]) for x in bucketed],
                         [(x["object_a"], x["object_b"], x["distance_km"]) for x in brute])

    def test_streaming_preserves_same_pair_at_multiple_epochs(self):
        values = [state("A1", 500.0, epoch="2026-01-01T00:00:00Z"),
                  state("B2", 500.0, 10.0, epoch="2026-01-01T00:00:00Z"),
                  state("A1", 500.0, epoch="2026-01-01T00:10:00Z"),
                  state("B2", 500.0, 10.0, epoch="2026-01-01T00:10:00Z")]
        result = list(screen_states_streaming(values))
        self.assertEqual(len(result), 2)
        self.assertEqual([item["epoch_utc"] for item in result], ["2026-01-01T00:00:00Z", "2026-01-01T00:10:00Z"])

    def test_streaming_requires_epoch_order(self):
        values = [state("A1", 500.0, epoch="2026-01-01T00:10:00Z"),
                  state("B2", 500.0, epoch="2026-01-01T00:00:00Z")]
        with self.assertRaises(ValueError):
            list(screen_states_streaming(values))

    def test_invalid_width_rejected(self):
        with self.assertRaises(ValueError):
            screen_states([state("A1", 500), state("B2", 500)], threshold_km=50, shell_width_km=10)
