"""Optional Cassandra object-state adapter; PostgreSQL/SQLite remain defaults."""

import math
from datetime import datetime


UPSERT_CQL = """INSERT INTO object_state_by_bucket
(object_id, time_bucket, epoch_utc, position_x_km, position_y_km,
 position_z_km, velocity_x_km_s, velocity_y_km_s, velocity_z_km_s,
 coordinate_frame, source_uri)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
LOOKUP_CQL = """SELECT * FROM object_state_by_bucket
WHERE object_id = ? AND time_bucket = ? AND epoch_utc = ?"""


def validate_state(state):
    required = ("object_id", "time_bucket", "epoch_utc", "position_km", "velocity_km_s", "coordinate_frame")
    missing = [key for key in required if key not in state or state[key] in (None, "")]
    if missing:
        raise ValueError("missing state fields: " + ", ".join(missing))
    if len(state["position_km"]) != 3 or len(state["velocity_km_s"]) != 3:
        raise ValueError("position_km and velocity_km_s must contain three values")
    values = [float(value) for value in state["position_km"] + state["velocity_km_s"]]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("state coordinates and velocities must be finite")
    if not isinstance(state["epoch_utc"], datetime):
        raise ValueError("epoch_utc must be a datetime")
    return state


class CassandraObjectStateStore:
    """Small session-protocol adapter; session creation is intentionally external."""

    def __init__(self, session):
        if session is None or not hasattr(session, "execute"):
            raise RuntimeError("Cassandra session is unavailable")
        self.session = session

    def upsert(self, state, source_uri=""):
        validate_state(state)
        values = (state["object_id"], state["time_bucket"], state["epoch_utc"],
                  *[float(value) for value in state["position_km"]],
                  *[float(value) for value in state["velocity_km_s"]],
                  state["coordinate_frame"], source_uri)
        self.session.execute(UPSERT_CQL, values)

    def get(self, object_id, time_bucket, epoch_utc):
        if not object_id or not time_bucket or not isinstance(epoch_utc, datetime):
            raise ValueError("object_id, time_bucket, and epoch_utc are required")
        return self.session.execute(LOOKUP_CQL, (object_id, time_bucket, epoch_utc)).one()
