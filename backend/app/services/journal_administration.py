from __future__ import annotations

from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.admin import AdminUser
from app.models.content import (
    JournalArticle,
    JournalArticleBlock,
    JournalCategory,
    PublicationState,
)
from app.schemas.admin import (
    AdminJournalArticleBlockResponse,
    AdminJournalArticleListItemResponse,
    AdminJournalArticleListResponse,
    AdminJournalArticleResponse,
    AdminJournalCategoryListResponse,
    AdminJournalCategoryResponse,
    AdminJournalCategoryWriteRequest,
    JournalArticleBlockType,
    JournalArticleBlockWriteRequest,
    JournalArticleCreateRequest,
    JournalArticleUpdateRequest,
    JournalCategoryReorderRequest,
)
from app.services.admin_auth import record_audit_event
from app.services.public_cache import TaggedPublicCache


class JournalAdministrationError(RuntimeError):
    """Base error for journal administration workflows."""


class JournalCategoryNotFoundError(JournalAdministrationError):
    pass


class JournalCategoryConflictError(JournalAdministrationError):
    pass


class JournalCategoryInUseError(JournalAdministrationError):
    pass


class JournalCategoryReorderError(JournalAdministrationError):
    pass


class JournalArticleNotFoundError(JournalAdministrationError):
    pass


class JournalArticleSlugConflictError(JournalAdministrationError):
    pass


class JournalArticlePublishingValidationError(JournalAdministrationError):
    def __init__(self, fields: list[str]) -> None:
        super().__init__("journal article cannot be published")
        self.fields = fields


