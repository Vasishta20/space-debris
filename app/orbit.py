from datetime import datetime, timedelta, timezone
from math import sqrt
from sgp4.api import Satrec, jday

THRESHOLD_KM = 50.0
STEP_MINUTES = 10
SAMPLES = 7

def parse_tle_text(text: str, max_objects: int = 60):
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    records = []
    for i in range(0, len(lines) - 2, 3):
        name, line1, line2 = lines[i:i + 3]
        if not (line1.startswith("1 ") and line2.startswith("2 ")): continue
        try: norad = int(line1[2:7])
        except ValueError: continue
        try: sat = Satrec.twoline2rv(line1, line2)
        except Exception: continue
        records.append({"name": name.strip(), "norad_id": norad, "line1": line1, "line2": line2, "sat": sat})
        if len(records) >= max_objects: break
    return records

def utc_window(start: datetime, samples: int = SAMPLES, step_minutes: int = STEP_MINUTES):
    if start.tzinfo is None: raise ValueError("start must be timezone-aware UTC")
    start = start.astimezone(timezone.utc)
    return [start + timedelta(minutes=step_minutes * i) for i in range(samples)]

def distance_km(a, b):
    return sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))

def is_candidate(distance: float, threshold_km: float = THRESHOLD_KM):
    return 0.0 <= float(distance) <= float(threshold_km)

def screen_records(records, epochs, threshold_km: float = THRESHOLD_KM):
    candidates = []
    for epoch in epochs:
        jd, fr = jday(epoch.year, epoch.month, epoch.day, epoch.hour, epoch.minute, epoch.second + epoch.microsecond / 1e6)
        positions = []
        for record in records:
            error, position, velocity = record["sat"].sgp4(jd, fr)
            if error == 0: positions.append((record, position, velocity))
        for index, (a, pa, va) in enumerate(positions):
            for b, pb, vb in positions[index + 1:]:
                distance = distance_km(pa, pb)
                if is_candidate(distance, threshold_km):
                    relative_velocity = distance_km(va, vb)
                    candidates.append({
                        "object_a": a["name"], "norad_a": a["norad_id"], "object_b": b["name"], "norad_b": b["norad_id"],
                        "epoch_utc": epoch.isoformat().replace("+00:00", "Z"), "distance_km": distance,
                        "relative_velocity_km_s": relative_velocity, "coordinate_frame": "TEME",
                        "tle_a_line1": a["line1"], "tle_a_line2": a["line2"], "tle_b_line1": b["line1"], "tle_b_line2": b["line2"]
                    })
    return candidates
