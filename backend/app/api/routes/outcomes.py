from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import CampaignOutcome
from app.db.session import get_db

router = APIRouter(prefix="/api/outcomes", tags=["outcomes"], dependencies=[Depends(require_basic_auth)])


@router.post("")
def create_outcome(payload: dict, db: Session = Depends(get_db)) -> dict:
    outcome = CampaignOutcome(
        blueprint_id=payload.get("blueprint_id"),
        ad_id=payload.get("ad_id"),
        leads_count=payload.get("leads_count"),
        qualified_leads_count=payload.get("qualified_leads_count"),
        sales_count=payload.get("sales_count"),
        cpl=payload.get("cpl"),
        notes=payload.get("notes"),
    )
    db.add(outcome)
    db.commit()
    return {"id": str(outcome.id)}


@router.get("")
def list_outcomes(db: Session = Depends(get_db)) -> dict:
    items = db.query(CampaignOutcome).order_by(CampaignOutcome.created_at.desc()).all()
    return {
        "items": [
            {
                "id": str(item.id),
                "blueprint_id": str(item.blueprint_id) if item.blueprint_id else None,
                "ad_id": str(item.ad_id) if item.ad_id else None,
                "leads_count": item.leads_count,
                "qualified_leads_count": item.qualified_leads_count,
                "sales_count": item.sales_count,
                "cpl": item.cpl,
                "notes": item.notes,
                "created_at": item.created_at,
            }
            for item in items
        ]
    }
