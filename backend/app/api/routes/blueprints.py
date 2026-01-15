import csv
import io
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import Blueprint, CreativeAnalysis, FunnelAnalysis, OfferPsychology, SuccessSignals
from app.db.session import get_db
from app.services.blueprints import (
    create_blueprint,
    detect_destination_type,
    update_success_signals,
    capture_snapshot,
)

router = APIRouter(prefix="/api/blueprints", tags=["blueprints"], dependencies=[Depends(require_basic_auth)])


@router.post("")
def create_blueprint_route(payload: dict, db: Session = Depends(get_db)) -> dict:
    source_ad_id = payload.get("sourceAdId")
    if not source_ad_id:
        raise HTTPException(status_code=400, detail="sourceAdId required")
    existing = db.execute(select(Blueprint).where(Blueprint.source_ad_id == source_ad_id)).scalar_one_or_none()
    if existing:
        return {"id": str(existing.id)}
    blueprint = create_blueprint(db, source_ad_id, payload.get("industry"), payload.get("title"))
    update_success_signals(db, blueprint)
    db.commit()
    return {"id": str(blueprint.id)}


@router.get("")
def list_blueprints(
    industry: str | None = None,
    destination_type: str | None = None,
    hook_type: str | None = None,
    min_score: int | None = None,
    source_ad_id: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    query = select(Blueprint)
    if industry:
        query = query.where(Blueprint.industry == industry)
    if source_ad_id:
        query = query.where(Blueprint.source_ad_id == source_ad_id)
    blueprints = db.execute(query).scalars().all()
    items = []
    for blueprint in blueprints:
        if destination_type and blueprint.funnel and blueprint.funnel.destination_type != destination_type:
            continue
        if hook_type and blueprint.creative and blueprint.creative.hook_type != hook_type:
            continue
        if min_score is not None and blueprint.success and blueprint.success.scaling_score < min_score:
            continue
        items.append(
            {
                "id": str(blueprint.id),
                "title": blueprint.title,
                "industry": blueprint.industry,
                "scaling_score": blueprint.success.scaling_score if blueprint.success else 0,
                "destination_type": blueprint.funnel.destination_type if blueprint.funnel else "unknown",
                "created_at": blueprint.created_at,
            }
        )
    return {"items": items}


@router.get("/{blueprint_id}")
def get_blueprint(blueprint_id: str, db: Session = Depends(get_db)) -> dict:
    blueprint = db.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="not found")
    creative = blueprint.creative
    funnel = blueprint.funnel
    offer = blueprint.offer
    success = blueprint.success
    return {
        "id": str(blueprint.id),
        "title": blueprint.title,
        "industry": blueprint.industry,
        "notes": blueprint.notes,
        "source_ad_id": str(blueprint.source_ad_id),
        "creative": {
            "creative_type": creative.creative_type,
            "style_type": creative.style_type,
            "aspect_ratio": creative.aspect_ratio,
            "duration_sec": creative.duration_sec,
            "hook_type": creative.hook_type,
            "hook_window": creative.hook_window,
            "story_structure": creative.story_structure,
            "pov": creative.pov,
            "emotions": creative.emotions,
            "cta_type": creative.cta_type,
            "cta_tone": creative.cta_tone,
            "extracted_text": creative.extracted_text,
            "tags_json": creative.tags_json,
        } if creative else {},
        "funnel": {
            "click_url": funnel.click_url,
            "destination_type": funnel.destination_type,
            "lead_fields_count": funnel.lead_fields_count,
            "lead_fields_json": funnel.lead_fields_json,
            "friction_level": funnel.friction_level,
            "snapshot_id": str(funnel.snapshot_id) if funnel.snapshot_id else None,
            "trust_elements_json": funnel.trust_elements_json,
        } if funnel else {},
        "offer": {
            "price_mentioned": offer.price_mentioned,
            "monthly_price_value": offer.monthly_price_value,
            "discount_or_bonus": offer.discount_or_bonus,
            "urgency": offer.urgency,
            "comparison_frame": offer.comparison_frame,
            "primary_frame": offer.primary_frame,
            "notes": offer.notes,
        } if offer else {},
        "success": {
            "ad_run_days": success.ad_run_days,
            "variant_count_est": success.variant_count_est,
            "repetition_signal": success.repetition_signal,
            "scaling_score": success.scaling_score,
            "scoring_breakdown_json": success.scoring_breakdown_json,
        } if success else {},
        "snapshots": [
            {"id": str(snapshot.id), "url": snapshot.url, "captured_at": snapshot.captured_at}
            for snapshot in blueprint.snapshots
        ],
    }


