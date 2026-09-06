from __future__ import annotations

from typing import cast

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.content import (
    Discipline,
    Expertise,
    JournalArticle,
    JournalCategory,
    ProcessStep,
    Project,
    PublicationState,
    Recognition,
    SiteSettings,
    StudioMember,
    Typology,
)
from app.schemas.admin import QuoteBlockPayload, TextBlockPayload
from app.schemas.public import (
    EditorialSectionResponse,
    ExpertiseResponse,
    HomeResponse,
    ImageResponse,
    JournalArticleResponse,
    JournalCardResponse,
    JournalCategoryResponse,
    JournalListResponse,
    Locale,
    PaginationResponse,
    ProcessStepResponse,
    ProjectCardResponse,
    ProjectDetailResponse,
    ProjectEditorialBlockResponse,
    ProjectListResponse,
    QuoteEditorialBlockResponse,
    SearchResponse,
    SearchResultResponse,
    SiteResponse,
    StudioMemberResponse,
    StudioPrincipleResponse,
    StudioResponse,
    TaxonomyResponse,
    TextEditorialBlockResponse,
)

DEFAULT_PAGE_LIMIT = 12
MAX_PAGE_LIMIT = 24


def _locale_field(record: object, field: str, locale: Locale) -> str | None:
    return cast(str | None, getattr(record, f"{field}_{locale}"))


def _published_projects(*, include_blocks: bool = False) -> Select[tuple[Project]]:
    options = [selectinload(Project.disciplines), selectinload(Project.typologies)]
    if include_blocks:
        options.append(selectinload(Project.blocks))
    return (
        select(Project)
        .where(
            Project.publication_state == PublicationState.PUBLISHED,
            Project.published_at.is_not(None),
        )
        .options(*options)
    )


def _published_articles(*, include_blocks: bool = False) -> Select[tuple[JournalArticle]]:
    options = [selectinload(JournalArticle.category)]
    if include_blocks:
        options.append(selectinload(JournalArticle.blocks))
    return (
        select(JournalArticle)
        .where(
            JournalArticle.publication_state == PublicationState.PUBLISHED,
            JournalArticle.published_at.is_not(None),
        )
        .options(*options)
    )


def _image(url: str | None, alt: str | None) -> ImageResponse | None:
    if url is None or alt is None:
        return None
    return ImageResponse(url=url, alt=alt)


def _taxonomy_response(taxonomy: Discipline | Typology, locale: Locale) -> TaxonomyResponse:
    title = _locale_field(taxonomy, "title", locale)
    assert title is not None
    return TaxonomyResponse(slug=taxonomy.slug, title=title)


def project_card(project: Project, locale: Locale) -> ProjectCardResponse:
    title = _locale_field(project, "title", locale)
    summary = _locale_field(project, "summary", locale)
    location = _locale_field(project, "location", locale)
    assert title is not None and summary is not None and location is not None
    return ProjectCardResponse(
        slug=project.slug,
        title=title,
        subtitle=_locale_field(project, "subtitle", locale),
        summary=summary,
        location=location,
        completion_year=project.completion_year,
        status=_locale_field(project, "status", locale),
        cover_image=_image(
            project.cover_image_url,
            _locale_field(project, "cover_alt", locale),
        ),
        disciplines=[_taxonomy_response(item, locale) for item in project.disciplines],
        typologies=[_taxonomy_response(item, locale) for item in project.typologies],
    )


def project_detail(project: Project, locale: Locale) -> ProjectDetailResponse:
    card = project_card(project, locale)

    def section(prefix: str) -> EditorialSectionResponse | None:
        title = _locale_field(project, f"{prefix}_title", locale)
        body = _locale_field(project, prefix, locale)
        if title is None or body is None:
            return None
        return EditorialSectionResponse(title=title, body=body)

    return ProjectDetailResponse(
        **card.model_dump(),
        area=_locale_field(project, "area", locale),
        scope=_locale_field(project, "scope", locale),
        introduction=section("intro"),
        narrative=section("narrative"),
        quote=_locale_field(project, "quote", locale),
        material=section("material"),
        gallery=[
            ImageResponse(url=image["url"], alt=image[f"alt_{locale}"])
            for image in project.gallery_images
            if image.get("url") and image.get(f"alt_{locale}")
        ],
        blocks=_project_blocks(project, locale),
        seo_title=_locale_field(project, "seo_title", locale) or card.title,
        seo_description=_locale_field(project, "seo_description", locale) or card.summary,
    )


