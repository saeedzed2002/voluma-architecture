"""Attach managed portraits to studio members.

Revision ID: 20260908_04
Revises: 20260908_03
Create Date: 2026-09-08 23:45:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260908_04"
down_revision: str | Sequence[str] | None = "20260908_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("studio_members", sa.Column("portrait_media_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_studio_members_portrait_media_id_media_assets",
        "studio_members",
        "media_assets",
        ["portrait_media_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_studio_members_portrait_media_id", "studio_members", ["portrait_media_id"])


def downgrade() -> None:
    op.drop_index("ix_studio_members_portrait_media_id", table_name="studio_members")
    op.drop_constraint(
        "fk_studio_members_portrait_media_id_media_assets",
        "studio_members",
        type_="foreignkey",
    )
    op.drop_column("studio_members", "portrait_media_id")
