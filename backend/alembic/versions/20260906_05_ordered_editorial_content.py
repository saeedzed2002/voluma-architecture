"""Protect ordered expertise and process content.

Revision ID: 20260906_05
Revises: 20260906_04
Create Date: 2026-09-06 04:00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260906_05"
down_revision: str | Sequence[str] | None = "20260906_04"
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
    _normalize_order("expertise")
    _normalize_order("process_steps")
    op.create_unique_constraint("uq_expertise_display_order", "expertise", ["display_order"])
    op.create_unique_constraint(
        "uq_process_steps_display_order", "process_steps", ["display_order"]
    )
    op.create_index("ix_expertise_public_list", "expertise", ["publication_state", "display_order"])
    op.create_index(
        "ix_process_steps_public_list",
        "process_steps",
        ["publication_state", "display_order"],
    )


def downgrade() -> None:
    op.drop_index("ix_process_steps_public_list", table_name="process_steps")
    op.drop_index("ix_expertise_public_list", table_name="expertise")
    op.drop_constraint("uq_process_steps_display_order", "process_steps", type_="unique")
    op.drop_constraint("uq_expertise_display_order", "expertise", type_="unique")
