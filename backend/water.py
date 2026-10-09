"""Rain-smart water budget: ml per plant from plant type, pot size, soil and live weather."""
import httpx

PLANTS = {
    "tomato": {"ml_per_l": 55, "sun": "full"},
    "chilli": {"ml_per_l": 45, "sun": "full"},
    "mint": {"ml_per_l": 70, "sun": "partial"},
    "basil": {"ml_per_l": 60, "sun": "partial"},
    "spinach": {"ml_per_l": 50, "sun": "partial"},
}
SOIL = {"sandy": 1.25, "loam": 1.0, "clay": 0.8}


def get_weather(lat: float, lon: float) -> dict:
    """Free Open-Meteo forecast; falls back to mild defaults offline so demos never break."""
    try:
        r = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon,
                    "daily": "precipitation_sum,temperature_2m_max,relative_humidity_2m_mean",
                    "forecast_days": 2, "timezone": "auto"},
            timeout=6,
        )
        d = r.json()["daily"]
        return {"rain_mm": d["precipitation_sum"][0], "rain_tomorrow_mm": d["precipitation_sum"][1],
                "temp_c": d["temperature_2m_max"][0], "humidity": d["relative_humidity_2m_mean"][0],
                "source": "open-meteo"}
    except Exception:
        return {"rain_mm": 0.0, "rain_tomorrow_mm": 0.0, "temp_c": 30.0, "humidity": 50, "source": "fallback"}


def water_budget(plant: str, pot_litres: float, soil: str, weather: dict, feedback: float = 1.0) -> dict:
    """feedback: learned multiplier from user taps ('too dry' -> up, 'soggy' -> down)."""
    p = PLANTS.get(plant, PLANTS["tomato"])
    ml = p["ml_per_l"] * pot_litres * SOIL.get(soil, 1.0)
    ml *= 1 + max(0, weather["temp_c"] - 25) * 0.03
    ml *= 1 - max(0, weather["humidity"] - 60) * 0.004
    ml *= feedback
    if weather["rain_mm"] >= 5:
        return {"ml": 0, "action": "skip", "reason": f"{weather['rain_mm']} mm rain today"}
    if weather["rain_tomorrow_mm"] >= 8:
        return {"ml": int(ml * 0.4), "action": "reduce", "reason": "heavy rain expected tomorrow"}
    return {"ml": int(ml), "action": "water", "reason": "dry day"}
