from app.services.feature_extractor import extract_features


def test_extract_features_metrics():
    copy_bodies = {"0": "Jetzt sparen! Ohne Wartezeit."}
    features = extract_features(copy_bodies)
    assert features["hook_text"]
    assert features["copy_metrics"]["cta_position"] in {"early", "mid", "late", "none"}
    assert features["offer_type"] in {"price", "no_waiting", "unknown", "bonus", "testsieger", "cost_shock"}
