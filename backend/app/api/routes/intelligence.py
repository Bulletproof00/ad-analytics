import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.session import get_db
from app.services.intelligence import parameter_strength, pattern_combos, trend_overview, clear_cache

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"], dependencies=[Depends(require_basic_auth)])


@router.get("/parameter-strength")
def parameter_strength_route(industry: str | None = None, db: Session = Depends(get_db)) -> dict:
    return parameter_strength(db, industry)


@router.get("/pattern-combos")
def pattern_combos_route(industry: str | None = None, db: Session = Depends(get_db)) -> dict:
    return {"items": pattern_combos(db, industry)}


@router.get("/trends")
def trends_route(days: int = 90, db: Session = Depends(get_db)) -> dict:
    return trend_overview(db, days)


@router.get("/parameter-strength.csv")
def parameter_strength_csv(industry: str | None = None, db: Session = Depends(get_db)) -> StreamingResponse:
    data = parameter_strength(db, industry)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["type", "feature", "avg_score", "lift", "sample"])
    for row in data.get("hook_type", []):
        writer.writerow(["hook_type", row["feature"], row["avg_score"], row["lift"], row["sample"]])
    for row in data.get("destination_type", []):
        writer.writerow(["destination_type", row["feature"], row["avg_score"], row["lift"], row["sample"]])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv")


@router.get("/pattern-combos.csv")
def pattern_combos_csv(industry: str | None = None, db: Session = Depends(get_db)) -> StreamingResponse:
    items = pattern_combos(db, industry)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["hook_type", "destination_type", "count"])
    for item in items:
        writer.writerow([item["hook_type"], item["destination_type"], item["count"]])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv")


@router.post("/recompute")
def recompute() -> dict:
    clear_cache()
    return {"status": "ok"}
