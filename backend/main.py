from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import radar, rootcause, sunmap, water
from .leaf import analyse_leaf

app = FastAPI(title="GreenTwin API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
FRONT = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/sunmap")
def api_sunmap(lat: float = 22.30, lon: float = 70.80, obstruction_deg: float = 15):
    return sunmap.sun_map(lat, lon, obstruction_deg)


@app.get("/api/water")
def api_water(plant: str = "tomato", pot_litres: float = 10, soil: str = "loam",
              lat: float = 22.30, lon: float = 70.80):
    w = water.get_weather(lat, lon)
    return {"weather": w, "budget": water.water_budget(plant, pot_litres, soil, w)}


@app.get("/api/radar/{pincode}")
def api_radar(pincode: str):
    return {"pincode": pincode, "alerts": radar.alerts(pincode)}


@app.post("/api/diagnose")
async def api_diagnose(
    photo: UploadFile = File(...),
    plant: str = Form("tomato"),
    facing: str = Form("S"),
    season: str = Form("winter"),
    waterings_per_week: int = Form(3),
    lat: float = Form(22.30),
    lon: float = Form(70.80),
    pincode: str = Form("360005"),
    lang: str = Form("en"),
):
    scan = analyse_leaf(await photo.read())
    hrs = sunmap.sun_hours(lat, lon, facing, season)
    w = water.get_weather(lat, lon)
    need = water.PLANTS.get(plant, water.PLANTS["tomato"])["sun"]
    verdict = rootcause.diagnose(scan["signal"], hrs, need, waterings_per_week, w["humidity"], lang)
    if scan["signal"] == "fungal_spots":
        radar.report(pincode, scan["label"])
    return {"scan": scan, "sun_hours": hrs, "light": sunmap.light_class(hrs), "weather": w,
            "verdict": verdict, "radar": radar.alerts(pincode)}


app.mount("/static", StaticFiles(directory=FRONT), name="static")


@app.get("/")
def index():
    return FileResponse(FRONT / "index.html")
