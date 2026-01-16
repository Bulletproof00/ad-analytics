from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import TestQueueItem
from app.db.session import get_db
from app.schemas import ExportRequest

router = APIRouter(prefix="/api/export", tags=["export"], dependencies=[Depends(require_basic_auth)])


@router.post("")
def build_export(payload: ExportRequest, db: Session = Depends(get_db)) -> dict:
    items = db.query(TestQueueItem).filter(TestQueueItem.id.in_(payload.test_queue_ids)).all()
    export = {
        "campaign_plan": {
            "niche": payload.niche,
            "funnel_type": payload.funnel_type,
            "budget": payload.budget,
            "objective": payload.objective,
            "created_at": datetime.utcnow().isoformat(),
        },
        "ad_copy": [item.payload for item in items],
        "ugc_script": "UGC script placeholder",
        "whatsapp_flow": "WhatsApp flow placeholder",
        "tracking_plan": "UTM plan placeholder",
    }
    return export
