from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import Alert
from app.db.session import get_db

router = APIRouter(prefix="/api/alerts", tags=["alerts"], dependencies=[Depends(require_basic_auth)])


@router.get("")
def list_alerts(db: Session = Depends(get_db)) -> dict:
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    return {
        "items": [
            {
                "id": str(alert.id),
                "type": alert.type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "status": alert.status,
                "created_at": alert.created_at,
            }
            for alert in alerts
        ]
    }


@router.post("/{alert_id}")
def update_alert(alert_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="alert not found")
    status = payload.get("status")
    if status:
        alert.status = status
        alert.updated_at = datetime.utcnow()
        db.add(alert)
        db.commit()
    return {"status": "ok"}
