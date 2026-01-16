"""os pro tables

Revision ID: 0002_os_pro
Revises: 0001_initial
Create Date: 2024-01-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_os_pro"

down_revision = "0001_initial"

branch_labels = None

depends_on = None


def upgrade() -> None:
    op.add_column("scores", sa.Column("saturation_index", sa.Integer(), server_default="0"))

    op.create_table(
        "scan_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("state", sa.Text(), server_default="running"),
        sa.Column("payload", postgresql.JSONB()),
        sa.Column("summary", postgresql.JSONB()),
        sa.Column("errors", postgresql.JSONB()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "scan_keywords",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scan_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scan_runs.id")),
        sa.Column("keyword", sa.Text()),
        sa.Column("fetched_count", sa.Integer(), server_default="0"),
        sa.Column("upserted_count", sa.Integer(), server_default="0"),
        sa.Column("unique_pages", sa.Integer(), server_default="0"),
        sa.Column("runtime_ms", sa.Integer(), server_default="0"),
    )
    op.create_table(
        "features",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ad_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ads.id"), unique=True),
        sa.Column("hook_text", sa.Text()),
        sa.Column("hook_hash", sa.Text()),
        sa.Column("offer_type", sa.Text()),
        sa.Column("emotion_trigger", sa.Text()),
        sa.Column("funnel_type", sa.Text()),
        sa.Column("creative_type", sa.Text()),
        sa.Column("copy_metrics", postgresql.JSONB()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "agent_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_name", sa.Text()),
        sa.Column("status", sa.Text(), server_default="completed"),
        sa.Column("input", postgresql.JSONB()),
        sa.Column("output", postgresql.JSONB()),
        sa.Column("evidence", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "own_campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text()),
        sa.Column("source", sa.Text()),
        sa.Column("metrics", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scope", sa.Text()),
        sa.Column("key", sa.Text()),
        sa.Column("value", postgresql.JSONB()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.Text()),
        sa.Column("severity", sa.Text()),
        sa.Column("title", sa.Text()),
        sa.Column("message", sa.Text()),
        sa.Column("evidence", postgresql.JSONB()),
        sa.Column("status", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_name", sa.Text()),
        sa.Column("payload", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "test_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.Text()),
        sa.Column("status", sa.Text()),
        sa.Column("predicted_success", sa.Integer(), server_default="0"),
        sa.Column("risk_notes", sa.Text()),
        sa.Column("recommended_budget", sa.Integer()),
        sa.Column("kill_rules", postgresql.JSONB()),
        sa.Column("payload", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("test_queue")
    op.drop_table("events")
    op.drop_table("alerts")
    op.drop_table("settings")
    op.drop_table("own_campaigns")
    op.drop_table("agent_runs")
    op.drop_table("features")
    op.drop_table("scan_keywords")
    op.drop_table("scan_runs")
    op.drop_column("scores", "saturation_index")
