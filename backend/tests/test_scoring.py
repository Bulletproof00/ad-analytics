from datetime import datetime, timedelta
from app.db.models import Ad, Advertiser, Tag
from app.services.scoring import score_ad


def test_scoring_runtime(db_session):
    advertiser = Advertiser(page_id="1", page_name="Test", first_seen_at=datetime.utcnow())
    db_session.add(advertiser)
    db_session.flush()
    ad = Ad(
        ad_archive_id="a1",
        advertiser_id=advertiser.id,
        start_time=datetime.utcnow() - timedelta(days=10),
        stop_time=None,
        copy_bodies={"0": "Hook"},
    )
    ad.tags = Tag(ad_id=ad.id, funnel_type="whatsapp")
    db_session.add(ad)
    db_session.commit()

    score = score_ad(db_session, ad)
    assert score.score_runtime == 40
    assert score.score_funnel_fit == 80
