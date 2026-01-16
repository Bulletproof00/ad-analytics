"""campaign blueprints

Revision ID: 0003_campaign_blueprints
Revises: 0002_os_pro
Create Date: 2024-01-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_campaign_blueprints"

down_revision = "0002_os_pro"

branch_labels = None

depends_on = None


def upgrade() -> None:
    op.create_table(
        "blueprints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_ad_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ads.id")),
        sa.Column("advertiser_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("advertisers.id")),
        sa.Column("title", sa.Text()),
        sa.Column("industry", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "creative_analysis",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("blueprint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blueprints.id")),
        sa.Column("creative_type", sa.Text()),
        sa.Column("style_type", sa.Text()),
        sa.Column("aspect_ratio", sa.Text()),
        sa.Column("duration_sec", sa.Integer()),
        sa.Column("hook_type", sa.Text()),
        sa.Column("hook_window", sa.Text()),
        sa.Column("story_structure", sa.Text()),
        sa.Column("pov", sa.Text()),
        sa.Column("emotions", postgresql.JSONB()),
        sa.Column("cta_type", sa.Text()),
        sa.Column("cta_tone", sa.Text()),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("tags_json", postgresql.JSONB()),
    )
    op.create_table(
        "landing_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("blueprint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blueprints.id")),
        sa.Column("url", sa.Text()),
        sa.Column("captured_at", sa.DateTime(timezone=True)),
        sa.Column("html_path", sa.Text()),
        sa.Column("screenshot_path", sa.Text()),
        sa.Column("title", sa.Text()),
        sa.Column("h1", sa.Text()),
        sa.Column("meta_description", sa.Text()),
    )
    op.create_table(
        "funnel_analysis",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("blueprint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blueprints.id")),
        sa.Column("click_url", sa.Text()),
        sa.Column("destination_type", sa.Text()),
        sa.Column("lead_fields_count", sa.Integer()),
        sa.Column("lead_fields_json", postgresql.JSONB()),
        sa.Column("friction_level", sa.Text()),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("landing_snapshots.id")),
        sa.Column("trust_elements_json", postgresql.JSONB()),
    )
    op.create_table(
        "offer_psychology",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("blueprint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blueprints.id")),
        sa.Column("price_mentioned", sa.Boolean()),
        sa.Column("monthly_price_value", sa.Float()),
        sa.Column("discount_or_bonus", sa.Boolean()),
        sa.Column("urgency", sa.Boolean()),
        sa.Column("comparison_frame", sa.Boolean()),
        sa.Column("primary_frame", sa.Text()),
        sa.Column("notes", sa.Text()),
    )
    op.create_table(
        "success_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("blueprint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blueprints.id")),
        sa.Column("ad_run_days", sa.Integer()),
        sa.Column("variant_count_est", sa.Integer()),
        sa.Column("repetition_signal", sa.Boolean()),
        sa.Column("scaling_score", sa.Integer()),
        sa.Column("scoring_breakdown_json", postgresql.JSONB()),
    )


def downgrade() -> None:
    op.drop_table("success_signals")
    op.drop_table("offer_psychology")
    op.drop_table("funnel_analysis")
    op.drop_table("landing_snapshots")
    op.drop_table("creative_analysis")
    op.drop_table("blueprints")
