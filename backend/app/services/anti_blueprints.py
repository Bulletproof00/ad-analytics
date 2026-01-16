from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Ad, Score, Tag, Blueprint


def detect_failures(db: Session) -> list[dict]:
    ads = db.execute(select(Ad)).scalars().all()
    failures = []
    for ad in ads:
        if not ad.start_time:
            continue
        runtime_days = (ad.stop_time or datetime.utcnow() - ad.start_time).days
        if runtime_days >= 3:
            continue
        failures.append(
            {
                "ad_id": str(ad.id),
                "runtime_days": runtime_days,
                "reason": "short_runtime",
            }
        )
    return failures
