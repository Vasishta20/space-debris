import csv, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connect

REQUIRED = {"OBJECT_NAME","OBJECT_ID","NORAD_CAT_ID","OBJECT_TYPE","OWNER","PERIOD","INCLINATION","APOGEE","PERIGEE","RCS"}
def number(v):
    if v is None or v.strip() in ("", "-1"): return None
    try: return float(v)
    except ValueError: return None

def main(src):
    started=time.perf_counter()
    now = datetime.now(timezone.utc).isoformat(); seen=set(); rows=[]; rejected=0; total=0
    with open(src, newline="", encoding="utf-8") as f:
        reader=csv.DictReader(f); missing=REQUIRED-set(reader.fieldnames or [])
        if missing: raise ValueError(f"missing columns: {sorted(missing)}")
        for r in reader:
            total += 1
            try: norad=int(r["NORAD_CAT_ID"])
            except (ValueError,TypeError): rejected += 1; continue
            if norad in seen or not r["OBJECT_TYPE"]: rejected += 1; continue
            seen.add(norad); rows.append((norad,r["OBJECT_NAME"],r["OBJECT_ID"],r["OBJECT_TYPE"],r["OWNER"],r["LAUNCH_DATE"],r["DECAY_DATE"],number(r["PERIOD"]),number(r["INCLINATION"]),number(r["APOGEE"]),number(r["PERIGEE"]),number(r["RCS"]),r["ORBIT_CENTER"],r["ORBIT_TYPE"],now))
    with connect() as c:
        c.execute("DELETE FROM objects")
        c.executemany("INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        c.execute("DELETE FROM ingestion_batches")
        c.execute("INSERT INTO ingestion_batches(source,rows_seen,rows_loaded,rows_rejected,created_at) VALUES(?,?,?,?,?)", (str(src),total,len(rows),rejected,now))
        c.execute("DELETE FROM orbital_stats")
        for metric,value in [("objects_loaded",len(rows)),("rows_rejected",rejected),("mean_apogee_km",sum(x[9] for x in rows if x[9] is not None)/sum(x[9] is not None for x in rows)),("mean_perigee_km",sum(x[10] for x in rows if x[10] is not None)/sum(x[10] is not None for x in rows))]:
            c.execute("INSERT INTO orbital_stats(metric,value,source,created_at) VALUES(?,?,?,?)",(metric,value,str(src),now))
    print(json.dumps({"source":str(src),"rows_seen":total,"rows_loaded":len(rows),"rows_rejected":rejected,"elapsed_seconds":time.perf_counter()-started}))

if __name__ == "__main__": main(Path(sys.argv[1]))
