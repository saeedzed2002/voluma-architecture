"""Reference managed media from site settings.

Revision ID: 20260908_05
Revises: 20260908_04
Create Date: 2026-09-08 23:55:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260908_05"
down_revision: str | Sequence[str] | None = "20260908_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for column in ("logo_media_id", "favicon_media_id", "home_hero_media_id"):
        op.add_column("site_settings", sa.Column(column, sa.Uuid(), nullable=True))
        op.create_foreign_key(
            f"fk_site_settings_{column}_media_assets",
            "site_settings",
            "media_assets",
            [column],
            ["id"],
            ondelete="RESTRICT",
        )
        op.create_index(f"ix_site_settings_{column}", "site_settings", [column])


def downgrade() -> None:
    for column in ("home_hero_media_id", "favicon_media_id", "logo_media_id"):
        op.drop_index(f"ix_site_settings_{column}", table_name="site_settings")
        op.drop_constraint(
            f"fk_site_settings_{column}_media_assets",
            "site_settings",
            type_="foreignkey",
        )
        op.drop_column("site_settings", column)
