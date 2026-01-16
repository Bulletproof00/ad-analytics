from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import Feature, Ad
from app.db.session import get_db

router = APIRouter(prefix="/api/funnels", tags=["funnels"], dependencies=[Depends(require_basic_auth)])


@router.get("")
def funnel_stats(days: int = 90, db: Session = Depends(get_db)) -> dict:
    since = datetime.utcnow() - timedelta(days=days)
    rows = db.execute(
        select(Feature.funnel_type, func.count(Feature.id))
        .join(Ad, Ad.id == Feature.ad_id)
        .where(Ad.created_at >= since)
        .group_by(Feature.funnel_type)
    ).all()
    return {
        "items": [
            {"funnel_type": row[0] or "unknown", "count": row[1]}
            for row in rows
        ]
    }
