from datetime import datetime
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Ad, Advertiser, AdSnapshot, Tag, Feature
from app.services.funnel_detector import detect_all
from app.services.feature_extractor import extract_features


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _bool_from_status(status: str | None) -> bool | None:
    if status is None:
        return None
    if status.lower() == "active":
        return True
    if status.lower() == "inactive":
        return False
    return None


def upsert_ad(db: Session, payload: dict[str, Any]) -> Ad:
    ad_archive_id = payload.get("ad_archive_id")
    if not ad_archive_id:
        raise ValueError("ad_archive_id missing")
    page_id = payload.get("page_id") or "unknown"
    page_name = payload.get("page_name")

    advertiser = db.execute(select(Advertiser).where(Advertiser.page_id == page_id)).scalar_one_or_none()
    now = datetime.utcnow()
    if not advertiser:
        advertiser = Advertiser(
            page_id=page_id,
            page_name=page_name,
            first_seen_at=now,
            last_seen_at=now,
        )
        db.add(advertiser)
        db.flush()
    else:
        advertiser.page_name = page_name or advertiser.page_name
        advertiser.last_seen_at = now

    ad = db.execute(select(Ad).where(Ad.ad_archive_id == ad_archive_id)).scalar_one_or_none()
    is_active = _bool_from_status(payload.get("ad_active_status"))
    start_time = _parse_datetime(payload.get("ad_delivery_start_time"))
    stop_time = _parse_datetime(payload.get("ad_delivery_stop_time"))

    update_fields = {
        "advertiser_id": advertiser.id,
        "start_time": start_time,
        "stop_time": stop_time,
        "is_active": is_active,
        "snapshot_url": payload.get("ad_snapshot_url"),
        "copy_bodies": payload.get("ad_creative_bodies"),
        "link_titles": payload.get("ad_creative_link_titles"),
        "link_descriptions": payload.get("ad_creative_link_descriptions"),
        "link_captions": payload.get("ad_creative_link_captions"),
        "publisher_platforms": payload.get("publisher_platforms"),
        "raw": payload,
        "updated_at": now,
    }

    if ad:
        for key, value in update_fields.items():
            setattr(ad, key, value)
    else:
        ad = Ad(ad_archive_id=ad_archive_id, created_at=now, **update_fields)
        db.add(ad)
        db.flush()

    snapshot = AdSnapshot(ad_id=ad.id, raw=payload, collected_at=now)
    db.add(snapshot)

    if not ad.tags:
        auto_tags = detect_all(ad.copy_bodies)
        ad.tags = Tag(
            ad_id=ad.id,
            niche="unknown",
            funnel_type=auto_tags["funnel_type"],
            offer_type=auto_tags["offer_type"],
            emotion_trigger=auto_tags["emotion_trigger"],
            updated_at=now,
        )

    features_data = extract_features(ad.copy_bodies)
    if ad.features:
        for key, value in features_data.items():
            setattr(ad.features, key, value)
        ad.features.updated_at = now
    else:
        ad.features = Feature(ad_id=ad.id, updated_at=now, **features_data)

    return ad
