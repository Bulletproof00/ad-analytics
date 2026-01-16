from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import Ad, Advertiser, HookLibrary, Score
from app.db.session import get_db

router = APIRouter(prefix="/api/stats", tags=["stats"], dependencies=[Depends(require_basic_auth)])


@router.get("")
def get_stats(db: Session = Depends(get_db)) -> dict:
    total_ads = db.execute(select(func.count(Ad.id))).scalar_one()
    total_pages = db.execute(select(func.count(Advertiser.id))).scalar_one()
    winners_count = db.execute(select(func.count(Score.ad_id)).where(Score.score_total >= 75)).scalar_one()

    since = datetime.utcnow() - timedelta(days=7)
    new_ads_last_7d = db.execute(select(func.count(Ad.id)).where(Ad.created_at >= since)).scalar_one()

    top_hooks = db.execute(
        select(HookLibrary)
        .order_by(HookLibrary.reuse_count.desc())
        .limit(5)
    ).scalars().all()

    return {
        "total_ads": total_ads,
        "total_pages": total_pages,
        "winners_count": winners_count,
        "new_ads_last_7d": new_ads_last_7d,
        "top_hooks": [
            {"hook_text": hook.hook_text, "reuse_count": hook.reuse_count}
            for hook in top_hooks
        ],
    }
