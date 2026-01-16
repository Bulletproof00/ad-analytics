from datetime import datetime, timedelta
from app.db.models import Advertiser, Ad
from app.services.creative_evolution import creative_lineage


def test_creative_lineage_groups(db_session):
    advertiser = Advertiser(page_id="p1", page_name="Test", first_seen_at=datetime.utcnow())
    db_session.add(advertiser)
    db_session.flush()
    ad1 = Ad(ad_archive_id="a1", advertiser_id=advertiser.id, start_time=datetime.utcnow(), copy_bodies={"0": "Hook A"})
    ad2 = Ad(ad_archive_id="a2", advertiser_id=advertiser.id, start_time=datetime.utcnow() + timedelta(days=1), copy_bodies={"0": "Hook A updated"})
    db_session.add_all([ad1, ad2])
    db_session.commit()

    result = creative_lineage(db_session, str(advertiser.id))
    assert result["lineage"]
