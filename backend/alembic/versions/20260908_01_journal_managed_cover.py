"""Reference durable managed media from journal article covers.

Revision ID: 20260908_01
Revises: 20260906_10
Create Date: 2026-09-08 20:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260908_01"
down_revision: str | Sequence[str] | None = "20260906_10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("journal_articles", sa.Column("cover_media_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_journal_articles_cover_media_id_media_assets",
        "journal_articles",
        "media_assets",
        ["cover_media_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_journal_articles_cover_media_id", "journal_articles", ["cover_media_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_journal_articles_cover_media_id", table_name="journal_articles")
    op.drop_constraint(
        "fk_journal_articles_cover_media_id_media_assets",
        "journal_articles",
        type_="foreignkey",
    )
    op.drop_column("journal_articles", "cover_media_id")
