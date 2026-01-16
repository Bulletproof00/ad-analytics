from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.session import get_db
from app.services.anti_blueprints import detect_failures

router = APIRouter(prefix="/api/anti-blueprints", tags=["anti-blueprints"], dependencies=[Depends(require_basic_auth)])


@router.get("")
def list_failures(db: Session = Depends(get_db)) -> dict:
    return {"items": detect_failures(db)}
