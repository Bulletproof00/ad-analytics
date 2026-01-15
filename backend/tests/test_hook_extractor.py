from app.services.hook_extractor import extract_hook, normalize_hook, hook_hash


def test_extract_hook():
    bodies = {"0": "Erste Zeile. Zweite Zeile."}
    hook = extract_hook(bodies)
    assert hook == "Erste Zeile"


def test_normalize_hook():
    assert normalize_hook("  Hallo   Welt ") == "hallo welt"


def test_hook_hash_stable():
    assert hook_hash("Hallo") == hook_hash("hallo")
