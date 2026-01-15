from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Ad, Score
from app.services.hook_extractor import collect_hooks


def _ad_time(ad: Ad) -> datetime:
    return ad.start_time or ad.created_at or datetime.utcnow()


def score_ad(db: Session, ad: Ad) -> Score:
    hook, hook_hash = collect_hooks(ad.copy_bodies)
    now = datetime.utcnow()

    if ad.start_time:
        stop_time = ad.stop_time or now
        runtime_days = max(0, (stop_time - ad.start_time).days)
    else:
        runtime_days = 0

    score_runtime = min(100, runtime_days * 4)

    variants_count = 0
    reuse_count = 0
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

    score_variants = min(100, variants_count * 20)
    score_reuse = min(100, reuse_count * 25)

    funnel_type = "unknown"
    if ad.tags and ad.tags.funnel_type:
        funnel_type = ad.tags.funnel_type
    score_funnel_fit = {
        "whatsapp": 80,
        "instant_form": 70,
        "landing_page": 75,
        "unknown": 40,
    }.get(funnel_type, 40)

    score_total = round(
        0.4 * score_runtime + 0.3 * score_variants + 0.2 * score_reuse + 0.1 * score_funnel_fit
    )

    score = ad.score or Score(ad_id=ad.id)
    score.score_total = score_total
    score.score_runtime = score_runtime
    score.score_variants = score_variants
    score.score_reuse = score_reuse
    score.score_funnel_fit = score_funnel_fit
    score.explanation = {
        "runtime_days": runtime_days,
        "variants_count": variants_count,
        "reuse_count": reuse_count,
        "funnel_type": funnel_type,
        "weights": {
            "runtime": 0.4,
            "variants": 0.3,
            "reuse": 0.2,
            "funnel_fit": 0.1,
        },
    }
    score.updated_at = now
    db.add(score)
    db.flush()

    return score
