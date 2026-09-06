from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from redis.exceptions import RedisError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.admin import AdminUser
from app.models.content import Discipline, Project, ProjectBlock, PublicationState, Typology
from app.schemas.admin import (
    AdminProjectBlockResponse,
    AdminProjectFormOptionsResponse,
    AdminProjectListItemResponse,
    AdminProjectListResponse,
    AdminProjectResponse,
    AdminTaxonomyResponse,
    ProjectBlocksReplaceRequest,
    ProjectBlockType,
    ProjectCreateRequest,
    ProjectReorderRequest,
    ProjectUpdateRequest,
)
from app.services.admin_auth import record_audit_event
from app.services.public_cache import TaggedPublicCache


class ProjectAdministrationError(RuntimeError):
    """Base error for explicit administrator project workflow failures."""


class ProjectNotFoundError(ProjectAdministrationError):
    pass


class ProjectSlugConflictError(ProjectAdministrationError):
    pass


class ProjectTaxonomyError(ProjectAdministrationError):
    pass


class ProjectPublishingValidationError(ProjectAdministrationError):
    def __init__(self, fields: list[str]) -> None:
        super().__init__("project cannot be published")
        self.fields = fields


class ProjectReorderError(ProjectAdministrationError):
    pass


PROJECT_MUTABLE_FIELDS = (
    "featured",
    "title_en",
    "title_fa",
    "subtitle_en",
    "subtitle_fa",
    "summary_en",
    "summary_fa",
    "location_en",
    "location_fa",
    "completion_year",
    "status_en",
    "status_fa",
    "area_en",
    "area_fa",
    "scope_en",
    "scope_fa",
    "client_en",
    "client_fa",
    "architect_en",
    "architect_fa",
    "collaborators_en",
    "collaborators_fa",
    "completion_date",
    "seo_title_en",
    "seo_title_fa",
    "seo_description_en",
    "seo_description_fa",
    "intro_title_en",
    "intro_title_fa",
    "intro_en",
    "intro_fa",
    "narrative_title_en",
    "narrative_title_fa",
    "narrative_en",
    "narrative_fa",
    "quote_en",
    "quote_fa",
    "material_title_en",
    "material_title_fa",
    "material_en",
    "material_fa",
)


