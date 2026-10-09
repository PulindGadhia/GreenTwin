# GreenTwin 🌱
**AI Urban Farming Assistant (PS-04), Code Carnival 3.0, ADSC, Atmiya University**

An AI plant doctor that finds **why** a plant is sick, not just **what** it has. It fuses a leaf photo,
balcony sunlight, watering habits and live weather into one root-cause verdict with an organic-first fix,
in English, Hindi and Gujarati.

## Features in this prototype
| Feature | Where | Status |
|---|---|---|
| Root-Cause Leaf Doctor + explainable heat-map | `backend/leaf.py`, `backend/rootcause.py` | Working (colour-based scanner; CNN hook ready) |
| Balcony Sun-Map (sun-path maths) | `backend/sunmap.py` | Working (pvlib) |
| Rain-Smart Water Budget | `backend/water.py` | Working (Open-Meteo, offline fallback) |
| Neighbourhood Disease Radar | `backend/radar.py` | Working (in-memory) |
| Multilingual fixes (EN/HI/GU) | `backend/rootcause.py` | Working |

**Planned next:** PyTorch CNN trained on PlantVillage (tomato, chilli, mint) + Grad-CAM, Supabase storage,
React PWA, WhatsApp bot, voice input.

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Open http://localhost:8000 and upload any leaf photo. API docs at http://localhost:8000/docs.

Test: `pytest -q`

## Plugging in the real model
`backend/leaf.py` has `predict_cnn()` and a `USE_CNN` flag. Train on PlantVillage in Google Colab,
export the weights, load them there, and return `(label, confidence, heatmap)`. Nothing else changes.

## Architecture
`Browser (leaf photo + balcony info) -> FastAPI -> [leaf scan | sun-path | water budget] -> Root-Cause Engine -> verdict + action plan`

## Team
Team Leader: Zohair Sadikot · [add members]

## License
MIT
