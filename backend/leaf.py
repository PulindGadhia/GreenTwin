"""Leaf scan.

PROTOTYPE: colour-based lesion detector (no training data needed) that returns an explainable
heat-map. It stands in for the PyTorch CNN + Grad-CAM from the proposal. To plug in the real
model, implement `predict_cnn()` and set USE_CNN = True.
"""
import base64
import io

import numpy as np
from PIL import Image

USE_CNN = False


def predict_cnn(img: Image.Image):  # hook for the trained PlantVillage model
    raise NotImplementedError("Return (label, confidence, heatmap[H,W] in 0..1)")


def analyse_leaf(data: bytes) -> dict:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((384, 384))
    hsv = np.asarray(img.convert("HSV")).astype(float)
    h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255

    leaf = (s > 0.18) & (v > 0.12)
    green = leaf & (h > 70) & (h < 170)
    yellow = leaf & (h >= 40) & (h <= 70)
    brown = leaf & (h < 40) & (v < 0.65)
    dark = leaf & (v < 0.22)
    area = max(int(leaf.sum()), 1)
    f = {"yellow": yellow.sum() / area, "brown": brown.sum() / area,
         "dark": dark.sum() / area, "green": green.sum() / area}

    if f["brown"] + f["dark"] > 0.04:
        label, signal = "Blight-like fungal spots", "fungal_spots"
    elif f["yellow"] > 0.25:
        label, signal = "Chlorosis (yellowing)", "yellowing"
    elif f["yellow"] + f["brown"] > 0.02:
        label, signal = "Mild stress", "mild_stress"
    else:
        label, signal = "Healthy", "healthy"

    bad = (yellow | brown | dark).astype(float)
    bad_total = f["yellow"] + f["brown"] + f["dark"]
    conf = 0.9 if signal == "healthy" else round(min(0.97, 0.6 + 2 * bad_total), 2)
    return {"label": label, "signal": signal, "confidence": conf,
            "fractions": {k: round(float(x), 3) for k, x in f.items()},
            "heatmap_png_b64": _overlay(img, bad)}


def _overlay(img: Image.Image, mask: np.ndarray) -> str:
    rgb = np.asarray(img).astype(float)
    red = np.zeros_like(rgb)
    red[..., 0] = 255
    a = (mask * 0.55)[..., None]
    out = Image.fromarray((rgb * (1 - a) + red * a).astype("uint8"))
    buf = io.BytesIO()
    out.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()
