import json, os, sqlite3, sys
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import PG_SCHEMA

def main():
    root=Path(__file__).resolve().parents[1]; sqlite_path=root/'data'/'analytics.sqlite3'; dsn=os.getenv('DATABASE_URL','postgresql://postgres@127.0.0.1:55432/postgres')
    with sqlite3.connect(sqlite_path) as src, psycopg.connect(dsn,row_factory=dict_row) as dst:
        dst.execute(PG_SCHEMA)
        for table in ['ingestion_batches','objects','orbital_stats','screening_runs','close_approaches','model_metrics']:
            dst.execute(f'DELETE FROM {table}')
        for table in ['ingestion_batches','objects','orbital_stats','screening_runs','close_approaches','model_metrics']:
            rows=src.execute(f'SELECT * FROM {table}').fetchall(); cols=[d[0] for d in src.execute(f'SELECT * FROM {table} LIMIT 0').description]
            if rows:
                placeholders=','.join(['%s']*len(cols)); clean=[tuple(v.decode('utf-8') if isinstance(v,bytes) else v for v in row) for row in rows]; dst.cursor().executemany(f'INSERT INTO {table} ({",".join(cols)}) VALUES ({placeholders})',clean)
        counts={table:dst.execute(f'SELECT COUNT(*) AS n FROM {table}').fetchone()['n'] for table in ['objects','orbital_stats','screening_runs','close_approaches','model_metrics']}
        representative=dst.execute('SELECT norad_cat_id,object_type FROM objects ORDER BY norad_cat_id LIMIT 1').fetchone()
    result={'dsn':'postgresql://postgres@127.0.0.1:55432/postgres','counts':counts,'representative':{'norad_cat_id':representative['norad_cat_id'],'object_type':representative['object_type'].decode('utf-8') if isinstance(representative['object_type'],bytes) else representative['object_type']},'sqlite_source':str(sqlite_path)}
    encoded=json.dumps(result,indent=2,default=str); (root/'data'/'postgres-migration.json').write_text(encoded,encoding='utf-8'); print(encoded)
if __name__=='__main__': main()
