from pathlib import Path
import os
import csv
import json
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .db import connect

app = FastAPI(title="Space Debris Collision Risk Analytics", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["GET"], allow_headers=["*"])
REPORTS = Path(__file__).resolve().parents[1] / "reports" / "eda"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_100K = PROJECT_ROOT / "data" / "joined_object_type_100k.csv"
SAMPLE_100K_META = PROJECT_ROOT / "data" / "joined_object_type_100k_metadata.json"
PREDICTION_PARTS = PROJECT_ROOT / "data" / "pyspark_ml_joined_100k" / "predictions_csv"
_PREDICTION_LOOKUP: dict[tuple[str, str], str] | None = None

def _canonical_epoch(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00").replace(" ", "T"))
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc)
    parsed = parsed.replace(microsecond=(parsed.microsecond // 1000) * 1000)
    return parsed.isoformat()

def _prediction_lookup() -> dict[tuple[str, str], str]:
    global _PREDICTION_LOOKUP
    if _PREDICTION_LOOKUP is None:
        lookup: dict[tuple[str, str], str] = {}
        for part in sorted(PREDICTION_PARTS.glob("part-*.csv")):
            with part.open("r", encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    lookup[(row["norad_id"], _canonical_epoch(row["epoch"]))] = row["predicted_category"]
        _PREDICTION_LOOKUP = lookup
    return _PREDICTION_LOOKUP

@app.get("/health")
def health():
    with connect() as c:
        c.execute("SELECT 1")
    backend = "postgresql" if os.getenv("DATABASE_URL", "").startswith("postgresql") else "sqlite"
    return {"status": "ok", "database": backend, "warning": "not a collision-probability service"}

@app.get("/api/summary")
def summary():
    with connect() as c:
        obj = c.execute("SELECT COUNT(*) n FROM objects").fetchone()["n"]
        stats = [dict(r) for r in c.execute("SELECT metric,value,source,created_at FROM orbital_stats ORDER BY id")]
        runs = [dict(r) for r in c.execute("SELECT id,source,object_count,samples,threshold_km,created_at FROM screening_runs ORDER BY id DESC")]
    return {"objects": obj, "orbital_stats": stats, "screening_runs": runs}

@app.get("/api/ingestion")
def ingestion():
    with connect() as c:
        row = c.execute("SELECT * FROM ingestion_batches ORDER BY id DESC LIMIT 1").fetchone()
    return dict(row) if row else {"source": None, "rows_seen": 0, "rows_loaded": 0, "rows_rejected": 0, "created_at": None}

@app.get("/api/catalog-100k/summary")
def catalog_100k_summary():
    if not SAMPLE_100K_META.exists():
        raise HTTPException(404, "100k catalog view not found")
    return json.loads(SAMPLE_100K_META.read_text(encoding="utf-8"))

@app.get("/api/catalog-100k/objects")
def catalog_100k_objects(
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    object_type: str | None = None,
    search: str | None = None,
):
    if not SAMPLE_100K.exists() or not SAMPLE_100K_META.exists():
        raise HTTPException(404, "100k catalog view not found")
    wanted_type = object_type.strip().upper() if object_type else None
    wanted_search = search.strip().lower() if search else None
    predictions = _prediction_lookup()
    items = []
    matched = 0
    with SAMPLE_100K.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            row_type = (row.get("OBJECT_TYPE") or "").upper()
            searchable = f"{row.get('norad_id', '')} {row.get('OBJECT_NAME', '')}".lower()
            if wanted_type and row_type != wanted_type:
                continue
            if wanted_search and wanted_search not in searchable:
                continue
            if matched >= offset and len(items) < limit:
                key = (row.get("norad_id", ""), _canonical_epoch(row.get("epoch", "")))
                items.append({
                    "norad_id": row.get("norad_id"),
                    "epoch": row.get("epoch"),
                    "object_name": row.get("OBJECT_NAME") or "Unnamed object",
                    "object_type": "UNK" if row_type == "UNKNOWN" else row_type,
                    "owner": row.get("OWNER") or "Unknown",
                    "altitude_km": float(row["altitude_km"]) if row.get("altitude_km") else None,
                    "inclination_deg": float(row["inclination"]) if row.get("inclination") else None,
                    "period_min": float(row["period_min"]) if row.get("period_min") else None,
                    "predicted_category": predictions.get(key),
                })
            matched += 1
    return {"items": items, "limit": limit, "offset": offset, "total": matched, "has_more": offset + len(items) < matched}

@app.get("/api/eda")
def eda():
    report = REPORTS / "eda.json"
    if not report.exists(): raise HTTPException(404, "EDA report not found")
    import json
    return {"report": json.loads(report.read_text(encoding="utf-8")), "charts": ["apogee_hist.png", "perigee_hist.png", "inclination_hist.png", "object_type_counts.png"]}

@app.get("/api/eda/{filename}")
def eda_chart(filename: str):
    allowed = {"apogee_hist.png", "perigee_hist.png", "inclination_hist.png", "object_type_counts.png"}
    if filename not in allowed: raise HTTPException(404, "chart not found")
    path = REPORTS / filename
    if not path.exists(): raise HTTPException(404, "chart not found")
    return FileResponse(path)

@app.get("/api/objects")
def objects(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), object_type: str | None = None):
    sql = "SELECT * FROM objects"
    args = []
    if object_type:
        sql += " WHERE object_type = ?"; args.append(object_type)
    sql += " ORDER BY norad_cat_id LIMIT ? OFFSET ?"; args.extend([limit, offset])
    with connect() as c:
        rows = [dict(r) for r in c.execute(sql, args)]
        count_sql = "SELECT COUNT(*) n FROM objects" + (" WHERE object_type = ?" if object_type else "")
        total = c.execute(count_sql, [object_type] if object_type else []).fetchone()["n"]
    return {"items": rows, "limit": limit, "offset": offset, "total": total, "has_more": offset + len(rows) < total}

@app.get("/api/objects/{norad_cat_id}")
def object_detail(norad_cat_id: int):
    with connect() as c: row = c.execute("SELECT * FROM objects WHERE norad_cat_id=?", (norad_cat_id,)).fetchone()
    if row is None: raise HTTPException(404, "object not found")
    return dict(row)

@app.get("/api/close-approaches")
def close_approaches(limit: int = Query(100, ge=1, le=500)):
    with connect() as c:
        rows = [dict(r) for r in c.execute("SELECT * FROM close_approaches ORDER BY distance_km LIMIT ?", (limit,))]
    return {"items": rows, "count": len(rows)}

@app.get("/api/models")
def models():
    with connect() as c: rows = [dict(r) for r in c.execute("SELECT * FROM model_metrics ORDER BY id DESC")]
    return {"items": rows}
