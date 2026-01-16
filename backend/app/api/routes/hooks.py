from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import HookLibrary
from app.db.session import get_db

router = APIRouter(prefix="/api/hooks", tags=["hooks"], dependencies=[Depends(require_basic_auth)])


@router.get("")
def list_hooks(q: str | None = None, min_reuse: int | None = None, db: Session = Depends(get_db)) -> dict:
    query = select(HookLibrary)
    if q:
        query = query.where(HookLibrary.hook_text.ilike(f"%{q}%"))
    if min_reuse is not None:
        query = query.where(HookLibrary.reuse_count >= min_reuse)

    hooks = db.execute(query.order_by(HookLibrary.reuse_count.desc())).scalars().all()

    data = [
        {
            "id": str(hook.id),
            "hook_text": hook.hook_text,
            "reuse_count": hook.reuse_count,
            "example_ad_ids": hook.example_ad_ids or [],
        }
        for hook in hooks
    ]
    return {"items": data}