def _project_blocks(project: Project, locale: Locale) -> list[ProjectEditorialBlockResponse]:
    """Expose only block types whose public renderer needs no unresolved media asset."""

    blocks: list[ProjectEditorialBlockResponse] = []
    for block in project.blocks:
        content = block.content_fa if locale == "fa" else block.content_en
        if block.block_type == "text":
            text_payload = TextBlockPayload.model_validate(content)
            blocks.append(
                TextEditorialBlockResponse(
                    block_type="text", heading=text_payload.heading, body=text_payload.body
                )
            )
        elif block.block_type == "quote":
            quote_payload = QuoteBlockPayload.model_validate(content)
            blocks.append(
                QuoteEditorialBlockResponse(
                    block_type="quote",
                    quote=quote_payload.quote,
                    attribution=quote_payload.attribution,
                )
            )
    return blocks


def journal_card(article: JournalArticle, locale: Locale) -> JournalCardResponse:
    title = _locale_field(article, "title", locale)
    excerpt = _locale_field(article, "excerpt", locale)
    category_title = _locale_field(article.category, "title", locale)
    assert title is not None and excerpt is not None and category_title is not None
    assert article.published_at is not None
    return JournalCardResponse(
        slug=article.slug,
        title=title,
        excerpt=excerpt,
        category=JournalCategoryResponse(slug=article.category.slug, title=category_title),
        published_at=article.published_at,
        reading_minutes=article.reading_minutes,
        cover_image=_image(article.cover_image_url, _locale_field(article, "cover_alt", locale)),
    )


def _journal_blocks(article: JournalArticle, locale: Locale) -> list[ProjectEditorialBlockResponse]:
    blocks: list[ProjectEditorialBlockResponse] = []
    for block in article.blocks:
        content = block.content_fa if locale == "fa" else block.content_en
        if block.block_type == "text":
            text_payload = TextBlockPayload.model_validate(content)
            blocks.append(
                TextEditorialBlockResponse(
                    block_type="text", heading=text_payload.heading, body=text_payload.body
                )
            )
        elif block.block_type == "quote":
            quote_payload = QuoteBlockPayload.model_validate(content)
            blocks.append(
                QuoteEditorialBlockResponse(
                    block_type="quote",
                    quote=quote_payload.quote,
                    attribution=quote_payload.attribution,
                )
            )
    return blocks


