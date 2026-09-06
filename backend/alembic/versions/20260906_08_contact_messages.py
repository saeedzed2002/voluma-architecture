"""Create contact-message intake and administrator triage storage.

Revision ID: 20260906_08
Revises: 20260906_07
Create Date: 2026-09-06 14:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260906_08"
down_revision: str | Sequence[str] | None = "20260906_07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


contact_message_state = postgresql.ENUM(
    "new", "read", "archived", name="contactmessagestate", create_type=False
)


def upgrade() -> None:
    contact_message_state.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "contact_messages",
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
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("phone", sa.String(length=64)),
        sa.Column("company", sa.String(length=160)),
        sa.Column("project_type", sa.String(length=40)),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("source_locale", sa.String(length=2), nullable=False),
        sa.Column(
            "state",
            contact_message_state,
            nullable=False,
            server_default=sa.text("'new'"),
        ),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("source_locale IN ('en', 'fa')", name="ck_contact_messages_locale"),
        sa.CheckConstraint(
            "project_type IS NULL OR project_type IN ('architecture', 'interior', 'reuse')",
            name="ck_contact_messages_project_type",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_contact_messages_state_created_at",
        "contact_messages",
        ["state", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_contact_messages_state_created_at", table_name="contact_messages")
    op.drop_table("contact_messages")
    contact_message_state.drop(op.get_bind(), checkfirst=True)
