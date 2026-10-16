"""Bounded altitude-shell screening helpers.

The shell index is based on geocentric altitude derived from the propagated
TEME position: ``sqrt(x*x+y*y+z*z) - 6378.137 km``.  Shells are half-open
``[n*width, (n+1)*width)``; an exact boundary belongs to the higher shell.
With a shell width no smaller than the miss-distance threshold, same and
adjacent shells are sufficient for this radial-altitude prefilter because
Euclidean separation is at least the absolute difference in geocentric
radius.  This implementation still compares candidates with the original
distance and velocity checks, and is intended for bounded demonstrations,
not as a replacement for a high-fidelity conjunction assessment.
"""

from collections import defaultdict
from itertools import groupby
from math import isfinite, sqrt

EARTH_RADIUS_KM = 6378.137


def geocentric_altitude_km(position_km, earth_radius_km=EARTH_RADIUS_KM):
    values = [float(value) for value in position_km]
    if len(values) != 3 or not all(isfinite(value) for value in values):
        raise ValueError("position must contain three finite coordinates")
    return sqrt(sum(value * value for value in values)) - float(earth_radius_km)


def shell_index(altitude_km, width_km):
    altitude = float(altitude_km)
    width = float(width_km)
    if not isfinite(altitude) or not isfinite(width) or width <= 0:
        raise ValueError("altitude must be finite and shell width must be positive")
    return int(altitude // width)


def _distance(a, b):
    return sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def _pair_key(a, b):
    left = (str(a.get("object_id", "")), int(a.get("norad_id", -1)))
    right = (str(b.get("object_id", "")), int(b.get("norad_id", -1)))
    return tuple(sorted((left, right)))


def _candidate(a, b, epoch, distance_km, relative_velocity_km_s, shell_a, shell_b, width_km):
    first, second = sorted((a, b), key=lambda item: (str(item.get("object_id", "")), int(item.get("norad_id", -1))))
    return {
        "object_a": first.get("object_id"),
        "norad_a": first.get("norad_id"),
        "object_b": second.get("object_id"),
        "norad_b": second.get("norad_id"),
        "epoch_utc": epoch,
        "distance_km": distance_km,
        "relative_velocity_km_s": relative_velocity_km_s,
        "coordinate_frame": "TEME",
        "distance_units": "km",
        "velocity_units": "km/s",
        "shell_width_km": width_km,
        "shell_a": shell_a if first is a else shell_b,
        "shell_b": shell_b if first is a else shell_a,
    }


def _validate_parameters(threshold_km, shell_width_km):
    threshold = float(threshold_km)
    width = float(shell_width_km)
    if not isfinite(threshold) or threshold < 0 or not isfinite(width) or width < threshold:
        raise ValueError("threshold must be non-negative and shell width must be >= threshold")
    return threshold, width


def screen_epoch_states(states, threshold_km=50.0, shell_width_km=50.0):
    """Screen one epoch and release its state/pair working set on return."""
    threshold, width = _validate_parameters(threshold_km, shell_width_km)
    state_map = {}
    for state in states:
        object_id = str(state["object_id"])
        key = (object_id, int(state.get("norad_id", -1)))
        position = tuple(float(value) for value in state["position_km"])
        velocity = tuple(float(value) for value in state["velocity_km_s"])
        altitude = geocentric_altitude_km(position)
        state_map[key] = dict(state, object_id=object_id, position_km=position,
                              velocity_km_s=velocity, altitude_km=altitude,
                              shell=shell_index(altitude, width))
    if not state_map:
        return []
    epochs = {str(state["epoch_utc"]) for state in state_map.values()}
    if len(epochs) != 1:
        raise ValueError("screen_epoch_states requires exactly one epoch")
    epoch = next(iter(epochs))
    by_shell = defaultdict(list)
    for state in state_map.values():
        by_shell[state["shell"]].append(state)
    for bucket in by_shell.values():
        bucket.sort(key=lambda item: (str(item["object_id"]), int(item.get("norad_id", -1))))

    results = []
    shell_keys = sorted(by_shell)
    for shell in shell_keys:
        bucket = by_shell[shell]
        for index, first in enumerate(bucket):
            for second in bucket[index + 1:]:
                distance = _distance(first["position_km"], second["position_km"])
                if 0.0 <= distance <= threshold:
                    results.append(_candidate(first, second, epoch, distance,
                                              _distance(first["velocity_km_s"], second["velocity_km_s"]),
                                              first["shell"], second["shell"], width))
        adjacent = by_shell.get(shell + 1, [])
        for first in bucket:
            for second in adjacent:
                distance = _distance(first["position_km"], second["position_km"])
                if 0.0 <= distance <= threshold:
                    results.append(_candidate(first, second, epoch, distance,
                                              _distance(first["velocity_km_s"], second["velocity_km_s"]),
                                              first["shell"], second["shell"], width))
    return sorted(results, key=lambda item: (item["epoch_utc"], item["object_a"], item["object_b"]))


def screen_states_streaming(states, threshold_km=50.0, shell_width_km=50.0):
    """Process an epoch-ordered state iterator with bounded working memory.

    The input must be ordered by nondecreasing ``epoch_utc`` and may contain
    duplicate records within an epoch. Only one epoch's states and candidates
    are retained at a time; callers can propagate and yield one epoch at a
    time to avoid materializing the full time window.
    """
    _validate_parameters(threshold_km, shell_width_km)
    last_epoch = None
    for epoch, group in groupby(states, key=lambda item: str(item["epoch_utc"])):
        if last_epoch is not None and epoch <= last_epoch:
            raise ValueError("screen_states_streaming requires strictly increasing epoch groups")
        last_epoch = epoch
        for result in screen_epoch_states(group, threshold_km, shell_width_km):
            yield result


def screen_states(states, threshold_km=50.0, shell_width_km=50.0):
    """Screen propagated states using same/adjacent altitude shells.

    Each state must contain object_id, epoch_utc, position_km and velocity_km_s.
    States from different epochs are never paired. Duplicate object/epoch
    inputs are tolerated and cannot emit duplicate canonical pair keys. This
    compatibility API groups all supplied epochs; use screen_states_streaming
    for bounded one-epoch working memory.
    """
    threshold, width = _validate_parameters(threshold_km, shell_width_km)
    groups = defaultdict(dict)
    for state in states:
        epoch = str(state["epoch_utc"])
        object_id = str(state["object_id"])
        position = tuple(float(value) for value in state["position_km"])
        velocity = tuple(float(value) for value in state["velocity_km_s"])
        altitude = geocentric_altitude_km(position)
        shell = shell_index(altitude, width)
        normalized = dict(state, object_id=object_id, position_km=position, velocity_km_s=velocity,
                          altitude_km=altitude, shell=shell)
        groups[epoch][(object_id, int(state.get("norad_id", -1)))] = normalized

    return sorted((result for epoch_states in groups.values()
                   for result in screen_epoch_states(epoch_states.values(), threshold, width)),
                  key=lambda item: (item["epoch_utc"], item["object_a"], item["object_b"]))


def brute_force_states(states, threshold_km=50.0):
    """Reference implementation used only for bounded equivalence tests."""
    threshold = float(threshold_km)
    by_epoch = defaultdict(dict)
    for state in states:
        key = (str(state["object_id"]), int(state.get("norad_id", -1)))
        by_epoch[str(state["epoch_utc"])] [key] = state
    results = []
    for epoch, state_map in by_epoch.items():
        values = list(state_map.values())
        for index, a in enumerate(values):
            for b in values[index + 1:]:
                distance = _distance(a["position_km"], b["position_km"])
                if 0.0 <= distance <= threshold:
                    altitude_a = geocentric_altitude_km(a["position_km"])
                    altitude_b = geocentric_altitude_km(b["position_km"])
                    results.append(_candidate(a, b, epoch, distance,
                                              _distance(a["velocity_km_s"], b["velocity_km_s"]),
                                              shell_index(altitude_a, 50.0), shell_index(altitude_b, 50.0), 50.0))
    return sorted(results, key=lambda item: (item["epoch_utc"], item["object_a"], item["object_b"]))
