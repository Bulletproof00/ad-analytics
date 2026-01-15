import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import JSON


class Base(DeclarativeBase):
    pass


def _uuid_type():
    return UUID(as_uuid=True).with_variant(String, "sqlite")


def _json_type():
    return JSONB().with_variant(JSON, "sqlite")


class Advertiser(Base):
    __tablename__ = "advertisers"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(String, default="meta")
    page_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    page_name: Mapped[str | None] = mapped_column(String, nullable=True)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    ads = relationship("Ad", back_populates="advertiser")


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(String, default="meta")
    ad_archive_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    advertiser_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("advertisers.id"))
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stop_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool | None] = mapped_column(Boolean)
    snapshot_url: Mapped[str | None] = mapped_column(Text)
    copy_bodies: Mapped[dict | None] = mapped_column(_json_type())
    link_titles: Mapped[dict | None] = mapped_column(_json_type())
    link_descriptions: Mapped[dict | None] = mapped_column(_json_type())
    link_captions: Mapped[dict | None] = mapped_column(_json_type())
    publisher_platforms: Mapped[dict | None] = mapped_column(_json_type())
    raw: Mapped[dict | None] = mapped_column(_json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    advertiser = relationship("Advertiser", back_populates="ads")
    snapshots = relationship("AdSnapshot", back_populates="ad")
    tags = relationship("Tag", back_populates="ad", uselist=False)
    score = relationship("Score", back_populates="ad", uselist=False)
    features = relationship("Feature", back_populates="ad", uselist=False)


class AdSnapshot(Base):
    __tablename__ = "ad_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    ad_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ads.id"))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    raw: Mapped[dict | None] = mapped_column(_json_type())

    ad = relationship("Ad", back_populates="snapshots")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    ad_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ads.id"), unique=True)
    niche: Mapped[str | None] = mapped_column(String, default="unknown")
    funnel_type: Mapped[str | None] = mapped_column(String, default="unknown")
    offer_type: Mapped[str | None] = mapped_column(String, default="unknown")
    emotion_trigger: Mapped[str | None] = mapped_column(String, default="unknown")
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    ad = relationship("Ad", back_populates="tags")


class Score(Base):
    __tablename__ = "scores"

    ad_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ads.id"), primary_key=True)
    score_total: Mapped[int] = mapped_column(Integer, default=0)
    score_runtime: Mapped[int] = mapped_column(Integer, default=0)
    score_variants: Mapped[int] = mapped_column(Integer, default=0)
    score_reuse: Mapped[int] = mapped_column(Integer, default=0)
    score_funnel_fit: Mapped[int] = mapped_column(Integer, default=0)
    saturation_index: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[dict | None] = mapped_column(_json_type())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    ad = relationship("Ad", back_populates="score")


