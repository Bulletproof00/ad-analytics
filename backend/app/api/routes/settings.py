from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.session import get_db
from app.schemas import SettingPayload
from app.services.settings_service import get_settings, upsert_setting

router = APIRouter(prefix="/api/settings", tags=["settings"], dependencies=[Depends(require_basic_auth)])


@router.get("")
def list_settings(db: Session = Depends(get_db)) -> dict:
    return get_settings(db)


@router.post("")
def update_setting(payload: SettingPayload, db: Session = Depends(get_db)) -> dict:
    upsert_setting(db, payload.key, payload.value)
    db.commit()
    return {"status": "ok"}
