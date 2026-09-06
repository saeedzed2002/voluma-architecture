from __future__ import annotations

from typing import Literal, cast
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.admin import AdminUser
from app.models.content import Discipline, Project, PublicationState, Typology
from app.schemas.admin import (
    AdminTaxonomyListResponse,
    AdminTaxonomyResponse,
    AdminTaxonomyWriteRequest,
    TaxonomyReorderRequest,
)
from app.services.admin_auth import record_audit_event
from app.services.public_cache import TaggedPublicCache

TaxonomyKind = Literal["discipline", "typology"]
TaxonomyRecord = Discipline | Typology


class TaxonomyAdministrationError(RuntimeError):
    pass


class TaxonomyNotFoundError(TaxonomyAdministrationError):
    pass


class TaxonomyConflictError(TaxonomyAdministrationError):
    pass


class TaxonomyInUseError(TaxonomyAdministrationError):
    pass


class TaxonomyReorderError(TaxonomyAdministrationError):
    pass


class TaxonomyAdministrationService:
    """Explicit workflows for the two public project taxonomy collections."""

    def __init__(self, session: Session, cache: TaggedPublicCache) -> None:
        self.session = session
        self.cache = cache

    def list_taxonomies(self, kind: TaxonomyKind) -> AdminTaxonomyListResponse:
        records = cast(
            list[TaxonomyRecord],
            self.session.scalars(
                select(self._record_type(kind)).order_by(
                    self._record_type(kind).display_order,
                    self._record_type(kind).title_en,
                    self._record_type(kind).id,
                )
            ).all(),
        )
        return AdminTaxonomyListResponse(items=[_response(record) for record in records])

    def create(
        self, kind: TaxonomyKind, payload: AdminTaxonomyWriteRequest, administrator: AdminUser
    ) -> AdminTaxonomyResponse:
        record_type = self._record_type(kind)
        if (
            self.session.scalar(select(record_type.id).where(record_type.slug == payload.slug))
            is not None
        ):
            raise TaxonomyConflictError()
        self._lock_collection_for_append(kind)
        highest = self.session.scalar(select(func.max(record_type.display_order)))
        record = record_type(
            slug=payload.slug,
            title_en=payload.title_en,
            title_fa=payload.title_fa,
            display_order=int(highest) + 1 if highest is not None else 0,
        )
        self.session.add(record)
        self.session.flush()
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action=f"{kind}.created",
            target_type=kind,
            target_id=record.id,
        )
        self._commit_or_raise()
        return _response(record)

    def update(
        self,
        kind: TaxonomyKind,
        record_id: UUID,
        payload: AdminTaxonomyWriteRequest,
        administrator: AdminUser,
    ) -> AdminTaxonomyResponse:
        record = self._record_or_raise(kind, record_id, lock=True)
        affected_slugs = self._affected_project_slugs(kind, record.id)
        record.slug = payload.slug
        record.title_en = payload.title_en
        record.title_fa = payload.title_fa
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action=f"{kind}.updated",
            target_type=kind,
            target_id=record.id,
        )
        self._commit_or_raise()
        self._invalidate_projects(affected_slugs)
        return _response(record)

    def reorder(
        self,
        kind: TaxonomyKind,
        payload: TaxonomyReorderRequest,
        administrator: AdminUser,
    ) -> AdminTaxonomyListResponse:
        record_type = self._record_type(kind)
        records = cast(
            list[TaxonomyRecord],
            self.session.scalars(
                select(record_type)
                .order_by(record_type.display_order, record_type.title_en, record_type.id)
                .with_for_update()
            ).all(),
        )
        if {record.id for record in records} != set(payload.identifiers):
            raise TaxonomyReorderError(
                "the complete taxonomy collection is required for reordering"
            )
        by_id = {record.id: record for record in records}
        ordered = [by_id[record_id] for record_id in payload.identifiers]
        for position, record in enumerate(ordered, start=1):
            record.display_order = -position
        self.session.flush()
        for position, record in enumerate(ordered):
            record.display_order = position
            record_audit_event(
                self.session,
                actor_id=administrator.id,
                action=f"{kind}.reordered",
                target_type=kind,
                target_id=record.id,
            )
        self._commit_or_raise()
        self._invalidate_projects(self._all_published_project_slugs())
        return self.list_taxonomies(kind)

    def delete(self, kind: TaxonomyKind, record_id: UUID, administrator: AdminUser) -> None:
        record = self._record_or_raise(kind, record_id, lock=True)
        if self._affected_project_slugs(kind, record.id):
            raise TaxonomyInUseError("detach this taxonomy from every project before deleting it")
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action=f"{kind}.deleted",
            target_type=kind,
            target_id=record.id,
        )
        self.session.delete(record)
        self._commit_or_raise()

    @staticmethod
    def _record_type(kind: TaxonomyKind) -> type[Discipline] | type[Typology]:
        return Discipline if kind == "discipline" else Typology

    def _record_or_raise(
        self, kind: TaxonomyKind, record_id: UUID, *, lock: bool
    ) -> TaxonomyRecord:
        record_type = self._record_type(kind)
        statement = select(record_type).where(record_type.id == record_id)
        if lock:
            statement = statement.with_for_update()
        record = cast(TaxonomyRecord | None, self.session.scalar(statement))
        if record is None:
            raise TaxonomyNotFoundError()
        return record

    def _affected_project_slugs(self, kind: TaxonomyKind, record_id: UUID) -> list[str]:
        relationship = Project.disciplines if kind == "discipline" else Project.typologies
        return list(
            self.session.scalars(
                select(Project.slug).where(
                    Project.publication_state == PublicationState.PUBLISHED,
                    Project.published_at.is_not(None),
                    relationship.any(self._record_type(kind).id == record_id),
                )
            ).all()
        )

    def _all_published_project_slugs(self) -> list[str]:
        return list(
            self.session.scalars(
                select(Project.slug).where(
                    Project.publication_state == PublicationState.PUBLISHED,
                    Project.published_at.is_not(None),
                )
            ).all()
        )

    def _commit_or_raise(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise TaxonomyConflictError() from error

    def _invalidate_projects(self, slugs: list[str]) -> None:
        if not slugs:
            return
        tags = {
            "home",
            "home:en",
            "home:fa",
            "project-list",
            "project-list:en",
            "project-list:fa",
        }
        for slug in slugs:
            tags.update({f"project:{slug}", f"project:{slug}:en", f"project:{slug}:fa"})
        self.cache.invalidate(tags)

    def _lock_collection_for_append(self, kind: TaxonomyKind) -> None:
        if self.session.get_bind().dialect.name != "postgresql":
            return
        table = "disciplines" if kind == "discipline" else "typologies"
        # The table name is selected from a closed literal set, never request input.
        self.session.execute(text(f"LOCK TABLE {table} IN SHARE ROW EXCLUSIVE MODE"))


def _response(record: TaxonomyRecord) -> AdminTaxonomyResponse:
    return AdminTaxonomyResponse(
        id=record.id,
        slug=record.slug,
        title_en=record.title_en,
        title_fa=record.title_fa,
        display_order=record.display_order,
    )
