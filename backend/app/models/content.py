from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampedUUIDModel


class PublicationState(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


project_disciplines = Table(
    "project_disciplines",
    Base.metadata,
    Column(
        "project_id",
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "discipline_id",
        Uuid(as_uuid=True),
        ForeignKey("disciplines.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)

project_typologies = Table(
    "project_typologies",
    Base.metadata,
    Column(
        "project_id",
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "typology_id",
        Uuid(as_uuid=True),
        ForeignKey("typologies.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class SiteSettings(TimestampedUUIDModel):
    __tablename__ = "site_settings"

    studio_name: Mapped[str] = mapped_column(String(120), default="VOLUMA", nullable=False)
    home_title_en: Mapped[str] = mapped_column(Text, nullable=False)
    home_title_fa: Mapped[str] = mapped_column(Text, nullable=False)
    home_body_en: Mapped[str] = mapped_column(Text, nullable=False)
    home_body_fa: Mapped[str] = mapped_column(Text, nullable=False)
    home_hero_image_url: Mapped[str | None] = mapped_column(String(500))
    home_hero_alt_en: Mapped[str | None] = mapped_column(String(500))
    home_hero_alt_fa: Mapped[str | None] = mapped_column(String(500))
    studio_intro_en: Mapped[str] = mapped_column(Text, nullable=False)
    studio_intro_fa: Mapped[str] = mapped_column(Text, nullable=False)
    studio_principles_en: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    studio_principles_fa: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    privacy_en: Mapped[str] = mapped_column(Text, nullable=False)
    privacy_fa: Mapped[str] = mapped_column(Text, nullable=False)


class Discipline(TimestampedUUIDModel):
    __tablename__ = "disciplines"

    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    title_en: Mapped[str] = mapped_column(String(160), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(160), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Typology(TimestampedUUIDModel):
    __tablename__ = "typologies"

    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    title_en: Mapped[str] = mapped_column(String(160), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(160), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Project(TimestampedUUIDModel):
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_public_archive", "publication_state", "display_order", "published_at"),
        Index("ix_projects_public_location", "publication_state", "location_en"),
    )

    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    publication_state: Mapped[PublicationState] = mapped_column(
        Enum(PublicationState, name="publication_state"),
        default=PublicationState.DRAFT,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    title_en: Mapped[str] = mapped_column(String(240), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(240), nullable=False)
    subtitle_en: Mapped[str | None] = mapped_column(String(320))
    subtitle_fa: Mapped[str | None] = mapped_column(String(320))
    summary_en: Mapped[str] = mapped_column(Text, nullable=False)
    summary_fa: Mapped[str] = mapped_column(Text, nullable=False)
    location_en: Mapped[str] = mapped_column(String(160), nullable=False)
    location_fa: Mapped[str] = mapped_column(String(160), nullable=False)
    completion_year: Mapped[int | None] = mapped_column(Integer)
    status_en: Mapped[str | None] = mapped_column(String(100))
    status_fa: Mapped[str | None] = mapped_column(String(100))
    area_en: Mapped[str | None] = mapped_column(String(100))
    area_fa: Mapped[str | None] = mapped_column(String(100))
    scope_en: Mapped[str | None] = mapped_column(String(240))
    scope_fa: Mapped[str | None] = mapped_column(String(240))
    intro_title_en: Mapped[str | None] = mapped_column(String(240))
    intro_title_fa: Mapped[str | None] = mapped_column(String(240))
    intro_en: Mapped[str | None] = mapped_column(Text)
    intro_fa: Mapped[str | None] = mapped_column(Text)
    narrative_title_en: Mapped[str | None] = mapped_column(String(240))
    narrative_title_fa: Mapped[str | None] = mapped_column(String(240))
    narrative_en: Mapped[str | None] = mapped_column(Text)
    narrative_fa: Mapped[str | None] = mapped_column(Text)
    quote_en: Mapped[str | None] = mapped_column(Text)
    quote_fa: Mapped[str | None] = mapped_column(Text)
    material_title_en: Mapped[str | None] = mapped_column(String(240))
    material_title_fa: Mapped[str | None] = mapped_column(String(240))
    material_en: Mapped[str | None] = mapped_column(Text)
    material_fa: Mapped[str | None] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    cover_alt_en: Mapped[str | None] = mapped_column(String(500))
    cover_alt_fa: Mapped[str | None] = mapped_column(String(500))
    gallery_images: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list, nullable=False)
    disciplines: Mapped[list[Discipline]] = relationship(secondary=project_disciplines)
    typologies: Mapped[list[Typology]] = relationship(secondary=project_typologies)


class Expertise(TimestampedUUIDModel):
    __tablename__ = "expertise"

    publication_state: Mapped[PublicationState] = mapped_column(
        Enum(PublicationState, name="publication_state"),
        default=PublicationState.DRAFT,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    title_en: Mapped[str] = mapped_column(String(180), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(180), nullable=False)
    summary_en: Mapped[str] = mapped_column(Text, nullable=False)
    summary_fa: Mapped[str] = mapped_column(Text, nullable=False)


class ProcessStep(TimestampedUUIDModel):
    __tablename__ = "process_steps"

    publication_state: Mapped[PublicationState] = mapped_column(
        Enum(PublicationState, name="publication_state"),
        default=PublicationState.DRAFT,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    title_en: Mapped[str] = mapped_column(String(180), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(180), nullable=False)
    summary_en: Mapped[str] = mapped_column(Text, nullable=False)
    summary_fa: Mapped[str] = mapped_column(Text, nullable=False)


class StudioMember(TimestampedUUIDModel):
    __tablename__ = "studio_members"

    publication_state: Mapped[PublicationState] = mapped_column(
        Enum(PublicationState, name="publication_state"),
        default=PublicationState.DRAFT,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    role_en: Mapped[str] = mapped_column(String(180), nullable=False)
    role_fa: Mapped[str] = mapped_column(String(180), nullable=False)
    biography_en: Mapped[str | None] = mapped_column(Text)
    biography_fa: Mapped[str | None] = mapped_column(Text)


class Recognition(TimestampedUUIDModel):
    __tablename__ = "recognitions"

    publication_state: Mapped[PublicationState] = mapped_column(
        Enum(PublicationState, name="publication_state"),
        default=PublicationState.DRAFT,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    title_en: Mapped[str] = mapped_column(String(240), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(240), nullable=False)


class JournalCategory(TimestampedUUIDModel):
    __tablename__ = "journal_categories"

    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    title_en: Mapped[str] = mapped_column(String(160), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(160), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class JournalArticle(TimestampedUUIDModel):
    __tablename__ = "journal_articles"
    __table_args__ = (Index("ix_journal_public_archive", "publication_state", "published_at"),)

    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    publication_state: Mapped[PublicationState] = mapped_column(
        Enum(PublicationState, name="publication_state"),
        default=PublicationState.DRAFT,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("journal_categories.id", ondelete="RESTRICT")
    )
    category: Mapped[JournalCategory] = relationship()
    title_en: Mapped[str] = mapped_column(String(240), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(240), nullable=False)
    excerpt_en: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt_fa: Mapped[str] = mapped_column(Text, nullable=False)
    body_en: Mapped[str] = mapped_column(Text, nullable=False)
    body_fa: Mapped[str] = mapped_column(Text, nullable=False)
    reading_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    cover_alt_en: Mapped[str | None] = mapped_column(String(500))
    cover_alt_fa: Mapped[str | None] = mapped_column(String(500))
