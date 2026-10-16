import csv, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connect

def main(src):
    t=time.perf_counter(); rows=list(csv.DictReader(open(src,encoding="utf-8",newline="")))
    features=["PERIOD","INCLINATION","APOGEE","PERIGEE","RCS","OWNER","ORBIT_TYPE"]; target="OBJECT_TYPE"
    data=[r for r in rows if r.get(target)]
    X=[[float(r[k]) if k in features[:5] and r.get(k) not in ("","-1") else (np.nan if k in features[:5] else r.get(k,"")) for k in features] for r in data]; y=[r[target] for r in data]
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
    pre=ColumnTransformer([("num",Pipeline([("imp",SimpleImputer(strategy="median")),("scale",StandardScaler())]),list(range(5))), ("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),("oh",OneHotEncoder(handle_unknown="ignore"))]),[5,6])])
    model=Pipeline([("pre",pre),("clf",LogisticRegression(max_iter=500,class_weight="balanced"))]); model.fit(Xtr,ytr); pred=model.predict(Xte)
    metrics={"model_name":"logistic_regression_object_type","target":target,"accuracy":accuracy_score(yte,pred),"macro_f1":f1_score(yte,pred,average="macro"),"rows_used":len(data),"classes":sorted(set(y)),"classification_report":classification_report(yte,pred,output_dict=True),"elapsed_seconds":time.perf_counter()-t}
    out=Path(__file__).resolve().parents[1]/"data"/"model_metrics.json"; out.write_text(json.dumps(metrics,indent=2,default=float),encoding="utf-8")
    with connect() as c: c.execute("DELETE FROM model_metrics"); c.execute("INSERT INTO model_metrics(model_name,target,accuracy,macro_f1,rows_used,created_at,details_json) VALUES(?,?,?,?,?,?,?)",(metrics["model_name"],target,metrics["accuracy"],metrics["macro_f1"],len(data),datetime.now(timezone.utc).isoformat(),json.dumps(metrics)))
    print(json.dumps({k:metrics[k] for k in ["model_name","target","accuracy","macro_f1","rows_used","elapsed_seconds"]}))

if __name__ == "__main__": main(Path(sys.argv[1]))
