import csv, json, sys, time
from collections import Counter
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main(src, out):
    t=time.perf_counter(); rows=[]
    with open(src, newline="", encoding="utf-8") as f: rows=list(csv.DictReader(f))
    def nums(k): return [float(r[k]) for r in rows if r.get(k) not in (None,"","-1")]
    out.mkdir(parents=True, exist_ok=True)
    for key,label in [("APOGEE","Apogee (km)"),("PERIGEE","Perigee (km)"),("INCLINATION","Inclination (deg)")]:
        plt.figure(figsize=(7,4)); plt.hist(nums(key), bins=40); plt.xlabel(label); plt.ylabel("objects"); plt.tight_layout(); plt.savefig(out/(key.lower()+"_hist.png")); plt.close()
    counts=Counter(r["OBJECT_TYPE"] for r in rows); plt.figure(figsize=(7,4)); plt.bar(counts.keys(),counts.values()); plt.xticks(rotation=45); plt.ylabel("objects"); plt.tight_layout(); plt.savefig(out/"object_type_counts.png"); plt.close()
    report={"rows":len(rows),"object_types":counts,"missing":{k:sum(not r.get(k) for r in rows) for k in ["APOGEE","PERIGEE","INCLINATION","RCS"]},"elapsed_seconds":time.perf_counter()-t}
    (out/"eda.json").write_text(json.dumps(report,indent=2,default=dict),encoding="utf-8"); print(json.dumps(report,default=dict))

if __name__ == "__main__": main(Path(sys.argv[1]),Path(sys.argv[2]))
