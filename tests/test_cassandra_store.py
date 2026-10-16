import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from app.cassandra_store import CassandraObjectStateStore, validate_state


class Result:
    def __init__(self, value=None): self.value = value
    def one(self): return self.value


class FakeSession:
    def __init__(self): self.calls = []
    def execute(self, query, values):
        self.calls.append((query, values))
        return Result({"object_id": values[0] if isinstance(values, tuple) else "A"})


def valid_state():
    return {"object_id": "A", "time_bucket": "2026-01-01",
            "epoch_utc": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "position_km": (7000.0, 0.0, 0.0), "velocity_km_s": (0.0, 7.5, 0.0),
            "coordinate_frame": "TEME"}


class CassandraStoreTests(unittest.TestCase):
    def test_upsert_and_lookup_use_partition_key(self):
        session = FakeSession(); store = CassandraObjectStateStore(session)
        store.upsert(valid_state(), "fixture")
        row = store.get("A", "2026-01-01", valid_state()["epoch_utc"])
        self.assertEqual(row["object_id"], "A")
        self.assertEqual(len(session.calls), 2)

    def test_invalid_state_and_unavailable_session(self):
        with self.assertRaises(RuntimeError): CassandraObjectStateStore(None)
        bad = valid_state(); bad["position_km"] = (float("nan"), 0, 0)
        with self.assertRaises(ValueError): validate_state(bad)
        with self.assertRaises(ValueError): CassandraObjectStateStore(FakeSession()).get("", "x", valid_state()["epoch_utc"])

