from __future__ import annotations

from typing import Literal, cast
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.admin import AdminUser
from app.models.content import Expertise, ProcessStep, PublicationState
from app.schemas.admin import (
    AdminBilingualContentListResponse,
    AdminBilingualContentResponse,
    AdminBilingualContentWriteRequest,
    BilingualContentReorderRequest,
)
from app.services.admin_auth import record_audit_event
from app.services.public_cache import TaggedPublicCache

EditorialContentKind = Literal["expertise", "process"]
EditorialContentRecord = Expertise | ProcessStep


class EditorialContentAdministrationError(RuntimeError):
    """Base error for ordered bilingual editorial content workflows."""


class EditorialContentNotFoundError(EditorialContentAdministrationError):
    pass


class EditorialContentConflictError(EditorialContentAdministrationError):
    pass


class EditorialContentReorderError(EditorialContentAdministrationError):
    pass


class EditorialContentPublishingValidationError(EditorialContentAdministrationError):
    def __init__(self, fields: list[str]) -> None:
        super().__init__("content cannot be published")
        self.fields = fields


class EditorialContentAdministrationService:
    """Explicit administrator workflows for expertise and process steps."""

    def __init__(self, session: Session, cache: TaggedPublicCache) -> None:
        self.session = session
        self.cache = cache

    def list_entries(self, kind: EditorialContentKind) -> AdminBilingualContentListResponse:
        record_type = self._record_type(kind)
        records = cast(
            list[EditorialContentRecord],
            self.session.scalars(
                select(record_type).order_by(
                    record_type.display_order, record_type.created_at, record_type.id
                )
            ).all(),
        )
        return AdminBilingualContentListResponse(items=[_response(record) for record in records])

    def create(
        self,
        kind: EditorialContentKind,
        payload: AdminBilingualContentWriteRequest,
        administrator: AdminUser,
    ) -> AdminBilingualContentResponse:
        record_type = self._record_type(kind)
        self._lock_collection_for_append(kind)
        highest = self.session.scalar(select(func.max(record_type.display_order)))
        record = record_type(display_order=int(highest) + 1 if highest is not None else 0)
        self._apply_fields(record, payload)
        self._validate_publishable(record)
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
        if record.publication_state == PublicationState.PUBLISHED:
            self._invalidate(kind)
        return _response(record)

    def update(
        self,
        kind: EditorialContentKind,
        record_id: UUID,
        payload: AdminBilingualContentWriteRequest,
        administrator: AdminUser,
    ) -> AdminBilingualContentResponse:
        record = self._record_or_raise(kind, record_id, lock=True)
        was_published = record.publication_state == PublicationState.PUBLISHED
        self._apply_fields(record, payload)
        self._validate_publishable(record)
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action=f"{kind}.updated",
            target_type=kind,
            target_id=record.id,
        )
        self._commit_or_raise()
        if was_published or record.publication_state == PublicationState.PUBLISHED:
            self._invalidate(kind)
        return _response(record)

    def reorder(
        self,
        kind: EditorialContentKind,
        payload: BilingualContentReorderRequest,
        administrator: AdminUser,
    ) -> AdminBilingualContentListResponse:
        record_type = self._record_type(kind)
        records = cast(
            list[EditorialContentRecord],
            self.session.scalars(
                select(record_type)
                .order_by(record_type.display_order, record_type.created_at, record_type.id)
                .with_for_update()
            ).all(),
        )
        if {record.id for record in records} != set(payload.identifiers):
            raise EditorialContentReorderError(
                "the complete editorial content collection is required for reordering"
            )
        by_id = {record.id: record for record in records}
        ordered = [by_id[record_id] for record_id in payload.identifiers]

        # Preserve the unique persistent ordering constraint during the swap.
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
        if any(record.publication_state == PublicationState.PUBLISHED for record in ordered):
            self._invalidate(kind)
        return self.list_entries(kind)

    def delete(self, kind: EditorialContentKind, record_id: UUID, administrator: AdminUser) -> None:
        record = self._record_or_raise(kind, record_id, lock=True)
        was_published = record.publication_state == PublicationState.PUBLISHED
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action=f"{kind}.deleted",
            target_type=kind,
            target_id=record.id,
        )
        self.session.delete(record)
        self._commit_or_raise()
        if was_published:
            self._invalidate(kind)

    @staticmethod
    def _record_type(kind: EditorialContentKind) -> type[Expertise] | type[ProcessStep]:
        return Expertise if kind == "expertise" else ProcessStep

    def _record_or_raise(
        self, kind: EditorialContentKind, record_id: UUID, *, lock: bool
    ) -> EditorialContentRecord:
        record_type = self._record_type(kind)
        statement = select(record_type).where(record_type.id == record_id)
        if lock:
            statement = statement.with_for_update()
        record = cast(EditorialContentRecord | None, self.session.scalar(statement))
        if record is None:
            raise EditorialContentNotFoundError()
        return record

    @staticmethod
    def _apply_fields(
        record: EditorialContentRecord, payload: AdminBilingualContentWriteRequest
    ) -> None:
        record.publication_state = payload.publication_state
        record.title_en = payload.title_en
        record.title_fa = payload.title_fa
        record.summary_en = payload.summary_en
        record.summary_fa = payload.summary_fa

    @staticmethod
    def _validate_publishable(record: EditorialContentRecord) -> None:
        if record.publication_state != PublicationState.PUBLISHED:
            return
        fields = (
            "title_en",
            "title_fa",
            "summary_en",
            "summary_fa",
        )
        missing = [field for field in fields if not getattr(record, field).strip()]
        if missing:
            raise EditorialContentPublishingValidationError(missing)

    def _commit_or_raise(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise EditorialContentConflictError() from error

    def _invalidate(self, kind: EditorialContentKind) -> None:
        self.cache.invalidate(
            {
                "home",
                "home:en",
                "home:fa",
                kind,
                f"{kind}:en",
                f"{kind}:fa",
            }
        )

    def _lock_collection_for_append(self, kind: EditorialContentKind) -> None:
        if self.session.get_bind().dialect.name != "postgresql":
            return
        table = "expertise" if kind == "expertise" else "process_steps"
        # The table name is selected from a closed literal set, never request input.
        self.session.execute(text(f"LOCK TABLE {table} IN SHARE ROW EXCLUSIVE MODE"))


def _response(record: EditorialContentRecord) -> AdminBilingualContentResponse:
    return AdminBilingualContentResponse(
        id=record.id,
        publication_state=record.publication_state,
        display_order=record.display_order,
        title_en=record.title_en,
        title_fa=record.title_fa,
        summary_en=record.summary_en,
        summary_fa=record.summary_fa,
        updated_at=record.updated_at,
    )
