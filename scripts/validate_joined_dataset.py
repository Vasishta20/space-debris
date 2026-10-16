"""Streaming, read-only validation for the large joined CSV.

The input is never rewritten. Only a compact JSON report is written to the
caller-selected output path under the external C: workspace.
"""

import argparse
import csv
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


NUMERIC_COLUMNS = {
    "norad_id": int,
    "inclination": float,
    "raan": float,
    "eccentricity": float,
    "arg_perigee": float,
    "mean_anomaly": float,
    "mean_motion": float,
    "mean_motion_dot": float,
    "bstar": float,
    "altitude_km": float,
    "period_min": float,
}


def validate(input_path: Path, parquet_path: Path | None = None) -> dict:
    started = time.perf_counter()
    stat = input_path.stat()
    rows = malformed = duplicate_keys = 0
    missing = Counter()
    invalid_numeric = Counter()
    key_set = set()
    joined_ids = set()
    header = None
    first_data = None
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        for values in reader:
            if first_data is None:
                first_data = values
            if len(values) != len(header):
                malformed += 1
                continue
            row = dict(zip(header, values))
            rows += 1
            for name, value in row.items():
                if value.strip() == "":
                    missing[name] += 1
            for name, converter in NUMERIC_COLUMNS.items():
                value = row[name].strip()
                if value:
                    try:
                        converter(value)
                    except (TypeError, ValueError):
                        invalid_numeric[name] += 1
            object_id = row["norad_id"].strip()
            epoch = row["epoch"].strip()
            if object_id:
                joined_ids.add(object_id)
            if object_id and epoch:
                key = (object_id, epoch)
                if key in key_set:
                    duplicate_keys += 1
                else:
                    key_set.add(key)

    comparison = None
    if parquet_path is not None:
        import pyarrow.parquet as pq

        table = pq.read_table(parquet_path, columns=["NORAD_CAT_ID"])
        parquet_ids = {str(value.as_py()) for value in table["NORAD_CAT_ID"] if value is not None}
        comparison = {
            "parquet_rows": table.num_rows,
            "joined_unique_norad_ids": len(joined_ids),
            "joined_ids_in_parquet": len(joined_ids & parquet_ids),
            "joined_ids_not_in_parquet": len(joined_ids - parquet_ids),
            "parquet_ids_not_in_joined": len(parquet_ids - joined_ids),
        }

    result = {
        "input": str(input_path),
        "input_size_bytes": stat.st_size,
        "input_last_write_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "header": header,
        "first_data_record": first_data,
        "data_rows": rows,
        "malformed_rows": malformed,
        "duplicate_norad_epoch_keys": duplicate_keys,
        "missing_values_by_column": dict(sorted(missing.items())),
        "invalid_numeric_values_by_column": dict(sorted(invalid_numeric.items())),
        "parquet_comparison": comparison,
        "elapsed_seconds": time.perf_counter() - started,
        "method": "single-pass csv.reader stream; exact duplicate key set and identifier-set comparison",
        "limitations": [
            "CSV row counts and quality checks are full-file checks; Parquet comparison uses the existing cleaned Parquet identifier column.",
            "No source TLE truth reconciliation or orbital propagation was performed by this validator.",
        ],
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--parquet", type=Path)
    args = parser.parse_args()
    result = validate(args.input, args.parquet)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
