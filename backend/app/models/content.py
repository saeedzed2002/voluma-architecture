from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampedUUIDModel


class PublicationState(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class ContactMessageState(StrEnum):
    NEW = "new"
    READ = "read"
    ARCHIVED = "archived"


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
    __table_args__ = (
        CheckConstraint("singleton IS TRUE", name="ck_site_settings_singleton"),
        CheckConstraint(
            "default_theme IN ('system', 'light', 'dark')",
            name="ck_site_settings_default_theme",
        ),
        UniqueConstraint("singleton", name="uq_site_settings_singleton"),
    )

    singleton: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    studio_name: Mapped[str] = mapped_column(String(120), default="VOLUMA", nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    favicon_url: Mapped[str | None] = mapped_column(String(500))
    contact_email: Mapped[str | None] = mapped_column(String(320))
    contact_phone: Mapped[str | None] = mapped_column(String(64))
    contact_address_en: Mapped[str | None] = mapped_column(Text)
    contact_address_fa: Mapped[str | None] = mapped_column(Text)
    social_links: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list, nullable=False)
    default_theme: Mapped[str] = mapped_column(String(10), default="system", nullable=False)
    default_seo_title_en: Mapped[str | None] = mapped_column(String(240))
    default_seo_title_fa: Mapped[str | None] = mapped_column(String(240))
    default_seo_description_en: Mapped[str | None] = mapped_column(String(320))
    default_seo_description_fa: Mapped[str | None] = mapped_column(String(320))
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


class ContactMessage(TimestampedUUIDModel):
    __tablename__ = "contact_messages"
    __table_args__ = (Index("ix_contact_messages_state_created_at", "state", "created_at"),)

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(64))
    company: Mapped[str | None] = mapped_column(String(160))
    project_type: Mapped[str | None] = mapped_column(String(40))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    source_locale: Mapped[str] = mapped_column(String(2), nullable=False)
    state: Mapped[ContactMessageState] = mapped_column(
        Enum(
            ContactMessageState,
            name="contactmessagestate",
            values_callable=lambda enum_class: [state.value for state in enum_class],
        ),
        default=ContactMessageState.NEW,
        nullable=False,
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Discipline(TimestampedUUIDModel):
    __tablename__ = "disciplines"
    __table_args__ = (UniqueConstraint("display_order", name="uq_disciplines_display_order"),)

    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    title_en: Mapped[str] = mapped_column(String(160), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(160), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Typology(TimestampedUUIDModel):
    __tablename__ = "typologies"
    __table_args__ = (UniqueConstraint("display_order", name="uq_typologies_display_order"),)

    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    title_en: Mapped[str] = mapped_column(String(160), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(160), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Project(TimestampedUUIDModel):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("display_order", name="uq_projects_display_order"),
        Index("ix_projects_public_archive", "publication_state", "display_order", "published_at"),
        Index("ix_projects_public_location", "publication_state", "location_en"),
        Index(
            "ix_projects_public_search_en",
            "publication_state",
            func.lower("title_en"),
            func.lower("location_en"),
        ),
        Index(
            "ix_projects_public_search_fa",
            "publication_state",
            func.lower("title_fa"),
            func.lower("location_fa"),
        ),
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
    client_en: Mapped[str | None] = mapped_column(String(240))
    client_fa: Mapped[str | None] = mapped_column(String(240))
    architect_en: Mapped[str | None] = mapped_column(String(240))
    architect_fa: Mapped[str | None] = mapped_column(String(240))
    collaborators_en: Mapped[str | None] = mapped_column(Text)
    collaborators_fa: Mapped[str | None] = mapped_column(Text)
    completion_date: Mapped[date | None] = mapped_column(Date)
    seo_title_en: Mapped[str | None] = mapped_column(String(240))
    seo_title_fa: Mapped[str | None] = mapped_column(String(240))
    seo_description_en: Mapped[str | None] = mapped_column(String(320))
    seo_description_fa: Mapped[str | None] = mapped_column(String(320))
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
    blocks: Mapped[list[ProjectBlock]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectBlock.display_order",
    )


class ProjectBlock(TimestampedUUIDModel):
    __tablename__ = "project_blocks"
    __table_args__ = (
        CheckConstraint(
            "block_type IN ('text', 'quote', 'single_image', 'full_width_image', "
            "'paired_image', 'gallery')",
            name="ck_project_blocks_type",
        ),
        UniqueConstraint(
            "project_id", "display_order", name="uq_project_blocks_project_display_order"
        ),
        Index("ix_project_blocks_project_order", "project_id", "display_order"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    block_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content_en: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    content_fa: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    project: Mapped[Project] = relationship(back_populates="blocks")


class Expertise(TimestampedUUIDModel):
    __tablename__ = "expertise"
    __table_args__ = (
        UniqueConstraint("display_order", name="uq_expertise_display_order"),
        Index("ix_expertise_public_list", "publication_state", "display_order"),
    )

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
    __table_args__ = (
        UniqueConstraint("display_order", name="uq_process_steps_display_order"),
        Index("ix_process_steps_public_list", "publication_state", "display_order"),
    )

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
    __table_args__ = (
        UniqueConstraint("display_order", name="uq_studio_members_display_order"),
        Index("ix_studio_members_public_list", "publication_state", "display_order"),
    )

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
    __table_args__ = (
        UniqueConstraint("display_order", name="uq_recognitions_display_order"),
        Index("ix_recognitions_public_list", "publication_state", "display_order"),
    )

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
    __table_args__ = (
        UniqueConstraint("display_order", name="uq_journal_categories_display_order"),
    )

    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    title_en: Mapped[str] = mapped_column(String(160), nullable=False)
    title_fa: Mapped[str] = mapped_column(String(160), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class JournalArticle(TimestampedUUIDModel):
    __tablename__ = "journal_articles"
    __table_args__ = (
        Index("ix_journal_public_archive", "publication_state", "published_at"),
        Index("ix_journal_public_search_en", "publication_state", func.lower("title_en")),
        Index("ix_journal_public_search_fa", "publication_state", func.lower("title_fa")),
    )

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
    seo_title_en: Mapped[str | None] = mapped_column(String(240))
    seo_title_fa: Mapped[str | None] = mapped_column(String(240))
    seo_description_en: Mapped[str | None] = mapped_column(String(320))
    seo_description_fa: Mapped[str | None] = mapped_column(String(320))
    blocks: Mapped[list[JournalArticleBlock]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
        order_by="JournalArticleBlock.display_order",
    )


class JournalArticleBlock(TimestampedUUIDModel):
    __tablename__ = "article_blocks"
    __table_args__ = (
        CheckConstraint(
            "block_type IN ('text', 'quote')",
            name="ck_article_blocks_type",
        ),
        UniqueConstraint(
            "article_id", "display_order", name="uq_article_blocks_article_display_order"
        ),
        Index("ix_article_blocks_article_order", "article_id", "display_order"),
    )

    article_id: Mapped[UUID] = mapped_column(
        ForeignKey("journal_articles.id", ondelete="CASCADE"), nullable=False
    )
    block_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content_en: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    content_fa: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    article: Mapped[JournalArticle] = relationship(back_populates="blocks")
