import re
from datetime import datetime
from typing import Iterable
from app.services.hook_extractor import collect_hooks
from app.services.funnel_detector import detect_all

EMOJI_REGEX = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
CTA_REGEX = re.compile(r"(jetzt|jetzt berechnen|mehr erfahren|angebot anfordern|klick|start)")


def _flatten_text(copy_bodies: dict | list | None) -> str:
    if isinstance(copy_bodies, dict):
        values = [str(v) for v in copy_bodies.values() if v]
    elif isinstance(copy_bodies, list):
        values = [str(v) for v in copy_bodies if v]
    else:
        values = []
    return " ".join(values)


def _sentence_lengths(text: str) -> list[int]:
    sentences = [s.strip() for s in re.split(r"[.!?\n]", text) if s.strip()]
    return [len(s) for s in sentences]


def _emoji_density(text: str) -> float:
    if not text:
        return 0.0
    emojis = EMOJI_REGEX.findall(text)
    return round(len(emojis) / max(len(text), 1), 4)


def _has_numbers(text: str) -> bool:
    return bool(re.search(r"\d", text))


def _pronoun_style(text: str) -> str:
    text_lower = text.lower()
    if re.search(r"\bdu\b|\bdein\b|\bdich\b", text_lower):
        return "du"
    if re.search(r"\bsie\b|\bihr\b|\bihnen\b", text_lower):
        return "sie"
    return "unknown"


def _cta_position(text: str) -> str:
    if not text:
        return "unknown"
    match = CTA_REGEX.search(text.lower())
    if not match:
        return "none"
    index = match.start()
    ratio = index / max(len(text), 1)
    if ratio < 0.33:
        return "early"
    if ratio < 0.66:
        return "mid"
    return "late"


def _hook_type(hook: str | None) -> str:
    if not hook:
        return "unknown"
    hook_lower = hook.lower()
    if hook_lower.endswith("?"):
        return "question"
    if re.search(r"\d", hook_lower):
        return "stat"
    if re.search(r"sofort|jetzt|schnell", hook_lower):
        return "urgent"
    return "statement"


def extract_features(copy_bodies: dict | list | None) -> dict:
    text = _flatten_text(copy_bodies)
    hook, hook_hash = collect_hooks(copy_bodies)
    tags = detect_all(copy_bodies)
    sentence_lengths = _sentence_lengths(text)
    metrics = {
        "sentence_lengths": sentence_lengths,
        "avg_sentence_length": round(sum(sentence_lengths) / len(sentence_lengths), 2) if sentence_lengths else 0,
        "emoji_density": _emoji_density(text),
        "has_numbers": _has_numbers(text),
        "pronoun_style": _pronoun_style(text),
        "cta_position": _cta_position(text),
        "hook_type": _hook_type(hook),
        "text_length": len(text),
    }
    return {
        "hook_text": hook,
        "hook_hash": hook_hash,
        "offer_type": tags["offer_type"],
        "emotion_trigger": tags["emotion_trigger"],
        "funnel_type": tags["funnel_type"],
        "creative_type": "unknown",
        "copy_metrics": metrics,
    }
