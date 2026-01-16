from datetime import datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db.models import Ad, Advertiser, HookLibrary, Score, Feature, Alert, ScanKeyword


def kpi_snapshot(db: Session, since_days: int) -> dict:
    since = datetime.utcnow() - timedelta(days=since_days)
    total_ads = db.execute(select(func.count(Ad.id))).scalar_one()
    total_pages = db.execute(select(func.count(Advertiser.id))).scalar_one()
    new_ads = db.execute(select(func.count(Ad.id)).where(Ad.created_at >= since)).scalar_one()
    active_ads = db.execute(
        select(func.count(Ad.id)).where((Ad.stop_time.is_(None)) | (Ad.stop_time >= since))
    ).scalar_one()
    winners = db.execute(select(func.count(Score.ad_id)).where(Score.score_total >= 75)).scalar_one()
    saturation_avg = db.execute(select(func.avg(Score.saturation_index))).scalar_one() or 0
    coverage_avg = db.execute(select(func.avg(ScanKeyword.fetched_count))).scalar_one() or 0
    market_velocity = round(new_ads / max(since_days, 1), 2)
    return {
        "total_ads": total_ads,
        "total_pages": total_pages,
        "new_ads": new_ads,
        "active_ads": active_ads,
        "winners": winners,
        "market_velocity": market_velocity,
        "saturation_avg": int(saturation_avg),
        "coverage_health": round(coverage_avg, 2),
    }


def trend_series(db: Session, days: int) -> list[dict]:
    start = datetime.utcnow() - timedelta(days=days)
    rows = db.execute(
        select(func.date_trunc("day", Ad.created_at).label("day"), func.count(Ad.id))
        .where(Ad.created_at >= start)
        .group_by("day")
        .order_by("day")
    ).all()
    return [{"date": row[0].date().isoformat(), "new_ads": row[1]} for row in rows]


def funnel_share(db: Session, days: int) -> list[dict]:
    start = datetime.utcnow() - timedelta(days=days)
    rows = db.execute(
        select(Feature.funnel_type, func.count(Feature.id))
        .join(Ad, Ad.id == Feature.ad_id)
        .where(Ad.created_at >= start)
        .group_by(Feature.funnel_type)
    ).all()
    total = sum(row[1] for row in rows) or 1
    return [
        {"funnel_type": row[0] or "unknown", "count": row[1], "share": round(row[1] / total, 3)}
        for row in rows
    ]


def top_hooks_growth(db: Session, days: int) -> list[dict]:
    rows = db.execute(
        select(HookLibrary).order_by(HookLibrary.reuse_count.desc()).limit(10)
    ).scalars().all()
    return [
        {
            "hook_hash": hook.hook_hash,
            "hook_text": hook.hook_text,
            "reuse_count": hook.reuse_count,
        }
        for hook in rows
    ]


def open_alerts(db: Session) -> list[dict]:
    alerts = db.execute(select(Alert).where(Alert.status == "open").order_by(Alert.created_at.desc())).scalars().all()
    return [
        {
            "id": str(alert.id),
            "type": alert.type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "evidence": alert.evidence or {},
            "status": alert.status,
            "created_at": alert.created_at,
        }
        for alert in alerts
    ]
