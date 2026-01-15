import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
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
