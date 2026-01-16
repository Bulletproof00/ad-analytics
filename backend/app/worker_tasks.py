import logging
import time
from datetime import datetime
from celery import shared_task
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import ScanRun, ScanKeyword
from app.services.meta_client import MetaClientError, fetch_ads
from app.services.ingest import upsert_ad
from app.services.scoring import score_ad
from app.services.hook_library import update_hook_library

logger = logging.getLogger(__name__)


@shared_task
def run_scan_task(scan_run_id: str, payload: dict) -> None:
    db: Session = SessionLocal()
    scan = db.get(ScanRun, scan_run_id)
    if not scan:
        return
    keywords = payload.get("keywords", [])
    country = payload.get("country", "DE")
    since_days = payload.get("since_days", 90)
    status = payload.get("status", "ALL")
    max_results = payload.get("max_results_per_keyword", 2000)
    scan.summary = scan.summary or {}
    scan.errors = scan.errors or []
    scan.state = "running"
    db.commit()

    try:
        for keyword in keywords:
            keyword_start = time.monotonic()
            fetched_count = 0
            upserted_count = 0
            pages = set()
            try:
                for ad_payload in fetch_ads(
                    search_term=keyword,
                    country=country,
                    status=status,
                    since_days=since_days,
                    max_results=max_results,
                ):
                    fetched_count += 1
                    ad = upsert_ad(db, ad_payload)
                    score_ad(db, ad)
                    pages.add(ad.advertiser_id)
                    upserted_count += 1
                db.commit()
            except MetaClientError as exc:
                logger.exception("scan_failed", extra={"scan_id": scan_run_id, "keyword": keyword})
                scan.errors.append(str(exc))
            except Exception as exc:  # noqa: BLE001
                logger.exception("scan_keyword_failed", extra={"scan_id": scan_run_id, "keyword": keyword})
                scan.errors.append(str(exc))
            runtime_ms = int((time.monotonic() - keyword_start) * 1000)
            keyword_row = ScanKeyword(
                scan_run_id=scan.id,
                keyword=keyword,
                fetched_count=fetched_count,
                upserted_count=upserted_count,
                unique_pages=len(pages),
                runtime_ms=runtime_ms,
            )
            db.add(keyword_row)
            db.commit()

        update_hook_library(db)
        db.commit()
        scan.state = "done"
        scan.finished_at = datetime.utcnow()
        scan.summary = {
            "keywords_total": len(keywords),
            "ads_upserted": sum(k.upserted_count for k in scan.keywords),
            "pages_discovered": sum(k.unique_pages for k in scan.keywords),
        }
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        scan.state = "error"
        scan.errors = (scan.errors or []) + [str(exc)]
        scan.finished_at = datetime.utcnow()
        db.commit()
        logger.exception("scan_failed", extra={"scan_id": scan_run_id})
    finally:
        db.close()
