from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.session import get_db
from app.services.analytics import kpi_snapshot, trend_series, funnel_share, top_hooks_growth, open_alerts

router = APIRouter(prefix="/api/analytics", tags=["analytics"], dependencies=[Depends(require_basic_auth)])


@router.get("/overview")
def overview(days: int = 30, db: Session = Depends(get_db)) -> dict:
    return {
        "kpis": kpi_snapshot(db, days),
        "trends": trend_series(db, days),
        "funnel_share": funnel_share(db, days),
        "top_hooks": top_hooks_growth(db, days),
        "alerts": open_alerts(db),
    }
