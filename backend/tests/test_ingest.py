from datetime import datetime
from app.db.models import Ad, Advertiser
from app.services.ingest import upsert_ad


def test_upsert_dedupe(db_session):
    payload = {
        "ad_archive_id": "123",
        "page_id": "p1",
        "page_name": "Page",
        "ad_delivery_start_time": datetime.utcnow().isoformat(),
        "ad_creative_bodies": {"0": "Hallo"},
    }

    ad = upsert_ad(db_session, payload)
    db_session.commit()

    payload["page_name"] = "Page Updated"
    ad2 = upsert_ad(db_session, payload)
    db_session.commit()

    ads = db_session.query(Ad).all()
    advertisers = db_session.query(Advertiser).all()

    assert len(ads) == 1
    assert len(advertisers) == 1
    assert ad2.advertiser.page_name == "Page Updated"
