"""Protect ordered studio members and recognitions.

Revision ID: 20260906_06
Revises: 20260906_05
Create Date: 2026-09-06 05:00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260906_06"
down_revision: str | Sequence[str] | None = "20260906_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _normalize_order(table: str) -> None:
    op.execute(
        f"""
        WITH ranked AS (
            SELECT id, row_number() OVER (ORDER BY display_order, created_at, id) - 1 AS position
            FROM {table}
        )
        UPDATE {table} AS item
        SET display_order = ranked.position
        FROM ranked
        WHERE item.id = ranked.id
        """
    )


def upgrade() -> None:
    _normalize_order("studio_members")
    _normalize_order("recognitions")
    op.create_unique_constraint(
        "uq_studio_members_display_order", "studio_members", ["display_order"]
    )
    op.create_unique_constraint("uq_recognitions_display_order", "recognitions", ["display_order"])
    op.create_index(
        "ix_studio_members_public_list",
        "studio_members",
        ["publication_state", "display_order"],
    )
    op.create_index(
        "ix_recognitions_public_list",
        "recognitions",
        ["publication_state", "display_order"],
    )


def downgrade() -> None:
    op.drop_index("ix_recognitions_public_list", table_name="recognitions")
    op.drop_index("ix_studio_members_public_list", table_name="studio_members")
    op.drop_constraint("uq_recognitions_display_order", "recognitions", type_="unique")
    op.drop_constraint("uq_studio_members_display_order", "studio_members", type_="unique")
