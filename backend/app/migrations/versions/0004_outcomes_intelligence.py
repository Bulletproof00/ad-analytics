"""outcomes

Revision ID: 0004_outcomes_intelligence
Revises: 0003_campaign_blueprints
Create Date: 2024-01-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_outcomes_intelligence"

down_revision = "0003_campaign_blueprints"

branch_labels = None

depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaign_outcomes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("blueprint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blueprints.id")),
        sa.Column("ad_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ads.id")),
        sa.Column("leads_count", sa.Integer()),
        sa.Column("qualified_leads_count", sa.Integer()),
        sa.Column("sales_count", sa.Integer()),
        sa.Column("cpl", sa.Float()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("campaign_outcomes")
