"""Create durable media assets and ordered project-media relationships.

Revision ID: 20260906_10
Revises: 20260906_09
Create Date: 2026-09-06 20:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260906_10"
down_revision: str | Sequence[str] | None = "20260906_09"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


media_processing_state = postgresql.ENUM(
    "processing",
    "ready",
    "failed",
    "deleted",
    name="mediaprocessingstate",
    create_type=False,
)


def upgrade() -> None:
    media_processing_state.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "media_assets",
        sa.Column("original_extension", sa.String(length=8), nullable=False),
        sa.Column("source_content_type", sa.String(length=40), nullable=False),
        sa.Column("source_size_bytes", sa.Integer(), nullable=False),
        sa.Column("source_width", sa.Integer(), nullable=False),
        sa.Column("source_height", sa.Integer(), nullable=False),
        sa.Column("processing_state", media_processing_state, nullable=False),
        sa.Column("processing_attempts", sa.Integer(), nullable=False),
        sa.Column("processing_error", sa.String(length=500), nullable=True),
        sa.Column("derivative_version", sa.String(length=40), nullable=True),
        sa.Column("derivative_width", sa.Integer(), nullable=True),
        sa.Column("derivative_height", sa.Integer(), nullable=True),
        sa.Column("alt_en", sa.String(length=500), nullable=True),
        sa.Column("alt_fa", sa.String(length=500), nullable=True),
        sa.Column("caption_en", sa.Text(), nullable=True),
        sa.Column("caption_fa", sa.Text(), nullable=True),
        sa.Column("credit", sa.String(length=500), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("source_size_bytes > 0", name="ck_media_assets_source_size_positive"),
        sa.CheckConstraint("source_width > 0", name="ck_media_assets_source_width_positive"),
        sa.CheckConstraint("source_height > 0", name="ck_media_assets_source_height_positive"),
        sa.CheckConstraint(
            "processing_attempts >= 0", name="ck_media_assets_processing_attempts_nonnegative"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_media_assets_status_created_at",
        "media_assets",
        ["processing_state", "created_at"],
        unique=False,
    )
    op.create_table(
        "project_media",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("media_asset_id", sa.Uuid(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_cover", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["media_asset_id"], ["media_assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "media_asset_id", name="uq_project_media_asset"),
        sa.UniqueConstraint("project_id", "display_order", name="uq_project_media_display_order"),
    )
    op.create_index(
        "ix_project_media_project_cover",
        "project_media",
        ["project_id", "is_cover"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_project_media_project_cover", table_name="project_media")
    op.drop_table("project_media")
    op.drop_index("ix_media_assets_status_created_at", table_name="media_assets")
    op.drop_table("media_assets")
    media_processing_state.drop(op.get_bind(), checkfirst=True)
