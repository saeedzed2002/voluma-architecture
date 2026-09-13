"""Allow journal image-and-text editorial blocks.

Revision ID: 20260913_02
Revises: 20260913_01
Create Date: 2026-09-13 12:20:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260913_02"
down_revision: str | Sequence[str] | None = "20260913_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_article_blocks_type", "article_blocks", type_="check")
    op.create_check_constraint(
        "ck_article_blocks_type",
        "article_blocks",
        "block_type IN ('text', 'quote', 'single_image', 'image_text')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_article_blocks_type", "article_blocks", type_="check")
    op.create_check_constraint(
        "ck_article_blocks_type",
        "article_blocks",
        "block_type IN ('text', 'quote', 'single_image')",
    )
