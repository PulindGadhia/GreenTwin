"""Neighbourhood Disease Radar: anonymous pin-code outbreak alerts.
In-memory for the prototype; swap for a Supabase table in production."""
import time
from collections import defaultdict

_REPORTS = defaultdict(list)
ALERT_THRESHOLD = 3
WINDOW_S = 14 * 24 * 3600


def report(pincode: str, disease: str):
    _REPORTS[pincode].append((time.time(), disease))


def alerts(pincode: str) -> list:
    now = time.time()
    counts = defaultdict(int)
    for ts, d in _REPORTS[pincode]:
        if now - ts < WINDOW_S:
            counts[d] += 1
    return [{"disease": d, "reports": n,
             "message": f"{n} nearby gardens reported {d} in the last 14 days. Inspect your plants."}
            for d, n in counts.items() if n >= ALERT_THRESHOLD]
