"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"

down_revision = None

branch_labels = None

depends_on = None


def upgrade() -> None:
    op.create_table(
        "advertisers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("platform", sa.Text(), server_default="meta"),
        sa.Column("page_id", sa.Text(), unique=True),
        sa.Column("page_name", sa.Text()),
        sa.Column("first_seen_at", sa.DateTime(timezone=True)),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "ads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("platform", sa.Text(), server_default="meta"),
        sa.Column("ad_archive_id", sa.Text(), unique=True),
        sa.Column("advertiser_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("advertisers.id")),
        sa.Column("start_time", sa.DateTime(timezone=True)),
        sa.Column("stop_time", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean()),
        sa.Column("snapshot_url", sa.Text()),
        sa.Column("copy_bodies", postgresql.JSONB()),
        sa.Column("link_titles", postgresql.JSONB()),
        sa.Column("link_descriptions", postgresql.JSONB()),
        sa.Column("link_captions", postgresql.JSONB()),
        sa.Column("publisher_platforms", postgresql.JSONB()),
        sa.Column("raw", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "ad_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ad_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ads.id")),
        sa.Column("collected_at", sa.DateTime(timezone=True)),
        sa.Column("raw", postgresql.JSONB()),
    )
    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ad_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ads.id"), unique=True),
        sa.Column("niche", sa.Text()),
        sa.Column("funnel_type", sa.Text()),
        sa.Column("offer_type", sa.Text()),
        sa.Column("emotion_trigger", sa.Text()),
        sa.Column("is_winner", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("notes", sa.Text()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "scores",
        sa.Column("ad_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ads.id"), primary_key=True),
        sa.Column("score_total", sa.Integer()),
        sa.Column("score_runtime", sa.Integer()),
        sa.Column("score_variants", sa.Integer()),
        sa.Column("score_reuse", sa.Integer()),
        sa.Column("score_funnel_fit", sa.Integer()),
        sa.Column("explanation", postgresql.JSONB()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "hook_library",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("hook_text", sa.Text()),
        sa.Column("hook_hash", sa.Text(), unique=True),
        sa.Column("reuse_count", sa.Integer(), server_default="0"),
        sa.Column("example_ad_ids", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("hook_library")
    op.drop_table("scores")
    op.drop_table("tags")
    op.drop_table("ad_snapshots")
    op.drop_table("ads")
    op.drop_table("advertisers")
