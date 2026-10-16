import json, sys, time
from pathlib import Path
import pandas as pd

def main(source: Path, output: Path):
    started=time.perf_counter(); frame=pd.read_csv(source); output.parent.mkdir(parents=True,exist_ok=True); frame.to_parquet(output,index=False,engine='pyarrow'); restored=pd.read_parquet(output,engine='pyarrow')
    result={'source':str(source),'output':str(output),'rows_written':len(frame),'rows_read':len(restored),'columns':list(restored.columns),'schema_valid':list(frame.columns)==list(restored.columns),'elapsed_seconds':time.perf_counter()-started,'format':'parquet','engine':'pyarrow'}
    if not result['schema_valid'] or result['rows_written'] != result['rows_read']: raise RuntimeError(json.dumps(result))
    report=output.with_suffix('.json'); report.write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result))

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]; source=Path(sys.argv[1]); output=Path(sys.argv[2]) if len(sys.argv)>2 else root/'data'/'satcat_clean.parquet'; main(source,output)
