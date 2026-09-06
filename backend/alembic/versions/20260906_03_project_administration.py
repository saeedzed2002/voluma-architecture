"""Add project editorial administration fields and ordered blocks.

Revision ID: 20260906_03
Revises: 20260906_02
Create Date: 2026-09-06 02:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260906_03"
down_revision: str | Sequence[str] | None = "20260906_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Existing projects predate transactional ordering. Normalize their positions before
    # protecting the invariant with a database constraint.
    op.execute(
        """
        WITH ranked AS (
            SELECT id, row_number() OVER (ORDER BY display_order, created_at, id) - 1 AS position
            FROM projects
        )
        UPDATE projects AS project
        SET display_order = ranked.position
        FROM ranked
        WHERE project.id = ranked.id
        """
    )
    op.create_unique_constraint("uq_projects_display_order", "projects", ["display_order"])
    op.add_column("projects", sa.Column("client_en", sa.String(length=240), nullable=True))
    op.add_column("projects", sa.Column("client_fa", sa.String(length=240), nullable=True))
    op.add_column("projects", sa.Column("architect_en", sa.String(length=240), nullable=True))
    op.add_column("projects", sa.Column("architect_fa", sa.String(length=240), nullable=True))
    op.add_column("projects", sa.Column("collaborators_en", sa.Text(), nullable=True))
    op.add_column("projects", sa.Column("collaborators_fa", sa.Text(), nullable=True))
    op.add_column("projects", sa.Column("completion_date", sa.Date(), nullable=True))
    op.add_column("projects", sa.Column("seo_title_en", sa.String(length=240), nullable=True))
    op.add_column("projects", sa.Column("seo_title_fa", sa.String(length=240), nullable=True))
    op.add_column("projects", sa.Column("seo_description_en", sa.String(length=320), nullable=True))
    op.add_column("projects", sa.Column("seo_description_fa", sa.String(length=320), nullable=True))
    op.create_table(
        "project_blocks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("block_type", sa.String(length=32), nullable=False),
        sa.Column("content_en", sa.JSON(), nullable=False),
        sa.Column("content_fa", sa.JSON(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "block_type IN ('text', 'quote', 'single_image', 'full_width_image', "
            "'paired_image', 'gallery')",
            name="ck_project_blocks_type",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id", "display_order", name="uq_project_blocks_project_display_order"
        ),
    )
    op.create_index(
        "ix_project_blocks_project_order", "project_blocks", ["project_id", "display_order"]
    )


def downgrade() -> None:
    op.drop_index("ix_project_blocks_project_order", table_name="project_blocks")
    op.drop_table("project_blocks")
    op.drop_column("projects", "seo_description_fa")
    op.drop_column("projects", "seo_description_en")
    op.drop_column("projects", "seo_title_fa")
    op.drop_column("projects", "seo_title_en")
    op.drop_column("projects", "completion_date")
    op.drop_column("projects", "collaborators_fa")
    op.drop_column("projects", "collaborators_en")
    op.drop_column("projects", "architect_fa")
    op.drop_column("projects", "architect_en")
    op.drop_column("projects", "client_fa")
    op.drop_column("projects", "client_en")
    op.drop_constraint("uq_projects_display_order", "projects", type_="unique")
