import re
from typing import Iterable


PRICE_REGEX = re.compile(r"(ab|nur)\s*\d+\s*(€|eur)", re.IGNORECASE)
COST_SHOCK_REGEX = re.compile(r"\d{3,5}\s*(€|eur)", re.IGNORECASE)


def _flatten_texts(texts: Iterable[str | None]) -> str:
    combined = " ".join([t for t in texts if t])
    return combined.lower()


def detect_offer_type(text: str) -> str:
    if PRICE_REGEX.search(text):
        return "price"
    if COST_SHOCK_REGEX.search(text):
        return "cost_shock"
    if re.search(r"ohne\s+wartezeit|sofort(iger)?\s+schutz", text):
        return "no_waiting"
    if re.search(r"testsieger|stiftung\s*warentest", text):
        return "testsieger"
    if re.search(r"bonus|gutschein|willkommensbonus|cashback", text):
        return "bonus"
    return "unknown"


def detect_funnel_type(text: str) -> str:
    if re.search(r"whatsapp|wa\.me|click to whatsapp", text):
        return "whatsapp"
    if re.search(r"in 2 min|formular|lead|kostenloses angebot", text):
        return "instant_form"
    if re.search(r"tarifrechner|jetzt berechnen|vergleich|angebot anfordern", text):
        return "landing_page"
    return "unknown"


def detect_emotion_trigger(text: str) -> str:
    if COST_SHOCK_REGEX.search(text) and re.search(r"schock|teuer|kostenexplosion", text):
        return "cost_shock"
    if re.search(r"angst|sorgen|notfall|plötzlich|unerwartet", text):
        return "fear"
    if re.search(r"familie|liebling|vierbeiner|fürsorge|gesund", text):
        return "care"
    if re.search(r"beruhigt|abgesichert|sicherheit|entspannung", text):
        return "relief"
    return "unknown"


def detect_all(copy_bodies: dict | list | None) -> dict:
    text = ""
    if isinstance(copy_bodies, dict):
        text = _flatten_texts(copy_bodies.values())
    elif isinstance(copy_bodies, list):
        text = _flatten_texts(copy_bodies)
    return {
        "offer_type": detect_offer_type(text),
        "funnel_type": detect_funnel_type(text),
        "emotion_trigger": detect_emotion_trigger(text),
    }
