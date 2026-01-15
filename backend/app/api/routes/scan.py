from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import ScanRun, ScanKeyword
from app.db.session import get_db
from app.schemas import ScanRequest, ScanStatusResponse
from app.worker_tasks import run_scan_task

router = APIRouter(prefix="/api/scan", tags=["scan"], dependencies=[Depends(require_basic_auth)])


@router.post("", response_model=dict)
async def start_scan(payload: ScanRequest, db: Session = Depends(get_db)) -> dict:
    keywords = payload.keywords
    if not keywords:
        raise HTTPException(status_code=400, detail="keywords required")

    scan_run = ScanRun(
        payload=payload.model_dump(),
        state="queued",
        started_at=datetime.utcnow(),
    )
    db.add(scan_run)
    db.commit()
    run_scan_task.delay(str(scan_run.id), payload.model_dump())
    return {"scan_id": str(scan_run.id), "started": True}


@router.get("/{scan_id}", response_model=ScanStatusResponse)
async def scan_status(scan_id: str, db: Session = Depends(get_db)) -> ScanStatusResponse:
    scan = db.get(ScanRun, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="scan not found")
    keywords = db.query(ScanKeyword).filter(ScanKeyword.scan_run_id == scan.id).all()
    return {
        "state": scan.state,
        "keywords_total": len(scan.payload.get("keywords", [])) if scan.payload else 0,
        "keywords_done": len(keywords),
        "ads_upserted": sum(k.upserted_count for k in keywords),
        "pages_discovered": sum(k.unique_pages for k in keywords),
        "errors": scan.errors or [],
        "started_at": scan.started_at,
        "finished_at": scan.finished_at,
    }