class HookLibrary(Base):
    __tablename__ = "hook_library"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    hook_text: Mapped[str] = mapped_column(Text)
    hook_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    reuse_count: Mapped[int] = mapped_column(Integer, default=0)
    example_ad_ids: Mapped[dict | None] = mapped_column(_json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    state: Mapped[str] = mapped_column(String, default="running")
    payload: Mapped[dict | None] = mapped_column(_json_type())
    summary: Mapped[dict | None] = mapped_column(_json_type())
    errors: Mapped[dict | None] = mapped_column(_json_type())
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    keywords = relationship("ScanKeyword", back_populates="scan_run")


class ScanKeyword(Base):
    __tablename__ = "scan_keywords"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    scan_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scan_runs.id"))
    keyword: Mapped[str] = mapped_column(String)
    fetched_count: Mapped[int] = mapped_column(Integer, default=0)
    upserted_count: Mapped[int] = mapped_column(Integer, default=0)
    unique_pages: Mapped[int] = mapped_column(Integer, default=0)
    runtime_ms: Mapped[int] = mapped_column(Integer, default=0)

    scan_run = relationship("ScanRun", back_populates="keywords")


class Feature(Base):
    __tablename__ = "features"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    ad_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ads.id"), unique=True)
    hook_text: Mapped[str | None] = mapped_column(Text)
    hook_hash: Mapped[str | None] = mapped_column(String, index=True)
    offer_type: Mapped[str | None] = mapped_column(String)
    emotion_trigger: Mapped[str | None] = mapped_column(String)
    funnel_type: Mapped[str | None] = mapped_column(String)
    creative_type: Mapped[str | None] = mapped_column(String, default="unknown")
    copy_metrics: Mapped[dict | None] = mapped_column(_json_type())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    ad = relationship("Ad", back_populates="features")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    agent_name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="completed")
    input: Mapped[dict | None] = mapped_column(_json_type())
    output: Mapped[dict | None] = mapped_column(_json_type())
    evidence: Mapped[dict | None] = mapped_column(_json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class OwnCampaign(Base):
    __tablename__ = "own_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    source: Mapped[str | None] = mapped_column(String, default="csv")
    metrics: Mapped[dict | None] = mapped_column(_json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    scope: Mapped[str] = mapped_column(String, default="global")
    key: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[dict | None] = mapped_column(_json_type())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict | None] = mapped_column(_json_type())
    status: Mapped[str] = mapped_column(String, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    event_name: Mapped[str] = mapped_column(String)
    payload: Mapped[dict | None] = mapped_column(_json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class TestQueueItem(Base):
    __tablename__ = "test_queue"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="draft")
    predicted_success: Mapped[int] = mapped_column(Integer, default=0)
    risk_notes: Mapped[str | None] = mapped_column(Text)
    recommended_budget: Mapped[int | None] = mapped_column(Integer)
    kill_rules: Mapped[dict | None] = mapped_column(_json_type())
    payload: Mapped[dict | None] = mapped_column(_json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Blueprint(Base):
    __tablename__ = "blueprints"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    source_ad_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ads.id"))
    advertiser_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("advertisers.id"), nullable=True)
    title: Mapped[str] = mapped_column(String)
    industry: Mapped[str | None] = mapped_column(String, default="unknown")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    ad = relationship("Ad")
    creative = relationship("CreativeAnalysis", back_populates="blueprint", uselist=False)
    funnel = relationship("FunnelAnalysis", back_populates="blueprint", uselist=False)
    offer = relationship("OfferPsychology", back_populates="blueprint", uselist=False)
    success = relationship("SuccessSignals", back_populates="blueprint", uselist=False)
    snapshots = relationship("LandingSnapshot", back_populates="blueprint")


class CreativeAnalysis(Base):
    __tablename__ = "creative_analysis"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    blueprint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blueprints.id"))
    creative_type: Mapped[str] = mapped_column(String, default="unknown")
    style_type: Mapped[str] = mapped_column(String, default="unknown")
    aspect_ratio: Mapped[str | None] = mapped_column(String)
    duration_sec: Mapped[int | None] = mapped_column(Integer)
    hook_type: Mapped[str] = mapped_column(String, default="unknown")
    hook_window: Mapped[str] = mapped_column(String, default="unknown")
    story_structure: Mapped[str] = mapped_column(String, default="unknown")
    pov: Mapped[str] = mapped_column(String, default="unknown")
    emotions: Mapped[dict | None] = mapped_column(_json_type())
    cta_type: Mapped[str] = mapped_column(String, default="unknown")
    cta_tone: Mapped[str] = mapped_column(String, default="unknown")
    extracted_text: Mapped[str | None] = mapped_column(Text)
    tags_json: Mapped[dict | None] = mapped_column(_json_type())

    blueprint = relationship("Blueprint", back_populates="creative")


class FunnelAnalysis(Base):
    __tablename__ = "funnel_analysis"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    blueprint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blueprints.id"))
    click_url: Mapped[str | None] = mapped_column(Text)
    destination_type: Mapped[str] = mapped_column(String, default="unknown")
    lead_fields_count: Mapped[int | None] = mapped_column(Integer)
    lead_fields_json: Mapped[dict | None] = mapped_column(_json_type())
    friction_level: Mapped[str] = mapped_column(String, default="unknown")
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("landing_snapshots.id"), nullable=True)
    trust_elements_json: Mapped[dict | None] = mapped_column(_json_type())

    blueprint = relationship("Blueprint", back_populates="funnel")
    snapshot = relationship("LandingSnapshot", foreign_keys=[snapshot_id])


class LandingSnapshot(Base):
    __tablename__ = "landing_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    blueprint_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("blueprints.id"), nullable=True)
    url: Mapped[str] = mapped_column(Text)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    html_path: Mapped[str | None] = mapped_column(Text)
    screenshot_path: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String)
    h1: Mapped[str | None] = mapped_column(String)
    meta_description: Mapped[str | None] = mapped_column(Text)

    blueprint = relationship("Blueprint", back_populates="snapshots")


class OfferPsychology(Base):
    __tablename__ = "offer_psychology"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    blueprint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blueprints.id"))
    price_mentioned: Mapped[bool] = mapped_column(Boolean, default=False)
    monthly_price_value: Mapped[float | None] = mapped_column(Float)
    discount_or_bonus: Mapped[bool] = mapped_column(Boolean, default=False)
    urgency: Mapped[bool] = mapped_column(Boolean, default=False)
    comparison_frame: Mapped[bool] = mapped_column(Boolean, default=False)
    primary_frame: Mapped[str] = mapped_column(String, default="unknown")
    notes: Mapped[str | None] = mapped_column(Text)

    blueprint = relationship("Blueprint", back_populates="offer")


class SuccessSignals(Base):
    __tablename__ = "success_signals"

    id: Mapped[uuid.UUID] = mapped_column(_uuid_type(), primary_key=True, default=uuid.uuid4)
    blueprint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blueprints.id"))
    ad_run_days: Mapped[int | None] = mapped_column(Integer)
    variant_count_est: Mapped[int | None] = mapped_column(Integer)
    repetition_signal: Mapped[bool] = mapped_column(Boolean, default=False)
    scaling_score: Mapped[int] = mapped_column(Integer, default=0)
    scoring_breakdown_json: Mapped[dict | None] = mapped_column(_json_type())

    blueprint = relationship("Blueprint", back_populates="success")