class PublicContentService:
    """Purpose-built, published-only public content queries."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def site(self, locale: Locale) -> SiteResponse | None:
        settings = self._settings()
        if settings is None:
            return None
        privacy = _locale_field(settings, "privacy", locale)
        assert privacy is not None
        return SiteResponse(studio_name=settings.studio_name, privacy=privacy)

    def home(self, locale: Locale) -> HomeResponse | None:
        settings = self._settings()
        if settings is None:
            return None

        selected = self.session.scalars(
            _published_projects()
            .where(Project.featured.is_(True))
            .order_by(Project.display_order, Project.published_at.desc(), Project.slug)
            .limit(4)
        ).all()
        expertise = self.session.scalars(
            select(Expertise)
            .where(Expertise.publication_state == PublicationState.PUBLISHED)
            .order_by(Expertise.display_order, Expertise.id)
            .limit(6)
        ).all()
        process = self.session.scalars(
            select(ProcessStep)
            .where(ProcessStep.publication_state == PublicationState.PUBLISHED)
            .order_by(ProcessStep.display_order, ProcessStep.id)
            .limit(6)
        ).all()
        articles = self.session.scalars(
            _published_articles()
            .order_by(JournalArticle.published_at.desc(), JournalArticle.slug)
            .limit(3)
        ).all()

        hero_title = _locale_field(settings, "home_title", locale)
        hero_body = _locale_field(settings, "home_body", locale)
        assert hero_title is not None and hero_body is not None
        return HomeResponse(
            studio_name=settings.studio_name,
            hero_title=hero_title,
            hero_body=hero_body,
            hero_image=_image(
                settings.home_hero_image_url,
                _locale_field(settings, "home_hero_alt", locale),
            ),
            selected_projects=[project_card(project, locale) for project in selected],
            expertise=[self._expertise_response(item, locale) for item in expertise],
            process=[self._process_response(item, locale) for item in process],
            journal=[journal_card(article, locale) for article in articles],
        )

    def projects(
        self,
        locale: Locale,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        query: str | None = None,
        discipline: str | None = None,
        typology: str | None = None,
        status: str | None = None,
        location: str | None = None,
        year: int | None = None,
    ) -> ProjectListResponse:
        statement = _published_projects()
        statement = self._project_filters(
            statement,
            locale=locale,
            query=query,
            discipline=discipline,
            typology=typology,
            status=status,
            location=location,
            year=year,
        )
        total = self.session.scalar(
            select(func.count()).select_from(statement.order_by(None).subquery())
        )
        projects = self.session.scalars(
            statement.order_by(Project.display_order, Project.published_at.desc(), Project.slug)
            .offset(offset)
            .limit(limit)
        ).all()
        return ProjectListResponse(
            items=[project_card(project, locale) for project in projects],
            pagination=PaginationResponse(limit=limit, offset=offset, total=total or 0),
        )

    def project(self, slug: str, locale: Locale) -> ProjectDetailResponse | None:
        project = self.session.scalar(
            _published_projects(include_blocks=True).where(Project.slug == slug)
        )
        return project_detail(project, locale) if project is not None else None

    def expertise(self, locale: Locale) -> list[ExpertiseResponse]:
        records = self.session.scalars(
            select(Expertise)
            .where(Expertise.publication_state == PublicationState.PUBLISHED)
            .order_by(Expertise.display_order, Expertise.id)
        ).all()
        return [self._expertise_response(record, locale) for record in records]

    def process(self, locale: Locale) -> list[ProcessStepResponse]:
        records = self.session.scalars(
            select(ProcessStep)
            .where(ProcessStep.publication_state == PublicationState.PUBLISHED)
            .order_by(ProcessStep.display_order, ProcessStep.id)
        ).all()
        return [self._process_response(record, locale) for record in records]

    def studio(self, locale: Locale) -> StudioResponse | None:
        settings = self._settings()
        if settings is None:
            return None
        intro = _locale_field(settings, "studio_intro", locale)
        assert intro is not None
        principles: list[dict[str, str]] = (
            settings.studio_principles_fa if locale == "fa" else settings.studio_principles_en
        )
        members = self.session.scalars(
            select(StudioMember)
            .where(StudioMember.publication_state == PublicationState.PUBLISHED)
            .order_by(StudioMember.display_order, StudioMember.id)
        ).all()
        recognitions = self.session.scalars(
            select(Recognition)
            .where(Recognition.publication_state == PublicationState.PUBLISHED)
            .order_by(Recognition.display_order, Recognition.id)
        ).all()
        return StudioResponse(
            intro=intro,
            principles=[StudioPrincipleResponse.model_validate(value) for value in principles],
            members=[
                StudioMemberResponse(
                    name=member.name,
                    role=_locale_field(member, "role", locale) or "",
                    biography=_locale_field(member, "biography", locale),
                )
                for member in members
            ],
            recognitions=[_locale_field(record, "title", locale) or "" for record in recognitions],
        )

    def journal(
        self,
        locale: Locale,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        category: str | None = None,
    ) -> JournalListResponse:
        statement = _published_articles()
        if category:
            statement = statement.where(
                JournalArticle.category.has(JournalCategory.slug == category)
            )
        total = self.session.scalar(
            select(func.count()).select_from(statement.order_by(None).subquery())
        )
        articles = self.session.scalars(
            statement.order_by(JournalArticle.published_at.desc(), JournalArticle.slug)
            .offset(offset)
            .limit(limit)
        ).all()
        return JournalListResponse(
            items=[journal_card(article, locale) for article in articles],
            pagination=PaginationResponse(limit=limit, offset=offset, total=total or 0),
        )

    def article(self, slug: str, locale: Locale) -> JournalArticleResponse | None:
        article = self.session.scalar(
            _published_articles(include_blocks=True).where(JournalArticle.slug == slug)
        )
        if article is None:
            return None
        blocks = _journal_blocks(article, locale)
        body = [
            paragraph
            for block in blocks
            if block.block_type == "text"
            for paragraph in self._paragraphs(block.body)
        ]
        if not body:
            legacy_body = _locale_field(article, "body", locale)
            assert legacy_body is not None
            body = self._paragraphs(legacy_body)
        card = journal_card(article, locale)
        return JournalArticleResponse(
            **card.model_dump(),
            body=body,
            blocks=blocks,
            seo_title=_locale_field(article, "seo_title", locale) or card.title,
            seo_description=_locale_field(article, "seo_description", locale) or card.excerpt,
        )

    def search(self, locale: Locale, query: str, *, limit: int = 10) -> SearchResponse:
        normalized = query.strip()
        if not normalized:
            return SearchResponse(query="", items=[])
        pattern = f"%{normalized.lower()}%"
        title = Project.title_fa if locale == "fa" else Project.title_en
        subtitle = Project.subtitle_fa if locale == "fa" else Project.subtitle_en
        location = Project.location_fa if locale == "fa" else Project.location_en
        project_matches = self.session.scalars(
            _published_projects()
            .where(
                or_(
                    func.lower(title).like(pattern),
                    func.lower(subtitle).like(pattern),
                    func.lower(location).like(pattern),
                )
            )
            .order_by(Project.display_order, Project.published_at.desc(), Project.slug)
            .limit(limit)
        ).all()
        article_title = JournalArticle.title_fa if locale == "fa" else JournalArticle.title_en
        article_excerpt = JournalArticle.excerpt_fa if locale == "fa" else JournalArticle.excerpt_en
        remaining = max(limit - len(project_matches), 0)
        article_matches = self.session.scalars(
            _published_articles()
            .where(
                or_(
                    func.lower(article_title).like(pattern),
                    func.lower(article_excerpt).like(pattern),
                )
            )
            .order_by(JournalArticle.published_at.desc(), JournalArticle.slug)
            .limit(remaining)
        ).all()
        items = [
            SearchResultResponse(
                kind="project",
                slug=project.slug,
                title=_locale_field(project, "title", locale) or "",
                summary=_locale_field(project, "summary", locale) or "",
            )
            for project in project_matches
        ]
        items.extend(
            SearchResultResponse(
                kind="journal",
                slug=article.slug,
                title=_locale_field(article, "title", locale) or "",
                summary=_locale_field(article, "excerpt", locale) or "",
            )
            for article in article_matches
        )
        return SearchResponse(query=normalized, items=items)

    def _settings(self) -> SiteSettings | None:
        return self.session.scalar(select(SiteSettings).order_by(SiteSettings.created_at).limit(1))

    def _expertise_response(self, record: Expertise, locale: Locale) -> ExpertiseResponse:
        title = _locale_field(record, "title", locale)
        summary = _locale_field(record, "summary", locale)
        assert title is not None and summary is not None
        return ExpertiseResponse(title=title, summary=summary, display_order=record.display_order)

    def _process_response(self, record: ProcessStep, locale: Locale) -> ProcessStepResponse:
        title = _locale_field(record, "title", locale)
        summary = _locale_field(record, "summary", locale)
        assert title is not None and summary is not None
        return ProcessStepResponse(title=title, summary=summary, display_order=record.display_order)

    def _project_filters(
        self,
        statement: Select[tuple[Project]],
        *,
        locale: Locale,
        query: str | None,
        discipline: str | None,
        typology: str | None,
        status: str | None,
        location: str | None,
        year: int | None,
    ) -> Select[tuple[Project]]:
        if query:
            normalized = f"%{query.strip().lower()}%"
            title = Project.title_fa if locale == "fa" else Project.title_en
            subtitle = Project.subtitle_fa if locale == "fa" else Project.subtitle_en
            project_location = Project.location_fa if locale == "fa" else Project.location_en
            statement = statement.where(
                or_(
                    func.lower(title).like(normalized),
                    func.lower(subtitle).like(normalized),
                    func.lower(project_location).like(normalized),
                )
            )
        if discipline:
            statement = statement.where(Project.disciplines.any(Discipline.slug == discipline))
        if typology:
            statement = statement.where(Project.typologies.any(Typology.slug == typology))
        if status:
            status_field = Project.status_fa if locale == "fa" else Project.status_en
            statement = statement.where(status_field == status)
        if location:
            location_field = Project.location_fa if locale == "fa" else Project.location_en
            statement = statement.where(location_field == location)
        if year is not None:
            statement = statement.where(Project.completion_year == year)
        return statement

    @staticmethod
    def _paragraphs(body: str) -> list[str]:
        return [paragraph for paragraph in body.split("\n\n") if paragraph]
