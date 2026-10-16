"""Bounded, project-local scalability assessment for altitude-shell screening.

This reads only the existing C: Parquet artifact, creates small deterministic
state fixtures, and never writes to the source repository or D:. Timings are
measurements of the shell implementation on a single process; catalog-scale
figures are arithmetic estimates, not executed jobs.
"""
import json
import math
import os
import sys
import time
import tracemalloc
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.shell_screen import screen_states, screen_states_streaming

PARQUET = ROOT / "data" / "satcat_clean.parquet"
EPOCHS = 7
THRESHOLD_KM = 50.0
SHELL_WIDTH_KM = 50.0


def load_altitudes():
    import pyarrow.parquet as pq
    table = pq.read_table(PARQUET, columns=["APOGEE", "PERIGEE"])
    values = []
    for apogee, perigee in zip(table["APOGEE"].to_pylist(), table["PERIGEE"].to_pylist()):
        value = apogee if apogee is not None else perigee
        if value is not None and math.isfinite(float(value)):
            values.append(float(value))
    return values


def make_states(altitudes, count):
    states = []
    radius = 6378.137
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for epoch_index in range(EPOCHS):
        epoch = (start + timedelta(minutes=10 * epoch_index)).isoformat().replace("+00:00", "Z")
        for index, altitude in enumerate(altitudes[:count]):
            angle = (index * 2.399963229728653 + epoch_index * 0.17) % (2 * math.pi)
            r = radius + altitude
            states.append({
                "object_id": f"S{index:06d}", "norad_id": index + 1,
                "epoch_utc": epoch,
                "position_km": (r * math.cos(angle), r * math.sin(angle), 0.0),
                "velocity_km_s": (-7.5 * math.sin(angle), 7.5 * math.cos(angle), 0.01),
            })
    return states


def iter_states(altitudes, count):
    radius = 6378.137
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for epoch_index in range(EPOCHS):
        epoch = (start + timedelta(minutes=10 * epoch_index)).isoformat().replace("+00:00", "Z")
        for index, altitude in enumerate(altitudes[:count]):
            angle = (index * 2.399963229728653 + epoch_index * 0.17) % (2 * math.pi)
            r = radius + altitude
            yield {"object_id": f"S{index:06d}", "norad_id": index + 1,
                   "epoch_utc": epoch,
                   "position_km": (r * math.cos(angle), r * math.sin(angle), 0.0),
                   "velocity_km_s": (-7.5 * math.sin(angle), 7.5 * math.cos(angle), 0.01)}


def run_case(altitudes, count):
    states = make_states(altitudes, count)
    shell_counts = Counter()
    for state in states[:count]:
        altitude = math.sqrt(sum(value * value for value in state["position_km"])) - 6378.137
        shell_counts[math.floor(altitude / SHELL_WIDTH_KM)] += 1
    brute_pairs_per_epoch = count * (count - 1) // 2
    # Exact shell candidate-comparison count for one epoch, without building a
    # second implementation: same-shell pairs plus each adjacent-shell pair.
    counts = list(shell_counts.values())
    shell_pair_count = sum(n * (n - 1) // 2 for n in counts)
    shell_keys = sorted(shell_counts)
    shell_pair_count += sum(shell_counts[a] * shell_counts[b] for a, b in zip(shell_keys, shell_keys[1:]) if b == a + 1)
    tracemalloc.start()
    started = time.perf_counter()
    legacy_result = screen_states(states, THRESHOLD_KM, SHELL_WIDTH_KM)
    legacy_elapsed = time.perf_counter() - started
    _, legacy_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    tracemalloc.start()
    started = time.perf_counter()
    streaming_result = list(screen_states_streaming(iter_states(altitudes, count), THRESHOLD_KM, SHELL_WIDTH_KM))
    streaming_elapsed = time.perf_counter() - started
    _, streaming_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "objects_per_epoch": count, "epochs": EPOCHS, "states": len(states),
        "brute_force_pairs_per_epoch": brute_pairs_per_epoch,
        "shell_comparisons_per_epoch": shell_pair_count,
        "legacy_candidates": len(legacy_result), "streaming_candidates": len(streaming_result),
        "identity_match": {(x["object_a"], x["object_b"], x["epoch_utc"]) for x in legacy_result} ==
                          {(x["object_a"], x["object_b"], x["epoch_utc"]) for x in streaming_result},
        "legacy_elapsed_seconds": legacy_elapsed, "streaming_elapsed_seconds": streaming_elapsed,
        "legacy_peak_tracemalloc_bytes": legacy_peak, "streaming_peak_tracemalloc_bytes": streaming_peak,
        "shell_count": len(shell_counts),
        "largest_shell_occupancy": max(shell_counts.values()),
        "candidate_pair_reduction_estimate": 1.0 - (shell_pair_count / brute_pairs_per_epoch) if brute_pairs_per_epoch else 0.0,
    }


def main():
    altitudes = load_altitudes()
    counts = [60, 240, 960]
    cases = [run_case(altitudes, count) for count in counts]
    catalog_objects = 68129
    full_pairs_per_epoch = catalog_objects * (catalog_objects - 1) // 2
    output = {
        "input": str(PARQUET), "input_altitude_values": len(altitudes),
        "threshold_km": THRESHOLD_KM, "shell_width_km": SHELL_WIDTH_KM,
        "epochs": EPOCHS, "cases": cases,
        "catalog_estimate": {
            "objects_per_epoch": catalog_objects, "states": catalog_objects * EPOCHS,
            "brute_force_pairs_per_epoch": full_pairs_per_epoch,
            "brute_force_pairs_all_epochs": full_pairs_per_epoch * EPOCHS,
            "note": "Arithmetic estimate only; no full-catalog shell or brute-force job executed.",
        },
        "algorithmic_limits": [
            "The legacy screen_states API retains all supplied states; screen_states_streaming retains only one epoch working set when input is epoch-ordered.",
            "Work is proportional to same/adjacent-shell occupancy, not guaranteed linear.",
            "Shell pruning is safe for this radial prefilter only when shell width is at least the distance threshold; final Cartesian distance remains authoritative.",
            "The streaming API has no disk spill or distributed partitioning; full-catalog execution requires a separate resource-approved design.",
        ],
    }
    target = ROOT / "reports" / "shell-scalability-20261015.json"
    target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
