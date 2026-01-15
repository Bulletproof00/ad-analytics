from datetime import datetime, timedelta
from app.db.models import Ad, Advertiser, Tag
from app.services.scoring import score_ad


def test_saturation_index(db_session):
    advertiser = Advertiser(page_id="1", page_name="Test", first_seen_at=datetime.utcnow())
    db_session.add(advertiser)
    db_session.flush()
    base = Ad(
        ad_archive_id="a1",
        advertiser_id=advertiser.id,
        start_time=datetime.utcnow() - timedelta(days=5),
        copy_bodies={"0": "Hook"},
    )
    base.tags = Tag(ad_id=base.id, funnel_type="whatsapp")
    db_session.add(base)
    db_session.commit()
    score = score_ad(db_session, base)
    assert score.saturation_index >= 0
