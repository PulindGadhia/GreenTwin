"""Root-Cause Engine: fuses leaf signal + sun + watering log + weather into ONE verdict (WHY, not just WHAT)."""

FIXES = {
    "overwatering": {"en": "Roots are too wet. Skip watering for 2-3 days and make sure the pot drains.",
                     "hi": "जड़ें ज़्यादा गीली हैं। 2-3 दिन पानी न दें और गमले में निकासी जाँचें।",
                     "gu": "મૂળ વધુ ભીના છે. 2-3 દિવસ પાણી ન આપો અને કુંડામાં નિકાસ તપાસો."},
    "underwatering": {"en": "Plant is thirsty. Water deeply in the morning and mulch the soil.",
                      "hi": "पौधा प्यासा है। सुबह गहरा पानी दें और मिट्टी पर मल्च बिछाएँ।",
                      "gu": "છોડ તરસ્યો છે. સવારે ઊંડું પાણી આપો અને માટી પર મલ્ચ કરો."},
    "low_light": {"en": "Not enough sun. Move it to a spot with 6+ hours of direct sun (see Sun-Map).",
                  "hi": "धूप कम है। इसे 6+ घंटे सीधी धूप वाली जगह रखें (Sun-Map देखें)।",
                  "gu": "તડકો ઓછો છે. 6+ કલાક સીધો તડકો મળે ત્યાં મૂકો (Sun-Map જુઓ)."},
    "fungal": {"en": "Fungal infection likely. Remove affected leaves, spray neem oil or 1:10 diluted buttermilk, keep leaves dry.",
               "hi": "फफूंद संक्रमण संभव है। प्रभावित पत्ते हटाएँ, नीम तेल या 1:10 पतली छाछ छिड़कें, पत्ते सूखे रखें।",
               "gu": "ફૂગનો ચેપ શક્ય છે. અસરગ્રસ્ત પાન કાઢો, લીમડાનું તેલ કે 1:10 છાશ છાંટો, પાન સૂકા રાખો."},
    "healthy": {"en": "Looking good. Keep the current routine.",
                "hi": "सब ठीक है। मौजूदा देखभाल जारी रखें।",
                "gu": "બધું સારું છે. હાલની સંભાળ ચાલુ રાખો."},
    "nutrient": {"en": "Likely nutrient deficiency. Add compost or diluted vermiwash every 2 weeks.",
                 "hi": "पोषक तत्वों की कमी संभव है। हर 2 हफ्ते कम्पोस्ट या वर्मीवॉश दें।",
                 "gu": "પોષક તત્વોની ઊણપ શક્ય છે. દર 2 અઠવાડિયે કમ્પોસ્ટ કે વર્મીવોશ આપો."},
}


def diagnose(signal: str, sun_hrs: float, sun_need: str, waterings_per_week: int,
             humidity: float, lang: str = "en") -> dict:
    need_hrs = 6 if sun_need == "full" else 3
    scores, evidence = {}, {}

    def add(cause, pts, why):
        scores[cause] = scores.get(cause, 0) + pts
        evidence.setdefault(cause, []).append(why)

    if signal == "healthy":
        add("healthy", 3, "Leaf looks healthy")
    if signal in ("yellowing", "mild_stress"):
        if waterings_per_week >= 6:
            add("overwatering", 2, f"Watered {waterings_per_week}x/week")
        if waterings_per_week <= 1:
            add("underwatering", 2, f"Only {waterings_per_week} watering(s)/week")
        if sun_hrs < need_hrs:
            add("low_light", 2, f"Only {sun_hrs} h sun, plant needs {need_hrs}+ h")
        add("nutrient", 1, "Yellowing despite normal water and light points to nutrients")
    if signal == "fungal_spots":
        add("fungal", 2, "Dark/brown spots on the leaf")
        if humidity > 70:
            add("fungal", 2, f"High humidity ({humidity:.0f}%) favours fungus")
        if waterings_per_week >= 6:
            add("fungal", 1, "Frequent watering keeps leaves damp")
        if sun_hrs < need_hrs:
            add("low_light", 1, f"Low sun ({sun_hrs} h) slows drying")

    cause = max(scores, key=scores.get)
    return {"cause": cause, "confidence": round(scores[cause] / sum(scores.values()), 2),
            "evidence": evidence[cause], "fix": FIXES[cause].get(lang, FIXES[cause]["en"]),
            "alternatives": [c for c in scores if c != cause]}
