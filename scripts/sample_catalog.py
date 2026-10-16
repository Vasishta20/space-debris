"""Create the deterministic canonical catalog from the joined SATCAT/TLE CSV.

The source is read sequentially and never rewritten. Reservoir sampling keeps
memory bounded while giving every valid row equal inclusion probability.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import time
from collections import Counter
from pathlib import Path


FIELDS = [
    "norad_id", "epoch", "inclination", "raan", "eccentricity",
    "arg_perigee", "mean_anomaly", "mean_motion", "mean_motion_dot",
    "bstar", "intl_designator", "altitude_km", "OBJECT_TYPE",
    "OBJECT_NAME", "OWNER", "LAUNCH_DATE", "DECAY_DATE",
    "OPS_STATUS_CODE", "period_min", "period_implausible",
    "altitude_shell", "inclination_band",
]


def run(source: Path, output: Path, metadata_path: Path, size: int, seed: int) -> dict:
    start = time.perf_counter()
    rng = random.Random(seed)
    reservoir: list[dict[str, str]] = []
    seen = 0
    malformed = 0
    label_counts = Counter()
    object_counts = Counter()
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [field for field in FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing source columns: {missing}")
        for row in reader:
            if not row.get("norad_id") or not row.get("OBJECT_TYPE"):
                malformed += 1
                continue
            try:
                float(row["inclination"])
                float(row["altitude_km"])
                float(row["period_min"])
            except (TypeError, ValueError):
                malformed += 1
                continue
            item = {field: row.get(field, "") for field in FIELDS}
            seen += 1
            label_counts[item["OBJECT_TYPE"]] += 1
            object_counts[item["norad_id"]] += 1
            if len(reservoir) < size:
                reservoir.append(item)
            else:
                position = rng.randrange(seen)
                if position < size:
                    reservoir[position] = item
    reservoir.sort(key=lambda row: (row["norad_id"], row["epoch"], row["OBJECT_TYPE"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(reservoir)
    sample_labels = Counter(row["OBJECT_TYPE"] for row in reservoir)
    sample_objects = Counter(row["norad_id"] for row in reservoir)
    metadata = {
        "source": str(source),
        "output": str(output),
        "requested_rows": size,
        "sample_rows": len(reservoir),
        "source_valid_rows_seen": seen,
        "source_rows_rejected": malformed,
        "random_seed": seed,
        "sampling": "one-pass uniform reservoir sampling over valid rows",
        "source_label_counts": dict(label_counts),
        "sample_label_counts": dict(sample_labels),
        "source_unique_norad_ids_observed": len(object_counts),
        "sample_unique_norad_ids": len(sample_objects),
        "elapsed_seconds": time.perf_counter() - start,
        "original_source_modified": False,
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--size", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=20261016)
    args = parser.parse_args()
    run(args.source, args.output, args.metadata, args.size, args.seed)
