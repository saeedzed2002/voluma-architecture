"""Allow typed image-and-text editorial blocks for project details.

Revision ID: 20260908_03
Revises: 20260908_02
Create Date: 2026-09-08 23:25:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260908_03"
down_revision: str | Sequence[str] | None = "20260908_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_project_blocks_type", "project_blocks", type_="check")
    op.create_check_constraint(
        "ck_project_blocks_type",
        "project_blocks",
        "block_type IN ('text', 'quote', 'single_image', 'full_width_image', "
        "'paired_image', 'gallery', 'image_text')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_project_blocks_type", "project_blocks", type_="check")
    op.create_check_constraint(
        "ck_project_blocks_type",
        "project_blocks",
        "block_type IN ('text', 'quote', 'single_image', 'full_width_image', "
        "'paired_image', 'gallery')",
    )
