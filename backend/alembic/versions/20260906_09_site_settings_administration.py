"""Expand the singleton site settings record for administrator management.

Revision ID: 20260906_09
Revises: 20260906_08
Create Date: 2026-09-06 15:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260906_09"
down_revision: str | Sequence[str] | None = "20260906_08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "site_settings",
        sa.Column("singleton", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("site_settings", sa.Column("logo_url", sa.String(length=500)))
    op.add_column("site_settings", sa.Column("favicon_url", sa.String(length=500)))
    op.add_column("site_settings", sa.Column("contact_email", sa.String(length=320)))
    op.add_column("site_settings", sa.Column("contact_phone", sa.String(length=64)))
    op.add_column("site_settings", sa.Column("contact_address_en", sa.Text()))
    op.add_column("site_settings", sa.Column("contact_address_fa", sa.Text()))
    op.add_column(
        "site_settings",
        sa.Column("social_links", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.add_column(
        "site_settings",
        sa.Column(
            "default_theme",
            sa.String(length=10),
            nullable=False,
            server_default=sa.text("'system'"),
        ),
    )
    op.add_column("site_settings", sa.Column("default_seo_title_en", sa.String(length=240)))
    op.add_column("site_settings", sa.Column("default_seo_title_fa", sa.String(length=240)))
    op.add_column("site_settings", sa.Column("default_seo_description_en", sa.String(length=320)))
    op.add_column("site_settings", sa.Column("default_seo_description_fa", sa.String(length=320)))
    op.create_check_constraint("ck_site_settings_singleton", "site_settings", "singleton IS TRUE")
    op.create_check_constraint(
        "ck_site_settings_default_theme",
        "site_settings",
        "default_theme IN ('system', 'light', 'dark')",
    )
    op.create_unique_constraint("uq_site_settings_singleton", "site_settings", ["singleton"])


def downgrade() -> None:
    op.drop_constraint("uq_site_settings_singleton", "site_settings", type_="unique")
    op.drop_constraint("ck_site_settings_default_theme", "site_settings", type_="check")
    op.drop_constraint("ck_site_settings_singleton", "site_settings", type_="check")
    op.drop_column("site_settings", "default_seo_description_fa")
    op.drop_column("site_settings", "default_seo_description_en")
    op.drop_column("site_settings", "default_seo_title_fa")
    op.drop_column("site_settings", "default_seo_title_en")
    op.drop_column("site_settings", "default_theme")
    op.drop_column("site_settings", "social_links")
    op.drop_column("site_settings", "contact_address_fa")
    op.drop_column("site_settings", "contact_address_en")
    op.drop_column("site_settings", "contact_phone")
    op.drop_column("site_settings", "contact_email")
    op.drop_column("site_settings", "favicon_url")
    op.drop_column("site_settings", "logo_url")
    op.drop_column("site_settings", "singleton")
