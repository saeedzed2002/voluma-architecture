"""Make every home-page editorial section content-managed.

Revision ID: 20260913_01
Revises: 20260908_05
Create Date: 2026-09-13 12:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260913_01"
down_revision: str | Sequence[str] | None = "20260908_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


TEXT_DEFAULTS = {
    "home_selected_projects_heading_en": "Selected projects",
    "home_selected_projects_heading_fa": "پروژه‌های منتخب",
    "home_studio_heading_en": "We design for atmosphere, use, and time.",
    "home_studio_heading_fa": "برای کیفیت فضا، شیوه‌ی استفاده و گذر زمان طراحی می‌کنیم.",
    "home_studio_body_en": "Configure the studio introduction shown on the home page.",
    "home_studio_body_fa": "معرفی استودیو که در صفحهٔ اصلی نمایش داده می‌شود را پیکربندی کنید.",
    "home_expertise_heading_en": "What we shape",
    "home_expertise_heading_fa": "آنچه شکل می‌دهیم",
    "home_process_heading_en": "A clear path from first question to built form.",
    "home_process_heading_fa": "مسیری روشن از نخستین پرسش تا فضای ساخته‌شده.",
    "home_journal_heading_en": "Latest from the journal",
    "home_journal_heading_fa": "تازه‌ترین یادداشت‌ها",
    "home_contact_heading_en": "Begin with a place, a question, or a possibility.",
    "home_contact_heading_fa": "با یک مکان، یک پرسش یا یک امکان آغاز کنیم.",
}


def upgrade() -> None:
    for column, value in TEXT_DEFAULTS.items():
        op.add_column(
            "site_settings",
            sa.Column(column, sa.Text(), nullable=False, server_default=sa.text(repr(value))),
        )
        op.alter_column("site_settings", column, server_default=None)
    for column in ("home_studio_media_id", "home_expertise_media_id"):
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
    for column in ("home_expertise_media_id", "home_studio_media_id"):
        op.drop_index(f"ix_site_settings_{column}", table_name="site_settings")
        op.drop_constraint(
            f"fk_site_settings_{column}_media_assets",
            "site_settings",
            type_="foreignkey",
        )
        op.drop_column("site_settings", column)
    for column in reversed(TEXT_DEFAULTS):
        op.drop_column("site_settings", column)
