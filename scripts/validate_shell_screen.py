"""Compare bounded altitude-shell screening with the existing brute-force screen."""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.orbit import THRESHOLD_KM, parse_tle_text, utc_window
from app.shell_screen import brute_force_states, screen_states


def main():
    source = ROOT / "data" / "starlink.tle"
    records = parse_tle_text(source.read_text(encoding="utf-8"), max_objects=60)
    epochs = utc_window(datetime(2026, 10, 14, 5, 50, tzinfo=timezone.utc))
    states = []
    start = time.perf_counter()
    for epoch in epochs:
        jd, fr = __import__("sgp4.api", fromlist=["jday"]).jday(
            epoch.year, epoch.month, epoch.day, epoch.hour, epoch.minute,
            epoch.second + epoch.microsecond / 1e6)
        epoch_text = epoch.isoformat().replace("+00:00", "Z")
        for record in records:
            error, position, velocity = record["sat"].sgp4(jd, fr)
            if error == 0:
                states.append({"object_id": record["name"], "norad_id": record["norad_id"],
                               "epoch_utc": epoch_text, "position_km": position,
                               "velocity_km_s": velocity})
    brute = brute_force_states(states, THRESHOLD_KM)
    bucketed = screen_states(states, THRESHOLD_KM, THRESHOLD_KM)

    def identity(row):
        return (row["object_a"], row["norad_a"], row["object_b"], row["norad_b"], row["epoch_utc"])

    brute_ids = {identity(row) for row in brute}
    bucket_ids = {identity(row) for row in bucketed}
    output = {
        "source": str(source), "objects": len(records), "epochs": len(epochs),
        "states": len(states), "reference_epoch_utc": epochs[0].isoformat().replace("+00:00", "Z"),
        "step_minutes": 10, "threshold_km": THRESHOLD_KM, "shell_width_km": THRESHOLD_KM,
        "altitude_definition": "geocentric TEME radius minus 6378.137 km",
        "boundary_definition": "half-open [n*50,(n+1)*50); exact boundary belongs to higher shell",
        "brute_force_candidates": len(brute), "bucketed_candidates": len(bucketed),
        "missing_from_bucketed": sorted(brute_ids - bucket_ids),
        "extra_in_bucketed": sorted(bucket_ids - brute_ids),
        "identity_match": brute_ids == bucket_ids,
        "result_match": [(identity(row), row["distance_km"], row["relative_velocity_km_s"]) for row in brute] ==
                        [(identity(row), row["distance_km"], row["relative_velocity_km_s"]) for row in bucketed],
        "candidates": bucketed,
        "elapsed_seconds": time.perf_counter() - start,
        "limitations": ["bounded 60-object, seven-epoch sample", "TEME geocentric altitude is a pruning reference, not an operational conjunction geometry model"],
    }
    target = ROOT / "reports" / "shell-screen-validation-20261015.json"
    target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not output["identity_match"] or not output["result_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
