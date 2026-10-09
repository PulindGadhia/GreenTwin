import io

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from backend import rootcause, sunmap, water
from backend.main import app
from backend.leaf import analyse_leaf

client = TestClient(app)


def make_leaf(spots=False, yellow=False):
    img = Image.new("RGB", (200, 200), (40, 140, 50))
    d = ImageDraw.Draw(img)
    if spots:
        for x in range(20, 180, 40):
            d.ellipse([x, 60, x + 25, 85], fill=(90, 50, 20))
    if yellow:
        d.rectangle([0, 0, 200, 120], fill=(200, 190, 40))
    buf = io.BytesIO(); img.save(buf, "PNG")
    return buf.getvalue()


def test_leaf_signals():
    assert analyse_leaf(make_leaf())["signal"] == "healthy"
    assert analyse_leaf(make_leaf(spots=True))["signal"] == "fungal_spots"
    assert analyse_leaf(make_leaf(yellow=True))["signal"] == "yellowing"


def test_sun_south_beats_north_in_winter():
    assert sunmap.sun_hours(22.3, 70.8, "S", "winter") > sunmap.sun_hours(22.3, 70.8, "N", "winter")


def test_rain_skips_watering():
    w = {"rain_mm": 12, "rain_tomorrow_mm": 0, "temp_c": 30, "humidity": 70}
    assert water.water_budget("tomato", 10, "loam", w)["action"] == "skip"


def test_rootcause_low_light():
    v = rootcause.diagnose("yellowing", 2.0, "full", 3, 50)
    assert v["cause"] == "low_light"


def test_api_diagnose():
    r = client.post("/api/diagnose", files={"photo": ("leaf.png", make_leaf(spots=True), "image/png")},
                    data={"plant": "tomato", "facing": "N", "waterings_per_week": 7})
    assert r.status_code == 200
    assert r.json()["verdict"]["cause"] == "fungal"
