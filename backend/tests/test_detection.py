from app.services.funnel_detector import detect_offer_type, detect_funnel_type, detect_emotion_trigger


def test_offer_detection_price():
    text = "Ab 20 € im Monat"
    assert detect_offer_type(text.lower()) == "price"


def test_funnel_detection_whatsapp():
    text = "Schreib uns bei WhatsApp"
    assert detect_funnel_type(text.lower()) == "whatsapp"


def test_emotion_detection_fear():
    text = "Plötzlich im Notfall"
    assert detect_emotion_trigger(text.lower()) == "fear"
