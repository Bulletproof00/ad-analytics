from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.session import get_db
from app.services.creative_evolution import creative_lineage

router = APIRouter(prefix="/api/creative-evolution", tags=["creative-evolution"], dependencies=[Depends(require_basic_auth)])


@router.get("")
def get_lineage(advertiser_id: str, db: Session = Depends(get_db)) -> dict:
    return creative_lineage(db, advertiser_id)
