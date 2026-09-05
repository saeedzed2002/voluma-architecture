"""Create the public content foundation.

Revision ID: 20260906_01
Revises: None
Create Date: 2026-09-06 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260906_01"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


publication_state = sa.Enum("DRAFT", "PUBLISHED", name="publication_state")


def _timestamps() -> list[sa.Column[object]]:
    return [
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
        sa.PrimaryKeyConstraint("id"),
    ]


def upgrade() -> None:
    op.create_table(
        "site_settings",
        *_timestamps(),
        sa.Column("studio_name", sa.String(length=120), nullable=False),
        sa.Column("home_title_en", sa.Text(), nullable=False),
        sa.Column("home_title_fa", sa.Text(), nullable=False),
        sa.Column("home_body_en", sa.Text(), nullable=False),
        sa.Column("home_body_fa", sa.Text(), nullable=False),
        sa.Column("home_hero_image_url", sa.String(length=500)),
        sa.Column("home_hero_alt_en", sa.String(length=500)),
        sa.Column("home_hero_alt_fa", sa.String(length=500)),
        sa.Column("studio_intro_en", sa.Text(), nullable=False),
        sa.Column("studio_intro_fa", sa.Text(), nullable=False),
        sa.Column("studio_principles_en", sa.JSON(), nullable=False),
        sa.Column("studio_principles_fa", sa.JSON(), nullable=False),
        sa.Column("privacy_en", sa.Text(), nullable=False),
        sa.Column("privacy_fa", sa.Text(), nullable=False),
    )
    op.create_table(
        "disciplines",
        *_timestamps(),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title_en", sa.String(length=160), nullable=False),
        sa.Column("title_fa", sa.String(length=160), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "typologies",
        *_timestamps(),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title_en", sa.String(length=160), nullable=False),
        sa.Column("title_fa", sa.String(length=160), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "projects",
        *_timestamps(),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("publication_state", publication_state, nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("featured", sa.Boolean(), nullable=False),
        sa.Column("title_en", sa.String(length=240), nullable=False),
        sa.Column("title_fa", sa.String(length=240), nullable=False),
        sa.Column("subtitle_en", sa.String(length=320)),
        sa.Column("subtitle_fa", sa.String(length=320)),
        sa.Column("summary_en", sa.Text(), nullable=False),
        sa.Column("summary_fa", sa.Text(), nullable=False),
        sa.Column("location_en", sa.String(length=160), nullable=False),
        sa.Column("location_fa", sa.String(length=160), nullable=False),
        sa.Column("completion_year", sa.Integer()),
        sa.Column("status_en", sa.String(length=100)),
        sa.Column("status_fa", sa.String(length=100)),
        sa.Column("area_en", sa.String(length=100)),
        sa.Column("area_fa", sa.String(length=100)),
        sa.Column("scope_en", sa.String(length=240)),
        sa.Column("scope_fa", sa.String(length=240)),
        sa.Column("intro_title_en", sa.String(length=240)),
        sa.Column("intro_title_fa", sa.String(length=240)),
        sa.Column("intro_en", sa.Text()),
        sa.Column("intro_fa", sa.Text()),
        sa.Column("narrative_title_en", sa.String(length=240)),
        sa.Column("narrative_title_fa", sa.String(length=240)),
        sa.Column("narrative_en", sa.Text()),
        sa.Column("narrative_fa", sa.Text()),
        sa.Column("quote_en", sa.Text()),
        sa.Column("quote_fa", sa.Text()),
        sa.Column("material_title_en", sa.String(length=240)),
        sa.Column("material_title_fa", sa.String(length=240)),
        sa.Column("material_en", sa.Text()),
        sa.Column("material_fa", sa.Text()),
        sa.Column("cover_image_url", sa.String(length=500)),
        sa.Column("cover_alt_en", sa.String(length=500)),
        sa.Column("cover_alt_fa", sa.String(length=500)),
        sa.Column("gallery_images", sa.JSON(), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "ix_projects_public_archive",
        "projects",
        ["publication_state", "display_order", "published_at"],
    )
    op.create_index("ix_projects_public_location", "projects", ["publication_state", "location_en"])
    op.create_index(
        "ix_projects_public_search_en",
        "projects",
        ["publication_state", sa.text("lower(title_en)"), sa.text("lower(location_en)")],
    )
    op.create_index(
        "ix_projects_public_search_fa",
        "projects",
        ["publication_state", sa.text("lower(title_fa)"), sa.text("lower(location_fa)")],
    )
    op.create_table(
        "project_disciplines",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("discipline_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["discipline_id"], ["disciplines.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "discipline_id"),
    )
    op.create_table(
        "project_typologies",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("typology_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["typology_id"], ["typologies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("project_id", "typology_id"),
    )
    op.create_table(
        "expertise",
        *_timestamps(),
        sa.Column("publication_state", publication_state, nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("title_en", sa.String(length=180), nullable=False),
        sa.Column("title_fa", sa.String(length=180), nullable=False),
        sa.Column("summary_en", sa.Text(), nullable=False),
        sa.Column("summary_fa", sa.Text(), nullable=False),
    )
    op.create_table(
        "process_steps",
        *_timestamps(),
        sa.Column("publication_state", publication_state, nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("title_en", sa.String(length=180), nullable=False),
        sa.Column("title_fa", sa.String(length=180), nullable=False),
        sa.Column("summary_en", sa.Text(), nullable=False),
        sa.Column("summary_fa", sa.Text(), nullable=False),
    )
    op.create_table(
        "studio_members",
        *_timestamps(),
        sa.Column("publication_state", publication_state, nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("role_en", sa.String(length=180), nullable=False),
        sa.Column("role_fa", sa.String(length=180), nullable=False),
        sa.Column("biography_en", sa.Text()),
        sa.Column("biography_fa", sa.Text()),
    )
    op.create_table(
        "recognitions",
        *_timestamps(),
        sa.Column("publication_state", publication_state, nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("title_en", sa.String(length=240), nullable=False),
        sa.Column("title_fa", sa.String(length=240), nullable=False),
    )
    op.create_table(
        "journal_categories",
        *_timestamps(),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title_en", sa.String(length=160), nullable=False),
        sa.Column("title_fa", sa.String(length=160), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "journal_articles",
        *_timestamps(),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("publication_state", publication_state, nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("title_en", sa.String(length=240), nullable=False),
        sa.Column("title_fa", sa.String(length=240), nullable=False),
        sa.Column("excerpt_en", sa.Text(), nullable=False),
        sa.Column("excerpt_fa", sa.Text(), nullable=False),
        sa.Column("body_en", sa.Text(), nullable=False),
        sa.Column("body_fa", sa.Text(), nullable=False),
        sa.Column("reading_minutes", sa.Integer(), nullable=False),
        sa.Column("cover_image_url", sa.String(length=500)),
        sa.Column("cover_alt_en", sa.String(length=500)),
        sa.Column("cover_alt_fa", sa.String(length=500)),
        sa.ForeignKeyConstraint(["category_id"], ["journal_categories.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "ix_journal_public_archive", "journal_articles", ["publication_state", "published_at"]
    )
    op.create_index(
        "ix_journal_public_search_en",
        "journal_articles",
        ["publication_state", sa.text("lower(title_en)")],
    )
    op.create_index(
        "ix_journal_public_search_fa",
        "journal_articles",
        ["publication_state", sa.text("lower(title_fa)")],
    )


def downgrade() -> None:
    op.drop_index("ix_journal_public_search_fa", table_name="journal_articles")
    op.drop_index("ix_journal_public_search_en", table_name="journal_articles")
    op.drop_index("ix_journal_public_archive", table_name="journal_articles")
    op.drop_table("journal_articles")
    op.drop_table("journal_categories")
    op.drop_table("recognitions")
    op.drop_table("studio_members")
    op.drop_table("process_steps")
    op.drop_table("expertise")
    op.drop_table("project_typologies")
    op.drop_table("project_disciplines")
    op.drop_index("ix_projects_public_search_fa", table_name="projects")
    op.drop_index("ix_projects_public_search_en", table_name="projects")
    op.drop_index("ix_projects_public_location", table_name="projects")
    op.drop_index("ix_projects_public_archive", table_name="projects")
    op.drop_table("projects")
    op.drop_table("typologies")
    op.drop_table("disciplines")
    op.drop_table("site_settings")
    publication_state.drop(op.get_bind(), checkfirst=True)