class ProjectAdministrationService:
    """Purpose-built administrator workflow for projects and validated editorial blocks."""

    def __init__(self, session: Session, cache: TaggedPublicCache) -> None:
        self.session = session
        self.cache = cache

    def list_projects(self) -> AdminProjectListResponse:
        projects = self.session.scalars(
            select(Project).order_by(Project.display_order, Project.created_at, Project.id)
        ).all()
        return AdminProjectListResponse(items=[_project_list_item(project) for project in projects])

    def project(self, project_id: UUID) -> AdminProjectResponse:
        return _project_response(self._project_or_raise(project_id))

    def form_options(self) -> AdminProjectFormOptionsResponse:
        disciplines = self.session.scalars(
            select(Discipline).order_by(
                Discipline.display_order, Discipline.title_en, Discipline.id
            )
        ).all()
        typologies = self.session.scalars(
            select(Typology).order_by(Typology.display_order, Typology.title_en, Typology.id)
        ).all()
        return AdminProjectFormOptionsResponse(
            disciplines=[_taxonomy_response(record) for record in disciplines],
            typologies=[_taxonomy_response(record) for record in typologies],
        )

    def create(
        self, payload: ProjectCreateRequest, administrator: AdminUser
    ) -> AdminProjectResponse:
        if self.session.scalar(select(Project.id).where(Project.slug == payload.slug)) is not None:
            raise ProjectSlugConflictError()
        project = Project(slug=payload.slug, display_order=self._next_display_order())
        self._apply_fields(project, payload)
        self.session.add(project)
        self.session.flush()
        self._validate_publishable(project)
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="project.created",
            target_type="project",
            target_id=project.id,
        )
        self._commit_or_raise()
        if project.publication_state == PublicationState.PUBLISHED:
            self._invalidate_project(project.slug)
        return _project_response(project)

    def update(
        self, project_id: UUID, payload: ProjectUpdateRequest, administrator: AdminUser
    ) -> AdminProjectResponse:
        project = self._project_or_raise(project_id, lock=True)
        was_published = project.publication_state == PublicationState.PUBLISHED
        self._apply_fields(project, payload)
        self._validate_publishable(project)
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="project.updated",
            target_type="project",
            target_id=project.id,
        )
        self._commit_or_raise()
        if was_published or project.publication_state == PublicationState.PUBLISHED:
            self._invalidate_project(project.slug)
        return _project_response(project)

    def replace_blocks(
        self,
        project_id: UUID,
        payload: ProjectBlocksReplaceRequest,
        administrator: AdminUser,
    ) -> AdminProjectResponse:
        project = self._project_or_raise(project_id, lock=True)
        was_published = project.publication_state == PublicationState.PUBLISHED
        for existing_block in project.blocks:
            self.session.delete(existing_block)
        self.session.flush()
        for display_order, block_request in enumerate(payload.blocks):
            project.blocks.append(
                ProjectBlock(
                    block_type=block_request.block_type,
                    content_en=block_request.content_en,
                    content_fa=block_request.content_fa,
                    display_order=display_order,
                )
            )
        self.session.flush()
        self._validate_publishable(project)
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="project.blocks_replaced",
            target_type="project",
            target_id=project.id,
        )
        self._commit_or_raise()
        if was_published:
            self._invalidate_project(project.slug)
        return _project_response(project)

    def reorder(
        self, payload: ProjectReorderRequest, administrator: AdminUser
    ) -> AdminProjectListResponse:
        projects = self.session.scalars(
            select(Project)
            .order_by(Project.display_order, Project.created_at, Project.id)
            .with_for_update()
        ).all()
        requested = payload.project_ids
        if {project.id for project in projects} != set(requested):
            raise ProjectReorderError("the complete project collection is required for reordering")
        by_id = {project.id: project for project in projects}
        ordered = [by_id[project_id] for project_id in requested]

        # The unique constraint is deliberately preserved throughout the transaction.
        # Negative temporary positions cannot collide with persisted public positions.
        for position, project in enumerate(ordered, start=1):
            project.display_order = -position
        self.session.flush()
        for position, project in enumerate(ordered):
            project.display_order = position
            record_audit_event(
                self.session,
                actor_id=administrator.id,
                action="project.reordered",
                target_type="project",
                target_id=project.id,
            )
        self._commit_or_raise()
        if any(project.publication_state == PublicationState.PUBLISHED for project in ordered):
            self._invalidate_project_collections()
        return self.list_projects()

    def delete(self, project_id: UUID, administrator: AdminUser) -> None:
        project = self._project_or_raise(project_id, lock=True)
        was_published = project.publication_state == PublicationState.PUBLISHED
        slug = project.slug
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="project.deleted",
            target_type="project",
            target_id=project.id,
        )
        self.session.delete(project)
        self._commit_or_raise()
        if was_published:
            self._invalidate_project(slug)

    def _project_or_raise(self, project_id: UUID, *, lock: bool = False) -> Project:
        statement = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.blocks),
                selectinload(Project.disciplines),
                selectinload(Project.typologies),
            )
        )
        if lock:
            statement = statement.with_for_update()
        project = self.session.scalar(statement)
        if project is None:
            raise ProjectNotFoundError()
        return project

    def _next_display_order(self) -> int:
        highest = self.session.scalar(select(func.max(Project.display_order)))
        return int(highest) + 1 if highest is not None else 0

    def _apply_fields(
        self, project: Project, payload: ProjectCreateRequest | ProjectUpdateRequest
    ) -> None:
        for field in PROJECT_MUTABLE_FIELDS:
            setattr(project, field, getattr(payload, field))
        project.disciplines = self._disciplines(payload.discipline_ids)
        project.typologies = self._typologies(payload.typology_ids)
        project.publication_state = payload.publication_state
        if payload.publication_state == PublicationState.PUBLISHED:
            project.published_at = _published_at(payload.published_at)
        else:
            project.published_at = None

    def _disciplines(self, identifiers: list[UUID]) -> list[Discipline]:
        return _ordered_taxonomy(
            self.session.scalars(select(Discipline).where(Discipline.id.in_(identifiers))).all(),
            identifiers,
            "discipline",
        )

    def _typologies(self, identifiers: list[UUID]) -> list[Typology]:
        return _ordered_taxonomy(
            self.session.scalars(select(Typology).where(Typology.id.in_(identifiers))).all(),
            identifiers,
            "typology",
        )

    def _validate_publishable(self, project: Project) -> None:
        if project.publication_state != PublicationState.PUBLISHED:
            return
        missing: list[str] = []
        for field in (
            "title_en",
            "title_fa",
            "summary_en",
            "summary_fa",
            "location_en",
            "location_fa",
        ):
            value = cast(str | None, getattr(project, field))
            if value is None or not value.strip():
                missing.append(field)
        if project.published_at is None:
            missing.append("published_at")
        if project.cover_image_url is not None and (
            not project.cover_alt_en or not project.cover_alt_fa
        ):
            missing.extend(("cover_alt_en", "cover_alt_fa"))
        for index, image in enumerate(project.gallery_images):
            if not image.get("url") or not image.get("alt_en") or not image.get("alt_fa"):
                missing.append(f"gallery_images[{index}]")
        if missing:
            raise ProjectPublishingValidationError(missing)

    def _commit_or_raise(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise ProjectSlugConflictError() from error

    def _invalidate_project(self, slug: str) -> None:
        try:
            self.cache.invalidate(
                {
                    "home",
                    "home:en",
                    "home:fa",
                    "project-list",
                    "project-list:en",
                    "project-list:fa",
                    f"project:{slug}",
                    f"project:{slug}:en",
                    f"project:{slug}:fa",
                }
            )
        except RedisError:
            raise

    def _invalidate_project_collections(self) -> None:
        self.cache.invalidate(
            {"home", "home:en", "home:fa", "project-list", "project-list:en", "project-list:fa"}
        )


def _published_at(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _ordered_taxonomy[T: Discipline | Typology](
    records: Sequence[T], identifiers: list[UUID], label: str
) -> list[T]:
    by_id = {record.id: record for record in records}
    if set(by_id) != set(identifiers):
        raise ProjectTaxonomyError(f"one or more {label} identifiers are invalid")
    return [by_id[identifier] for identifier in identifiers]


def _taxonomy_response(record: Discipline | Typology) -> AdminTaxonomyResponse:
    return AdminTaxonomyResponse(
        id=record.id,
        slug=record.slug,
        title_en=record.title_en,
        title_fa=record.title_fa,
        display_order=record.display_order,
    )


def _project_list_item(project: Project) -> AdminProjectListItemResponse:
    return AdminProjectListItemResponse(
        id=project.id,
        slug=project.slug,
        title_en=project.title_en,
        title_fa=project.title_fa,
        publication_state=project.publication_state,
        published_at=project.published_at,
        display_order=project.display_order,
        featured=project.featured,
        updated_at=project.updated_at,
    )


def _project_response(project: Project) -> AdminProjectResponse:
    return AdminProjectResponse(
        **_project_list_item(project).model_dump(),
        subtitle_en=project.subtitle_en,
        subtitle_fa=project.subtitle_fa,
        summary_en=project.summary_en,
        summary_fa=project.summary_fa,
        location_en=project.location_en,
        location_fa=project.location_fa,
        completion_year=project.completion_year,
        status_en=project.status_en,
        status_fa=project.status_fa,
        area_en=project.area_en,
        area_fa=project.area_fa,
        scope_en=project.scope_en,
        scope_fa=project.scope_fa,
        client_en=project.client_en,
        client_fa=project.client_fa,
        architect_en=project.architect_en,
        architect_fa=project.architect_fa,
        collaborators_en=project.collaborators_en,
        collaborators_fa=project.collaborators_fa,
        completion_date=project.completion_date,
        seo_title_en=project.seo_title_en,
        seo_title_fa=project.seo_title_fa,
        seo_description_en=project.seo_description_en,
        seo_description_fa=project.seo_description_fa,
        intro_title_en=project.intro_title_en,
        intro_title_fa=project.intro_title_fa,
        intro_en=project.intro_en,
        intro_fa=project.intro_fa,
        narrative_title_en=project.narrative_title_en,
        narrative_title_fa=project.narrative_title_fa,
        narrative_en=project.narrative_en,
        narrative_fa=project.narrative_fa,
        quote_en=project.quote_en,
        quote_fa=project.quote_fa,
        material_title_en=project.material_title_en,
        material_title_fa=project.material_title_fa,
        material_en=project.material_en,
        material_fa=project.material_fa,
        disciplines=[_taxonomy_response(record) for record in project.disciplines],
        typologies=[_taxonomy_response(record) for record in project.typologies],
        blocks=[
            AdminProjectBlockResponse(
                id=block.id,
                block_type=cast(ProjectBlockType, block.block_type),
                content_en=block.content_en,
                content_fa=block.content_fa,
                display_order=block.display_order,
            )
            for block in project.blocks
        ],
    )
