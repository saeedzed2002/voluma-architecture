"""Protect taxonomy ordering with database constraints.

Revision ID: 20260906_04
Revises: 20260906_03
Create Date: 2026-09-06 03:00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260906_04"
down_revision: str | Sequence[str] | None = "20260906_03"
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
    _normalize_order("disciplines")
    _normalize_order("typologies")
    op.create_unique_constraint("uq_disciplines_display_order", "disciplines", ["display_order"])
    op.create_unique_constraint("uq_typologies_display_order", "typologies", ["display_order"])


def downgrade() -> None:
    op.drop_constraint("uq_typologies_display_order", "typologies", type_="unique")
    op.drop_constraint("uq_disciplines_display_order", "disciplines", type_="unique")
