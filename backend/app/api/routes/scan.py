import logging
import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.session import get_db, SessionLocal
from app.services.meta_client import MetaClientError, fetch_ads
from app.services.ingest import upsert_ad
from app.services.scoring import score_ad
from app.services.hook_library import update_hook_library

router = APIRouter(prefix="/api/scan", tags=["scan"], dependencies=[Depends(require_basic_auth)])
logger = logging.getLogger(__name__)

SCAN_STORE: dict[str, dict[str, Any]] = {}


@router.post("")
async def start_scan(payload: dict, background_tasks: BackgroundTasks) -> dict:
    keywords = payload.get("keywords", [])
    if not keywords:
        raise HTTPException(status_code=400, detail="keywords required")

    scan_id = str(uuid.uuid4())
    SCAN_STORE[scan_id] = {
        "state": "running",
        "keywords_total": len(keywords),
        "keywords_done": 0,
        "ads_upserted": 0,
        "pages_discovered": 0,
        "errors": [],
        "started_at": datetime.utcnow().isoformat(),
    }

    background_tasks.add_task(run_scan, scan_id, payload)
    return {"scan_id": scan_id, "started": True}


@router.get("/{scan_id}")
async def scan_status(scan_id: str) -> dict:
    state = SCAN_STORE.get(scan_id)
    if not state:
        raise HTTPException(status_code=404, detail="scan not found")
    return state


def run_scan(scan_id: str, payload: dict) -> None:
    state = SCAN_STORE[scan_id]
    keywords = payload.get("keywords", [])
    country = payload.get("country", "DE")
    since_days = payload.get("since_days", 90)
    status = payload.get("status", "ALL")
    max_results = payload.get("max_results_per_keyword", 2000)
    pages = set()
    db: Session = SessionLocal()
    try:
        for keyword in keywords:
            try:
                for ad_payload in fetch_ads(
                    search_term=keyword,
                    country=country,
                    status=status,
                    since_days=since_days,
                    max_results=max_results,
                ):
                    ad = upsert_ad(db, ad_payload)
                    score_ad(db, ad)
                    pages.add(ad.advertiser_id)
                    state["ads_upserted"] += 1
                db.commit()
            except MetaClientError as exc:
                logger.exception("scan_failed", extra={"scan_id": scan_id, "keyword": keyword})
                state["errors"].append(str(exc))
            except Exception as exc:  # noqa: BLE001
                logger.exception("scan_keyword_failed", extra={"scan_id": scan_id, "keyword": keyword})
                state["errors"].append(str(exc))
            state["keywords_done"] += 1

        update_hook_library(db)
        db.commit()
        state["pages_discovered"] = len(pages)
        state["state"] = "done"
        state["finished_at"] = datetime.utcnow().isoformat()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        state["state"] = "error"
        state["errors"].append(str(exc))
        logger.exception("scan_failed", extra={"scan_id": scan_id})
    finally:
        db.close()
