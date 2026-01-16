from datetime import datetime
from app.db.models import Advertiser, Ad
from app.services.blueprints import create_blueprint, update_success_signals


def test_create_blueprint(db_session):
    advertiser = Advertiser(page_id="p1", page_name="Test", first_seen_at=datetime.utcnow())
    db_session.add(advertiser)
    db_session.flush()
    ad = Ad(ad_archive_id="a1", advertiser_id=advertiser.id, start_time=datetime.utcnow())
    db_session.add(ad)
    db_session.commit()

    blueprint = create_blueprint(db_session, str(ad.id), "pet_insurance", None)
    update_success_signals(db_session, blueprint)
    db_session.commit()

    assert blueprint.id is not None
    assert blueprint.industry == "pet_insurance"
    assert blueprint.success.scaling_score >= 0
