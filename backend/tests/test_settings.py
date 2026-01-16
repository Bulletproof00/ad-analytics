from app.services.settings_service import get_settings, upsert_setting


def test_settings_default_and_override(db_session):
    settings = get_settings(db_session)
    assert settings["scoring"]["winner_threshold"] == 75
    upsert_setting(db_session, "scoring", {"winner_threshold": 80})
    db_session.commit()
    settings = get_settings(db_session)
    assert settings["scoring"]["winner_threshold"] == 80
