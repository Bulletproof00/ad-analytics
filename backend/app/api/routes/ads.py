from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func, select, or_
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import Ad, Advertiser, Score, Tag
from app.db.session import get_db
from app.services.hook_extractor import hook_preview, collect_hooks
from app.services.scoring import score_ad

router = APIRouter(prefix="/api/ads", tags=["ads"], dependencies=[Depends(require_basic_auth)])


@router.get("")
def list_ads(
    q: str | None = None,
    min_score: int | None = None,
    is_winner: bool | None = None,
    funnel_type: str | None = None,
    offer_type: str | None = None,
    emotion_trigger: str | None = None,
    niche: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page_name: str | None = None,
    page_id: str | None = None,
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
) -> dict:
    filters = []
    if q:
        filters.append(Ad.ad_archive_id.ilike(f"%{q}%"))
    if date_from:
        filters.append(Ad.start_time >= datetime.fromisoformat(date_from))
    if date_to:
        filters.append(Ad.start_time <= datetime.fromisoformat(date_to))

    query = select(Ad).join(Advertiser)
    if filters:
        query = query.where(and_(*filters))
    if page_name:
        query = query.where(Advertiser.page_name.ilike(f"%{page_name}%"))
    if page_id:
        query = query.where(Advertiser.page_id == page_id)

    if min_score is not None:
        query = query.join(Score, isouter=True).where(Score.score_total >= min_score)
    if is_winner is not None:
        query = query.join(Score, isouter=True).join(Tag, isouter=True).where(
            or_(Tag.is_winner == is_winner, Score.score_total >= 75)
        )
    if funnel_type:
        query = query.join(Tag, isouter=True).where(Tag.funnel_type == funnel_type)
    if offer_type:
        query = query.join(Tag, isouter=True).where(Tag.offer_type == offer_type)
    if emotion_trigger:
        query = query.join(Tag, isouter=True).where(Tag.emotion_trigger == emotion_trigger)
    if niche:
        query = query.join(Tag, isouter=True).where(Tag.niche == niche)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()

    items = db.execute(
        query.order_by(Ad.created_at.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    ).scalars().all()

    data = []
    for ad in items:
        hook = hook_preview(ad.copy_bodies)
        data.append(
            {
                "id": str(ad.id),
                "score_total": ad.score.score_total if ad.score else 0,
                "page_name": ad.advertiser.page_name if ad.advertiser else None,
                "start_time": ad.start_time,
                "stop_time": ad.stop_time,
                "hook_preview": hook,
                "funnel_type": ad.tags.funnel_type if ad.tags else "unknown",
                "offer_type": ad.tags.offer_type if ad.tags else "unknown",
                "snapshot_url": ad.snapshot_url,
            }
        )

    return {"items": data, "total": total, "page": page, "page_size": page_size}


@router.get("/{ad_id}")
def get_ad(ad_id: str, db: Session = Depends(get_db)) -> dict:
    ad = db.execute(select(Ad).where(Ad.id == ad_id)).scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="ad not found")
    if not ad.score:
        score_ad(db, ad)
        db.commit()

    hook, hook_hash = collect_hooks(ad.copy_bodies)
    variants_count = 0
    reuse_count = 0
    if hook_hash:
        cutoff = datetime.utcnow() - timedelta(days=365)
        ads = db.execute(select(Ad)).scalars().all()
        advertisers = set()
        for other in ads:
            if other.id == ad.id:
                continue
            if (other.start_time or other.created_at) < cutoff:
                continue
            _, other_hash = collect_hooks(other.copy_bodies)
            if other_hash != hook_hash:
                continue
            advertisers.add(other.advertiser_id)
            if other.advertiser_id == ad.advertiser_id:
                variants_count += 1
        reuse_count = len(advertisers)

    return {
        "id": str(ad.id),
        "ad_archive_id": ad.ad_archive_id,
        "page_id": ad.advertiser.page_id if ad.advertiser else None,
        "page_name": ad.advertiser.page_name if ad.advertiser else None,
        "start_time": ad.start_time,
        "stop_time": ad.stop_time,
        "snapshot_url": ad.snapshot_url,
        "copy_bodies": ad.copy_bodies,
        "link_titles": ad.link_titles,
        "link_descriptions": ad.link_descriptions,
        "link_captions": ad.link_captions,
        "publisher_platforms": ad.publisher_platforms,
        "tags": {
            "niche": ad.tags.niche if ad.tags else "unknown",
            "funnel_type": ad.tags.funnel_type if ad.tags else "unknown",
            "offer_type": ad.tags.offer_type if ad.tags else "unknown",
            "emotion_trigger": ad.tags.emotion_trigger if ad.tags else "unknown",
            "is_winner": ad.tags.is_winner if ad.tags else False,
            "notes": ad.tags.notes if ad.tags else None,
        },
        "score": {
            "score_total": ad.score.score_total if ad.score else 0,
            "score_runtime": ad.score.score_runtime if ad.score else 0,
            "score_variants": ad.score.score_variants if ad.score else 0,
            "score_reuse": ad.score.score_reuse if ad.score else 0,
            "score_funnel_fit": ad.score.score_funnel_fit if ad.score else 0,
            "explanation": ad.score.explanation if ad.score else {},
        },
        "hook": hook,
        "reuse_count": reuse_count,
        "variants_count": variants_count,
    }


@router.post("/{ad_id}/tags")
def update_tags(ad_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    ad = db.execute(select(Ad).where(Ad.id == ad_id)).scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="ad not found")
    if not ad.tags:
        ad.tags = Tag(ad_id=ad.id)

    for field in ["niche", "funnel_type", "offer_type", "emotion_trigger", "is_winner", "notes"]:
        if field in payload:
            setattr(ad.tags, field, payload[field])
    ad.tags.updated_at = datetime.utcnow()
    db.add(ad.tags)
    db.commit()
    return {"status": "ok"}
