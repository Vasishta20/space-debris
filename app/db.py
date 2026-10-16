from pathlib import Path
import os
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "analytics.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS ingestion_batches (
    id INTEGER PRIMARY KEY, source TEXT NOT NULL, rows_seen INTEGER NOT NULL,
    rows_loaded INTEGER NOT NULL, rows_rejected INTEGER NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS objects (
    norad_cat_id INTEGER PRIMARY KEY, object_name TEXT, object_id TEXT,
    object_type TEXT, owner TEXT, launch_date TEXT, decay_date TEXT,
    period_min REAL, inclination_deg REAL, apogee_km REAL, perigee_km REAL,
    rcs_m2 REAL, orbit_center TEXT, orbit_type TEXT, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orbital_stats (
    id INTEGER PRIMARY KEY, metric TEXT NOT NULL, value REAL NOT NULL,
    source TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS screening_runs (
    id INTEGER PRIMARY KEY, source TEXT NOT NULL, object_count INTEGER NOT NULL,
    samples INTEGER NOT NULL, threshold_km REAL NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS close_approaches (
    id INTEGER PRIMARY KEY, screening_run_id INTEGER NOT NULL, object_a TEXT NOT NULL,
    object_b TEXT NOT NULL, epoch_utc TEXT NOT NULL, distance_km REAL NOT NULL,
    FOREIGN KEY(screening_run_id) REFERENCES screening_runs(id)
);
CREATE TABLE IF NOT EXISTS model_metrics (
    id INTEGER PRIMARY KEY, model_name TEXT NOT NULL, target TEXT NOT NULL,
    accuracy REAL NOT NULL, macro_f1 REAL NOT NULL, rows_used INTEGER NOT NULL,
    created_at TEXT NOT NULL, details_json TEXT NOT NULL
);
"""

PG_SCHEMA = """
CREATE TABLE IF NOT EXISTS ingestion_batches (id BIGSERIAL PRIMARY KEY, source TEXT NOT NULL, rows_seen BIGINT NOT NULL, rows_loaded BIGINT NOT NULL, rows_rejected BIGINT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS objects (norad_cat_id BIGINT PRIMARY KEY, object_name TEXT, object_id TEXT, object_type TEXT, owner TEXT, launch_date TEXT, decay_date TEXT, period_min DOUBLE PRECISION, inclination_deg DOUBLE PRECISION, apogee_km DOUBLE PRECISION, perigee_km DOUBLE PRECISION, rcs_m2 DOUBLE PRECISION, orbit_center TEXT, orbit_type TEXT, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS orbital_stats (id BIGSERIAL PRIMARY KEY, metric TEXT NOT NULL, value DOUBLE PRECISION NOT NULL, source TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS screening_runs (id BIGSERIAL PRIMARY KEY, source TEXT NOT NULL, object_count BIGINT NOT NULL, samples BIGINT NOT NULL, threshold_km DOUBLE PRECISION NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS close_approaches (id BIGSERIAL PRIMARY KEY, screening_run_id BIGINT NOT NULL, object_a TEXT NOT NULL, object_b TEXT NOT NULL, epoch_utc TEXT NOT NULL, distance_km DOUBLE PRECISION NOT NULL);
CREATE TABLE IF NOT EXISTS model_metrics (id BIGSERIAL PRIMARY KEY, model_name TEXT NOT NULL, target TEXT NOT NULL, accuracy DOUBLE PRECISION NOT NULL, macro_f1 DOUBLE PRECISION NOT NULL, rows_used BIGINT NOT NULL, created_at TEXT NOT NULL, details_json TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_objects_type ON objects(object_type);
CREATE INDEX IF NOT EXISTS idx_close_distance ON close_approaches(distance_km);
"""

class PostgresCompat:
    def __init__(self, dsn):
        import psycopg
        from psycopg.rows import dict_row
        self._con = psycopg.connect(dsn, row_factory=dict_row)
        self._con.execute(PG_SCHEMA)
        self._con.commit()
    def execute(self, sql, params=None):
        return DecodedCursor(self._con.execute(sql.replace("?", "%s"), params or ()))
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb):
        if exc_type: self._con.rollback()
        else: self._con.commit()
        self._con.close()

class DecodedCursor:
    def __init__(self, cursor): self._cursor = cursor
    @staticmethod
    def decode(value):
        if isinstance(value, bytes): return value.decode('utf-8')
        if isinstance(value, dict): return {k: DecodedCursor.decode(v) for k, v in value.items()}
        if isinstance(value, tuple): return tuple(DecodedCursor.decode(v) for v in value)
        return value
    def fetchone(self):
        row = self._cursor.fetchone(); return self.decode(row) if row is not None else None
    def fetchall(self): return [self.decode(row) for row in self._cursor.fetchall()]
    def __iter__(self): return iter(self.fetchall())

def connect():
    dsn = os.getenv("DATABASE_URL")
    if dsn and dsn.startswith("postgresql"):
        return PostgresCompat(dsn)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con
