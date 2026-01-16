import pytest
from app.services.blueprints import detect_destination_type, compute_scaling_score, validate_snapshot_url


def test_destination_type_detection():
    assert detect_destination_type("https://wa.me/123") == "whatsapp"
    assert detect_destination_type("https://facebook.com/leadgen") == "meta_lead_form"
    assert detect_destination_type("https://example.com/rechner") == "calculator_quiz"
    assert detect_destination_type("https://example.com") == "landing_page"


def test_scaling_score():
    score, breakdown = compute_scaling_score(30, 3, "whatsapp", "low", True)
    assert score >= 80
    assert breakdown["total"] == score


def test_snapshot_ssrf_guard():
    with pytest.raises(ValueError):
        validate_snapshot_url("file:///etc/passwd")
    with pytest.raises(ValueError):
        validate_snapshot_url("http://127.0.0.1/private")
