import json, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connect
from app.orbit import THRESHOLD_KM, STEP_MINUTES, SAMPLES, parse_tle_text, screen_records, utc_window

URL="https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
def main():
    root=Path(__file__).resolve().parents[1]; raw=root/"data"/"starlink.tle"; raw.parent.mkdir(exist_ok=True)
    downloaded=False
    if not raw.exists() or raw.stat().st_size == 0:
        request=urllib.request.Request(URL,headers={"User-Agent":"space-debris-collision-risk-local-research/0.1"})
        with urllib.request.urlopen(request,timeout=60) as response: raw.write_bytes(response.read())
        downloaded=True
    if raw.stat().st_size == 0: raise RuntimeError("TLE source returned an empty file")
    records=parse_tle_text(raw.read_text(encoding="utf-8"), max_objects=60)
    reference=datetime(2026,10,14,5,50,0,tzinfo=timezone.utc); times=utc_window(reference); t=time.perf_counter()
    approaches=screen_records(records, times, THRESHOLD_KM)
    now=datetime.now(timezone.utc).isoformat()
    with connect() as c:
        c.execute("DELETE FROM close_approaches"); c.execute("DELETE FROM screening_runs")
        c.execute("INSERT INTO screening_runs(source,object_count,samples,threshold_km,created_at) VALUES(?,?,?,?,?)",(URL,len(records),len(times),THRESHOLD_KM,now)); run=c.execute("SELECT last_insert_rowid()").fetchone()[0]
        c.executemany("INSERT INTO close_approaches(screening_run_id,object_a,object_b,epoch_utc,distance_km) VALUES(?,?,?,?,?)",[(run,x["object_a"],x["object_b"],x["epoch_utc"],x["distance_km"]) for x in approaches])
    result={"source":URL,"downloaded_file":str(raw),"download_performed_this_run":downloaded,"file_mtime_utc":datetime.fromtimestamp(raw.stat().st_mtime,timezone.utc).isoformat().replace("+00:00","Z"),"objects":len(records),"samples":len(times),"reference_epoch_utc":times[0].isoformat().replace("+00:00","Z"),"step_minutes":STEP_MINUTES,"coordinate_frame":"TEME","distance_units":"km","velocity_units":"km/s","threshold_km":THRESHOLD_KM,"approaches":len(approaches),"candidates":approaches,"elapsed_seconds":time.perf_counter()-t}
    (root/"data"/"screening.json").write_text(json.dumps(result,indent=2),encoding="utf-8"); print(json.dumps(result))
if __name__ == "__main__": main()