class JournalAdministrationService:
    """Administrator workflows for ordered categories and bilingual journal articles."""

    def __init__(self, session: Session, cache: TaggedPublicCache) -> None:
        self.session = session
        self.cache = cache

    def list_categories(self) -> AdminJournalCategoryListResponse:
        categories = self.session.scalars(
            select(JournalCategory).order_by(
                JournalCategory.display_order, JournalCategory.title_en, JournalCategory.id
            )
        ).all()
        return AdminJournalCategoryListResponse(
            items=[_category_response(category) for category in categories]
        )

    def create_category(
        self, payload: AdminJournalCategoryWriteRequest, administrator: AdminUser
    ) -> AdminJournalCategoryResponse:
        if (
            self.session.scalar(
                select(JournalCategory.id).where(JournalCategory.slug == payload.slug)
            )
            is not None
        ):
            raise JournalCategoryConflictError()
        self._lock_categories_for_append()
        highest = self.session.scalar(select(func.max(JournalCategory.display_order)))
        category = JournalCategory(
            slug=payload.slug,
            title_en=payload.title_en,
            title_fa=payload.title_fa,
            display_order=int(highest) + 1 if highest is not None else 0,
        )
        self.session.add(category)
        self.session.flush()
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="journal_category.created",
            target_type="journal_category",
            target_id=category.id,
        )
        self._commit_category_or_raise()
        return _category_response(category)

    def update_category(
        self,
        category_id: UUID,
        payload: AdminJournalCategoryWriteRequest,
        administrator: AdminUser,
    ) -> AdminJournalCategoryResponse:
        category = self._category_or_raise(category_id, lock=True)
        affected_slugs = self._published_article_slugs(category.id)
        category.slug = payload.slug
        category.title_en = payload.title_en
        category.title_fa = payload.title_fa
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="journal_category.updated",
            target_type="journal_category",
            target_id=category.id,
        )
        self._commit_category_or_raise()
        self._invalidate_articles(affected_slugs)
        return _category_response(category)

    def reorder_categories(
        self, payload: JournalCategoryReorderRequest, administrator: AdminUser
    ) -> AdminJournalCategoryListResponse:
        categories = self.session.scalars(
            select(JournalCategory)
            .order_by(JournalCategory.display_order, JournalCategory.title_en, JournalCategory.id)
            .with_for_update()
        ).all()
        if {category.id for category in categories} != set(payload.identifiers):
            raise JournalCategoryReorderError(
                "the complete journal category collection is required for reordering"
            )
        by_id = {category.id: category for category in categories}
        ordered = [by_id[category_id] for category_id in payload.identifiers]
        for position, category in enumerate(ordered, start=1):
            category.display_order = -position
        self.session.flush()
        for position, category in enumerate(ordered):
            category.display_order = position
            record_audit_event(
                self.session,
                actor_id=administrator.id,
                action="journal_category.reordered",
                target_type="journal_category",
                target_id=category.id,
            )
        self._commit_category_or_raise()
        return self.list_categories()

    def delete_category(self, category_id: UUID, administrator: AdminUser) -> None:
        category = self._category_or_raise(category_id, lock=True)
        if (
            self.session.scalar(
                select(JournalArticle.id).where(JournalArticle.category_id == category.id).limit(1)
            )
            is not None
        ):
            raise JournalCategoryInUseError(
                "move or delete every journal article before deleting its category"
            )
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="journal_category.deleted",
            target_type="journal_category",
            target_id=category.id,
        )
        self.session.delete(category)
        self._commit_category_or_raise()

    def list_articles(self) -> AdminJournalArticleListResponse:
        articles = self.session.scalars(
            select(JournalArticle)
            .options(selectinload(JournalArticle.category))
            .order_by(
                JournalArticle.published_at.desc(),
                JournalArticle.created_at.desc(),
                JournalArticle.id,
            )
        ).all()
        return AdminJournalArticleListResponse(
            items=[_article_list_item(article) for article in articles]
        )

    def article(self, article_id: UUID) -> AdminJournalArticleResponse:
        return _article_response(self._article_or_raise(article_id))

    def create_article(
        self, payload: JournalArticleCreateRequest, administrator: AdminUser
    ) -> AdminJournalArticleResponse:
        if (
            self.session.scalar(
                select(JournalArticle.id).where(JournalArticle.slug == payload.slug)
            )
            is not None
        ):
            raise JournalArticleSlugConflictError()
        article = JournalArticle(slug=payload.slug)
        self.session.add(article)
        self._apply_article_fields(article, payload)
        self.session.flush()
        self._validate_publishable(article)
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="journal_article.created",
            target_type="journal_article",
            target_id=article.id,
        )
        self._commit_article_or_raise()
        if article.publication_state == PublicationState.PUBLISHED:
            self._invalidate_articles([article.slug])
        return _article_response(article)

    def update_article(
        self,
        article_id: UUID,
        payload: JournalArticleUpdateRequest,
        administrator: AdminUser,
    ) -> AdminJournalArticleResponse:
        article = self._article_or_raise(article_id, lock=True)
        was_published = article.publication_state == PublicationState.PUBLISHED
        self._apply_article_fields(article, payload)
        self._validate_publishable(article)
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="journal_article.updated",
            target_type="journal_article",
            target_id=article.id,
        )
        self._commit_article_or_raise()
        if was_published or article.publication_state == PublicationState.PUBLISHED:
            self._invalidate_articles([article.slug])
        return _article_response(article)

    def delete_article(self, article_id: UUID, administrator: AdminUser) -> None:
        article = self._article_or_raise(article_id, lock=True)
        was_published = article.publication_state == PublicationState.PUBLISHED
        slug = article.slug
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="journal_article.deleted",
            target_type="journal_article",
            target_id=article.id,
        )
        self.session.delete(article)
        self._commit_article_or_raise()
        if was_published:
            self._invalidate_articles([slug])

    def _category_or_raise(self, category_id: UUID, *, lock: bool = False) -> JournalCategory:
        statement = select(JournalCategory).where(JournalCategory.id == category_id)
        if lock:
            statement = statement.with_for_update()
        category = self.session.scalar(statement)
        if category is None:
            raise JournalCategoryNotFoundError()
        return category

    def _article_or_raise(self, article_id: UUID, *, lock: bool = False) -> JournalArticle:
        statement = (
            select(JournalArticle)
            .where(JournalArticle.id == article_id)
            .options(selectinload(JournalArticle.category), selectinload(JournalArticle.blocks))
        )
        if lock:
            statement = statement.with_for_update()
        article = self.session.scalar(statement)
        if article is None:
            raise JournalArticleNotFoundError()
        return article

    def _apply_article_fields(
        self,
        article: JournalArticle,
        payload: JournalArticleCreateRequest | JournalArticleUpdateRequest,
    ) -> None:
        with self.session.no_autoflush:
            category = self._category_or_raise(payload.category_id)
        article.category = category
        article.publication_state = payload.publication_state
        article.title_en = payload.title_en
        article.title_fa = payload.title_fa
        article.excerpt_en = payload.excerpt_en
        article.excerpt_fa = payload.excerpt_fa
        article.reading_minutes = payload.reading_minutes
        article.cover_image_url = payload.cover_image_url
        article.cover_alt_en = payload.cover_alt_en
        article.cover_alt_fa = payload.cover_alt_fa
        article.seo_title_en = payload.seo_title_en
        article.seo_title_fa = payload.seo_title_fa
        article.seo_description_en = payload.seo_description_en
        article.seo_description_fa = payload.seo_description_fa
        if payload.publication_state == PublicationState.PUBLISHED:
            article.published_at = _published_at(payload.published_at, article.published_at)
        else:
            article.published_at = None
        article.body_en = _legacy_body(payload.blocks, "en")
        article.body_fa = _legacy_body(payload.blocks, "fa")
        self._replace_blocks(article, payload.blocks)

    def _replace_blocks(
        self,
        article: JournalArticle,
        blocks: list[JournalArticleBlockWriteRequest],
    ) -> None:
        article.blocks.clear()
        self.session.flush()
        for display_order, block in enumerate(blocks):
            article.blocks.append(
                JournalArticleBlock(
                    block_type=block.block_type,
                    content_en=block.content_en,
                    content_fa=block.content_fa,
                    display_order=display_order,
                )
            )
        self.session.flush()

    @staticmethod
    def _validate_publishable(article: JournalArticle) -> None:
        if article.publication_state != PublicationState.PUBLISHED:
            return
        missing: list[str] = []
        for field in ("title_en", "title_fa", "excerpt_en", "excerpt_fa"):
            if not getattr(article, field).strip():
                missing.append(field)
        if article.published_at is None:
            missing.append("published_at")
        if not article.blocks:
            missing.append("blocks")
        if article.cover_image_url is not None and (
            not article.cover_alt_en or not article.cover_alt_fa
        ):
            missing.extend(("cover_alt_en", "cover_alt_fa"))
        if missing:
            raise JournalArticlePublishingValidationError(missing)

    def _published_article_slugs(self, category_id: UUID | None = None) -> list[str]:
        statement = select(JournalArticle.slug).where(
            JournalArticle.publication_state == PublicationState.PUBLISHED,
            JournalArticle.published_at.is_not(None),
        )
        if category_id is not None:
            statement = statement.where(JournalArticle.category_id == category_id)
        return list(self.session.scalars(statement).all())

    def _commit_category_or_raise(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise JournalCategoryConflictError() from error

    def _commit_article_or_raise(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise JournalArticleSlugConflictError() from error

    def _invalidate_articles(self, slugs: list[str]) -> None:
        if not slugs:
            return
        tags = {"home", "home:en", "home:fa", "journal-list", "journal-list:en", "journal-list:fa"}
        for slug in slugs:
            tags.update({f"article:{slug}", f"article:{slug}:en", f"article:{slug}:fa"})
        self.cache.invalidate(tags)

    def _lock_categories_for_append(self) -> None:
        if self.session.get_bind().dialect.name != "postgresql":
            return
        self.session.execute(text("LOCK TABLE journal_categories IN SHARE ROW EXCLUSIVE MODE"))


def _published_at(value: datetime | None, current: datetime | None) -> datetime:
    if value is None:
        return current or datetime.now(UTC)
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _legacy_body(blocks: list[JournalArticleBlockWriteRequest], locale: str) -> str:
    paragraphs: list[str] = []
    for block in blocks:
        if block.block_type != "text":
            continue
        content = block.content_fa if locale == "fa" else block.content_en
        body = content.get("body")
        if isinstance(body, str) and body.strip():
            paragraphs.append(body.strip())
    return "\n\n".join(paragraphs)


def _category_response(category: JournalCategory) -> AdminJournalCategoryResponse:
    return AdminJournalCategoryResponse(
        id=category.id,
        slug=category.slug,
        title_en=category.title_en,
        title_fa=category.title_fa,
        display_order=category.display_order,
    )


def _article_list_item(article: JournalArticle) -> AdminJournalArticleListItemResponse:
    return AdminJournalArticleListItemResponse(
        id=article.id,
        slug=article.slug,
        publication_state=article.publication_state,
        published_at=article.published_at,
        category=_category_response(article.category),
        title_en=article.title_en,
        title_fa=article.title_fa,
        updated_at=article.updated_at,
    )


def _article_response(article: JournalArticle) -> AdminJournalArticleResponse:
    return AdminJournalArticleResponse(
        **_article_list_item(article).model_dump(),
        excerpt_en=article.excerpt_en,
        excerpt_fa=article.excerpt_fa,
        reading_minutes=article.reading_minutes,
        cover_image_url=article.cover_image_url,
        cover_alt_en=article.cover_alt_en,
        cover_alt_fa=article.cover_alt_fa,
        seo_title_en=article.seo_title_en,
        seo_title_fa=article.seo_title_fa,
        seo_description_en=article.seo_description_en,
        seo_description_fa=article.seo_description_fa,
        blocks=[
            AdminJournalArticleBlockResponse(
                id=block.id,
                block_type=cast(JournalArticleBlockType, block.block_type),
                content_en=block.content_en,
                content_fa=block.content_fa,
                display_order=block.display_order,
            )
            for block in article.blocks
        ],
    )
