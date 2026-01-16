import ipaddress
import os
import socket
from datetime import datetime
from urllib.parse import urlparse
import requests
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import (
    Ad,
    Advertiser,
    Blueprint,
    CreativeAnalysis,
    FunnelAnalysis,
    LandingSnapshot,
    OfferPsychology,
    SuccessSignals,
)

ALLOWED_SCHEMES = {"http", "https"}
MAX_HTML_BYTES = 2 * 1024 * 1024


def detect_destination_type(url: str | None) -> str:
    if not url:
        return "unknown"
    url_lower = url.lower()
    if "wa.me" in url_lower or "whatsapp" in url_lower:
        return "whatsapp"
    if "facebook.com/leadgen" in url_lower or "leadgen" in url_lower:
        return "meta_lead_form"
    if any(token in url_lower for token in ["/rechner", "/quiz", "/check", "/vergleich"]):
        return "calculator_quiz"
    return "landing_page"


def compute_scaling_score(
    ad_run_days: int | None,
    variant_count: int | None,
    destination_type: str,
    friction_level: str,
    trust_elements: bool,
) -> tuple[int, dict]:
    score = 0
    breakdown = {}
    if ad_run_days is not None:
        if ad_run_days >= 30:
            score += 45
            breakdown["runtime_days"] = 45
        elif ad_run_days >= 14:
            score += 30
            breakdown["runtime_days"] = 30
    if variant_count is not None and variant_count >= 3:
        score += 20
        breakdown["variants"] = 20
    if destination_type in {"whatsapp", "meta_lead_form"}:
        score += 10
        breakdown["fast_funnel"] = 10
    if trust_elements:
        score += 10
        breakdown["trust_elements"] = 10
    if friction_level == "high":
        score -= 10
        breakdown["friction_penalty"] = -10
    score = max(0, min(100, score))
    breakdown["total"] = score
    return score, breakdown


def _is_private_ip(hostname: str) -> bool:
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return True
    return False


def validate_snapshot_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("unsupported url scheme")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("invalid hostname")
    if _is_private_ip(hostname):
        raise ValueError("private ip not allowed")
    if hostname in {"localhost"}:
        raise ValueError("localhost not allowed")


def capture_snapshot(db: Session, blueprint: Blueprint, url: str) -> LandingSnapshot:
    validate_snapshot_url(url)
    response = requests.get(
        url,
        headers={"User-Agent": "AdRadarSnapshot/1.0"},
        timeout=10,
        stream=True,
    )
    response.raise_for_status()
    content = response.content[:MAX_HTML_BYTES]

    snapshot_dir = os.path.join("data", "snapshots", str(blueprint.id))
    os.makedirs(snapshot_dir, exist_ok=True)
    html_path = os.path.join(snapshot_dir, "snapshot.html")
    with open(html_path, "wb") as handle:
        handle.write(content)

    snapshot = LandingSnapshot(
        blueprint_id=blueprint.id,
        url=url,
        captured_at=datetime.utcnow(),
        html_path=html_path,
        title=None,
        h1=None,
        meta_description=None,
    )
    db.add(snapshot)
    db.flush()
    return snapshot


def create_blueprint(db: Session, source_ad_id: str, industry: str | None, title: str | None) -> Blueprint:
    ad = db.execute(select(Ad).where(Ad.id == source_ad_id)).scalar_one()
    advertiser = db.execute(select(Advertiser).where(Advertiser.id == ad.advertiser_id)).scalar_one_or_none()
    blueprint = Blueprint(
        source_ad_id=ad.id,
        advertiser_id=advertiser.id if advertiser else None,
        title=title or f"Blueprint: {advertiser.page_name if advertiser else 'Unknown'} - {ad.id}",
        industry=industry or "unknown",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(blueprint)
    db.flush()
    db.add(CreativeAnalysis(blueprint_id=blueprint.id))
    db.add(FunnelAnalysis(blueprint_id=blueprint.id))
    db.add(OfferPsychology(blueprint_id=blueprint.id))
    db.add(SuccessSignals(blueprint_id=blueprint.id))
    db.flush()
    return blueprint


def update_success_signals(db: Session, blueprint: Blueprint) -> SuccessSignals:
    ad = db.execute(select(Ad).where(Ad.id == blueprint.source_ad_id)).scalar_one()
    run_days = None
    if ad.start_time:
        stop_time = ad.stop_time or datetime.utcnow()
        run_days = max(0, (stop_time - ad.start_time).days)
    variants = db.execute(
        select(Ad)
        .where(Ad.advertiser_id == ad.advertiser_id)
        .where(Ad.id != ad.id)
    ).scalars().all()
    variant_count = len(variants)
    funnel = blueprint.funnel
    destination_type = funnel.destination_type if funnel else "unknown"
    friction = funnel.friction_level if funnel else "unknown"
    trust_elements = bool(funnel and funnel.trust_elements_json)
    score, breakdown = compute_scaling_score(run_days, variant_count, destination_type, friction, trust_elements)

    success = blueprint.success or SuccessSignals(blueprint_id=blueprint.id)
    success.ad_run_days = run_days
    success.variant_count_est = variant_count
    success.repetition_signal = variant_count >= 2
    success.scaling_score = score
    success.scoring_breakdown_json = breakdown
    db.add(success)
    db.flush()
    return success
