"""Deterministic candidate prioritization, not a collision probability model."""

import argparse
import json
import math
from pathlib import Path


def prioritize(candidate, threshold_km=50.0, velocity_scale_km_s=1.0):
    try:
        distance = float(candidate["distance_km"])
        velocity = float(candidate["relative_velocity_km_s"])
        threshold_km = float(threshold_km)
        velocity_scale_km_s = float(velocity_scale_km_s)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("candidate distance and relative velocity must be numeric") from exc
    if not all(math.isfinite(value) for value in (distance, velocity, threshold_km, velocity_scale_km_s)):
        raise ValueError("candidate distance, velocity, and scales must be finite")
    if distance < 0 or velocity < 0 or threshold_km <= 0 or velocity_scale_km_s <= 0:
        raise ValueError("distance, velocity, and scales must be non-negative/positive")
    distance_component = max(0.0, 1.0 - distance / threshold_km)
    velocity_component = max(0.0, 1.0 - velocity / velocity_scale_km_s)
    score = 0.7 * distance_component + 0.3 * velocity_component
    priority = "high" if score >= 0.75 else "medium" if score >= 0.40 else "low"
    return {
        **candidate,
        "prioritization_score": round(score, 9),
        "distance_component": round(distance_component, 9),
        "velocity_component": round(velocity_component, 9),
        "priority_band": priority,
        "score_definition": "0.7*(1-distance_km/threshold_km)+0.3*(1-relative_velocity_km_s/1.0), clipped at zero",
        "score_units": "dimensionless heuristic",
        "is_collision_probability": False,
    }


def rank_candidates(candidates, threshold_km=50.0, velocity_scale_km_s=1.0):
    ranked = [prioritize(candidate, threshold_km, velocity_scale_km_s) for candidate in candidates]
    return sorted(ranked, key=lambda item: (-item["prioritization_score"], item["distance_km"],
                                             item["relative_velocity_km_s"], str(item.get("object_a", "")),
                                             str(item.get("object_b", "")), str(item.get("epoch_utc", ""))))


def run(input_path, output_path):
    source = json.loads(Path(input_path).read_text(encoding="utf-8"))
    result = {
        "source_screening": str(input_path),
        "method": "deterministic physical-feature prioritization",
        "not_a_collision_probability": True,
        "threshold_km": source.get("threshold_km"),
        "candidates": rank_candidates(source.get("candidates", []), source["threshold_km"]),
    }
    Path(output_path).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    run(args.input, args.output)