@router.put("/{blueprint_id}")
def update_blueprint(blueprint_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    blueprint = db.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="not found")
    for field in ["title", "industry", "notes"]:
        if field in payload:
            setattr(blueprint, field, payload[field])
    blueprint.updated_at = datetime.utcnow()
    db.add(blueprint)
    db.commit()
    return {"status": "ok"}


@router.put("/{blueprint_id}/creative-analysis")
def update_creative(blueprint_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    blueprint = db.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="not found")
    creative = blueprint.creative or CreativeAnalysis(blueprint_id=blueprint.id)
    for field in [
        "creative_type",
        "style_type",
        "aspect_ratio",
        "duration_sec",
        "hook_type",
        "hook_window",
        "story_structure",
        "pov",
        "emotions",
        "cta_type",
        "cta_tone",
        "extracted_text",
        "tags_json",
    ]:
        if field in payload:
            setattr(creative, field, payload[field])
    db.add(creative)
    db.commit()
    return {"status": "ok"}


@router.put("/{blueprint_id}/funnel-analysis")
def update_funnel(blueprint_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    blueprint = db.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="not found")
    funnel = blueprint.funnel or FunnelAnalysis(blueprint_id=blueprint.id)
    click_url = payload.get("click_url")
    if click_url:
        funnel.click_url = click_url
        funnel.destination_type = detect_destination_type(click_url)
    for field in ["lead_fields_count", "lead_fields_json", "friction_level", "trust_elements_json"]:
        if field in payload:
            setattr(funnel, field, payload[field])
    db.add(funnel)
    db.commit()
    update_success_signals(db, blueprint)
    db.commit()
    return {"status": "ok", "destination_type": funnel.destination_type}


@router.put("/{blueprint_id}/offer-psychology")
def update_offer(blueprint_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    blueprint = db.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="not found")
    offer = blueprint.offer or OfferPsychology(blueprint_id=blueprint.id)
    for field in [
        "price_mentioned",
        "monthly_price_value",
        "discount_or_bonus",
        "urgency",
        "comparison_frame",
        "primary_frame",
        "notes",
    ]:
        if field in payload:
            setattr(offer, field, payload[field])
    db.add(offer)
    db.commit()
    return {"status": "ok"}


@router.post("/{blueprint_id}/snapshot")
def capture_snapshot_route(blueprint_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    blueprint = db.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="not found")
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    snapshot = capture_snapshot(db, blueprint, url)
    if blueprint.funnel:
        blueprint.funnel.snapshot_id = snapshot.id
        db.add(blueprint.funnel)
    db.commit()
    return {"snapshot_id": str(snapshot.id)}


@router.get("/{blueprint_id}/export.json")
def export_json(blueprint_id: str, db: Session = Depends(get_db)) -> JSONResponse:
    blueprint = db.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="not found")
    payload = {
        "id": str(blueprint.id),
        "title": blueprint.title,
        "industry": blueprint.industry,
        "creative": {
            "creative_type": blueprint.creative.creative_type,
            "style_type": blueprint.creative.style_type,
            "hook_type": blueprint.creative.hook_type,
            "story_structure": blueprint.creative.story_structure,
            "pov": blueprint.creative.pov,
            "emotions": blueprint.creative.emotions,
            "cta_type": blueprint.creative.cta_type,
            "cta_tone": blueprint.creative.cta_tone,
            "extracted_text": blueprint.creative.extracted_text,
        } if blueprint.creative else {},
        "funnel": {
            "click_url": blueprint.funnel.click_url,
            "destination_type": blueprint.funnel.destination_type,
            "lead_fields_count": blueprint.funnel.lead_fields_count,
            "friction_level": blueprint.funnel.friction_level,
        } if blueprint.funnel else {},
        "offer": {
            "price_mentioned": blueprint.offer.price_mentioned,
            "monthly_price_value": blueprint.offer.monthly_price_value,
            "discount_or_bonus": blueprint.offer.discount_or_bonus,
            "urgency": blueprint.offer.urgency,
            "comparison_frame": blueprint.offer.comparison_frame,
            "primary_frame": blueprint.offer.primary_frame,
        } if blueprint.offer else {},
        "success": {
            "ad_run_days": blueprint.success.ad_run_days,
            "variant_count_est": blueprint.success.variant_count_est,
            "scaling_score": blueprint.success.scaling_score,
            "scoring_breakdown_json": blueprint.success.scoring_breakdown_json,
        } if blueprint.success else {},
    }
    return JSONResponse(content=payload)


@router.get("/{blueprint_id}/export.csv")
def export_csv(blueprint_id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    blueprint = db.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="not found")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "industry", "scaling_score", "destination_type"])
    writer.writerow([
        str(blueprint.id),
        blueprint.title,
        blueprint.industry,
        blueprint.success.scaling_score if blueprint.success else 0,
        blueprint.funnel.destination_type if blueprint.funnel else "unknown",
    ])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv")
