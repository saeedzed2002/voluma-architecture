"""Add ordered journal blocks and editorial metadata.

Revision ID: 20260906_07
Revises: 20260906_06
Create Date: 2026-09-06 13:00:00
"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260906_07"
down_revision: str | Sequence[str] | None = "20260906_06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        WITH ranked AS (
            SELECT id, row_number() OVER (ORDER BY display_order, created_at, id) - 1 AS position
            FROM journal_categories
        )
        UPDATE journal_categories AS category
        SET display_order = ranked.position
        FROM ranked
        WHERE category.id = ranked.id
        """
    )
    op.create_unique_constraint(
        "uq_journal_categories_display_order", "journal_categories", ["display_order"]
    )
    op.add_column("journal_articles", sa.Column("seo_title_en", sa.String(length=240)))
    op.add_column("journal_articles", sa.Column("seo_title_fa", sa.String(length=240)))
    op.add_column("journal_articles", sa.Column("seo_description_en", sa.String(length=320)))
    op.add_column("journal_articles", sa.Column("seo_description_fa", sa.String(length=320)))
    op.create_table(
        "article_blocks",
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
        sa.Column("article_id", sa.Uuid(), nullable=False),
        sa.Column("block_type", sa.String(length=32), nullable=False),
        sa.Column("content_en", sa.JSON(), nullable=False),
        sa.Column("content_fa", sa.JSON(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.CheckConstraint("block_type IN ('text', 'quote')", name="ck_article_blocks_type"),
        sa.ForeignKeyConstraint(["article_id"], ["journal_articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "article_id", "display_order", name="uq_article_blocks_article_display_order"
        ),
    )
    op.create_index(
        "ix_article_blocks_article_order", "article_blocks", ["article_id", "display_order"]
    )

    connection = op.get_bind()
    legacy_articles = connection.execute(
        sa.text("SELECT id, body_en, body_fa FROM journal_articles")
    ).mappings()
    blocks = sa.table(
        "article_blocks",
        sa.column("id", sa.Uuid()),
        sa.column("article_id", sa.Uuid()),
        sa.column("block_type", sa.String()),
        sa.column("content_en", sa.JSON()),
        sa.column("content_fa", sa.JSON()),
        sa.column("display_order", sa.Integer()),
    )
    for article in legacy_articles:
        connection.execute(
            blocks.insert().values(
                id=uuid4(),
                article_id=article["id"],
                block_type="text",
                content_en={"body": article["body_en"]},
                content_fa={"body": article["body_fa"]},
                display_order=0,
            )
        )


def downgrade() -> None:
    op.drop_index("ix_article_blocks_article_order", table_name="article_blocks")
    op.drop_table("article_blocks")
    op.drop_column("journal_articles", "seo_description_fa")
    op.drop_column("journal_articles", "seo_description_en")
    op.drop_column("journal_articles", "seo_title_fa")
    op.drop_column("journal_articles", "seo_title_en")
    op.drop_constraint("uq_journal_categories_display_order", "journal_categories", type_="unique")
