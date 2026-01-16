from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Ad, Score
from app.services.hook_extractor import collect_hooks
from app.services.settings_service import get_settings


def _ad_time(ad: Ad) -> datetime:
    return ad.start_time or ad.created_at or datetime.utcnow()


def _compute_saturation(db: Session, hook_hash: str, now: datetime) -> int:
    cutoff_current = now - timedelta(days=14)
    cutoff_prev = now - timedelta(days=28)
    ads = db.execute(select(Ad)).scalars().all()
    current_pages = set()
    previous_pages = set()
    for ad in ads:
        if not ad.copy_bodies:
            continue
        _, other_hash = collect_hooks(ad.copy_bodies)
        if other_hash != hook_hash:
            continue
        ad_time = _ad_time(ad)
        if ad_time >= cutoff_current:
            current_pages.add(ad.advertiser_id)
        elif cutoff_prev <= ad_time < cutoff_current:
            previous_pages.add(ad.advertiser_id)
    reuse_count = len(current_pages)
    prev_count = len(previous_pages)
    growth_rate = (reuse_count - prev_count) / max(prev_count, 1)
    reuse_score = min(60, reuse_count * 10)
    growth_score = min(40, max(0, growth_rate * 40))
    return int(min(100, reuse_score + growth_score))


def score_ad(db: Session, ad: Ad) -> Score:
    _, hook_hash = collect_hooks(ad.copy_bodies)
    now = datetime.utcnow()
    settings = get_settings(db)
    weights = settings.get("scoring", {}).get("weights", {})
    funnel_fit_map = settings.get("scoring", {}).get("funnel_fit", {})

    if ad.start_time:
        stop_time = ad.stop_time or now
        runtime_days = max(0, (stop_time - ad.start_time).days)
    else:
        runtime_days = 0

    score_runtime = min(100, runtime_days * 4)

    variants_count = 0
    reuse_count = 0
    saturation_index = 0
    if hook_hash:
        cutoff = now - timedelta(days=365)
        ads = db.execute(select(Ad)).scalars().all()
        variants = []
        reuse_advertisers = set()
        for other in ads:
            if other.id == ad.id:
                continue
            if _ad_time(other) < cutoff:
                continue
            _, other_hash = collect_hooks(other.copy_bodies)
            if other_hash != hook_hash:
                continue
            reuse_advertisers.add(other.advertiser_id)
            if other.advertiser_id == ad.advertiser_id:
                variants.append(other)
        variants_count = len(variants)
        reuse_count = len(reuse_advertisers)
        saturation_index = _compute_saturation(db, hook_hash, now)

    score_variants = min(100, variants_count * 20)
    score_reuse = min(100, reuse_count * 25)

    funnel_type = "unknown"
    if ad.tags and ad.tags.funnel_type:
        funnel_type = ad.tags.funnel_type
    score_funnel_fit = funnel_fit_map.get(funnel_type, 40)

    score_total = round(
        weights.get("runtime", 0.4) * score_runtime
        + weights.get("variants", 0.3) * score_variants
        + weights.get("reuse", 0.2) * score_reuse
        + weights.get("funnel_fit", 0.1) * score_funnel_fit
    )

    score = ad.score or Score(ad_id=ad.id)
    score.score_total = score_total
    score.score_runtime = score_runtime
    score.score_variants = score_variants
    score.score_reuse = score_reuse
    score.score_funnel_fit = score_funnel_fit
    score.saturation_index = saturation_index
    score.explanation = {
        "runtime_days": runtime_days,
        "variants_count": variants_count,
        "reuse_count": reuse_count,
        "funnel_type": funnel_type,
        "saturation_index": saturation_index,
        "weights": {
            "runtime": weights.get("runtime", 0.4),
            "variants": weights.get("variants", 0.3),
            "reuse": weights.get("reuse", 0.2),
            "funnel_fit": weights.get("funnel_fit", 0.1),
        },
    }
    score.updated_at = now
    db.add(score)
    db.flush()

    return score
