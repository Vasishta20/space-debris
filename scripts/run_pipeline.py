import subprocess, sys, time
from pathlib import Path
root=Path(__file__).resolve().parents[1]; repo=Path(r"D:\Projects\space-debris-collision-risk"); py=sys.executable
commands=[
 [py,str(root/"scripts/ingest_satcat.py"),str(repo/"data/raw/satcat_clean.csv")],
 [py,str(root/"scripts/eda.py"),str(repo/"data/raw/satcat_clean.csv"),str(root/"reports/eda")],
 [py,str(root/"scripts/train_model.py"),str(repo/"data/raw/satcat_clean.csv")],
 [py,str(root/"scripts/screen_tle.py")],
]
for cmd in commands:
 print("RUN", " ".join(cmd)); subprocess.run(cmd,check=True)
print("pipeline complete")
