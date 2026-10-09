"""Balcony Sun-Map: sun-path maths (pvlib) -> direct-sun hours per spot and season."""
import pandas as pd
import pvlib

FACING = {"N": 0, "NE": 45, "E": 90, "SE": 135, "S": 180, "SW": 225, "W": 270, "NW": 315}
SEASON_DATES = {"summer": "2026-05-21", "monsoon": "2026-07-21", "winter": "2026-12-21"}


def sun_hours(lat: float, lon: float, facing: str, season: str = "winter", obstruction_deg: float = 15) -> float:
    """Hours of direct sun on a spot facing `facing`: sun must be above the obstruction angle
    (wall/building) and within 90 degrees of the facing direction."""
    date = SEASON_DATES.get(season, SEASON_DATES["winter"])
    times = pd.date_range(f"{date} 00:00", f"{date} 23:59", freq="10min", tz="Asia/Kolkata")
    sp = pvlib.solarposition.get_solarposition(times, lat, lon)
    face = FACING.get(facing.upper(), 180)
    diff = ((sp["azimuth"] - face + 180) % 360 - 180).abs()
    lit = (sp["elevation"] > obstruction_deg) & (diff < 90)
    return round(float(lit.sum()) * 10 / 60, 1)


def sun_map(lat: float, lon: float, obstruction_deg: float = 15) -> dict:
    grid = {f: {s: sun_hours(lat, lon, f, s, obstruction_deg) for s in SEASON_DATES} for f in FACING}
    best = max(grid, key=lambda f: grid[f]["winter"])
    return {"grid": grid, "best_facing_winter": best}


def light_class(hours: float) -> str:
    return "full" if hours >= 6 else "partial" if hours >= 3 else "shade"
