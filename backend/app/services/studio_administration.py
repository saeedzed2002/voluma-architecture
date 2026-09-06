from __future__ import annotations

from typing import Literal, cast
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.admin import AdminUser
from app.models.content import PublicationState, Recognition, StudioMember
from app.schemas.admin import (
    AdminRecognitionListResponse,
    AdminRecognitionResponse,
    AdminRecognitionWriteRequest,
    AdminStudioMemberListResponse,
    AdminStudioMemberResponse,
    AdminStudioMemberWriteRequest,
    StudioContentReorderRequest,
)
from app.services.admin_auth import record_audit_event
from app.services.public_cache import TaggedPublicCache

StudioContentKind = Literal["people", "recognition"]
StudioContentRecord = StudioMember | Recognition


class StudioAdministrationError(RuntimeError):
    """Base error for the explicit studio-content workflows."""


class StudioContentNotFoundError(StudioAdministrationError):
    pass


class StudioContentConflictError(StudioAdministrationError):
    pass


class StudioContentReorderError(StudioAdministrationError):
    pass


class StudioContentPublishingValidationError(StudioAdministrationError):
    def __init__(self, fields: list[str]) -> None:
        super().__init__("studio content cannot be published")
        self.fields = fields


class StudioAdministrationService:
    """Administrator workflows for people and recognition; media is deferred to Phase 5."""

    def __init__(self, session: Session, cache: TaggedPublicCache) -> None:
        self.session = session
        self.cache = cache

    def list_people(self) -> AdminStudioMemberListResponse:
        records = cast(
            list[StudioMember],
            self.session.scalars(
                select(StudioMember).order_by(
                    StudioMember.display_order, StudioMember.created_at, StudioMember.id
                )
            ).all(),
        )
        return AdminStudioMemberListResponse(items=[_person_response(record) for record in records])

    def create_person(
        self, payload: AdminStudioMemberWriteRequest, administrator: AdminUser
    ) -> AdminStudioMemberResponse:
        self._lock_collection_for_append("people")
        highest = self.session.scalar(select(func.max(StudioMember.display_order)))
        record = StudioMember(display_order=int(highest) + 1 if highest is not None else 0)
        self._apply_person(record, payload)
        self._validate_person_publishable(record)
        self.session.add(record)
        self.session.flush()
        self._audit("people.created", "person", record.id, administrator)
        self._commit_or_raise()
        if record.publication_state == PublicationState.PUBLISHED:
            self._invalidate_studio()
        return _person_response(record)

    def update_person(
        self, record_id: UUID, payload: AdminStudioMemberWriteRequest, administrator: AdminUser
    ) -> AdminStudioMemberResponse:
        record = cast(StudioMember, self._record_or_raise("people", record_id, lock=True))
        was_published = record.publication_state == PublicationState.PUBLISHED
        self._apply_person(record, payload)
        self._validate_person_publishable(record)
        self._audit("people.updated", "person", record.id, administrator)
        self._commit_or_raise()
        if was_published or record.publication_state == PublicationState.PUBLISHED:
            self._invalidate_studio()
        return _person_response(record)

    def list_recognitions(self) -> AdminRecognitionListResponse:
        records = cast(
            list[Recognition],
            self.session.scalars(
                select(Recognition).order_by(
                    Recognition.display_order, Recognition.created_at, Recognition.id
                )
            ).all(),
        )
        return AdminRecognitionListResponse(
            items=[_recognition_response(record) for record in records]
        )

    def create_recognition(
        self, payload: AdminRecognitionWriteRequest, administrator: AdminUser
    ) -> AdminRecognitionResponse:
        self._lock_collection_for_append("recognition")
        highest = self.session.scalar(select(func.max(Recognition.display_order)))
        record = Recognition(display_order=int(highest) + 1 if highest is not None else 0)
        self._apply_recognition(record, payload)
        self._validate_recognition_publishable(record)
        self.session.add(record)
        self.session.flush()
        self._audit("recognition.created", "recognition", record.id, administrator)
        self._commit_or_raise()
        if record.publication_state == PublicationState.PUBLISHED:
            self._invalidate_studio()
        return _recognition_response(record)

    def update_recognition(
        self, record_id: UUID, payload: AdminRecognitionWriteRequest, administrator: AdminUser
    ) -> AdminRecognitionResponse:
        record = cast(Recognition, self._record_or_raise("recognition", record_id, lock=True))
        was_published = record.publication_state == PublicationState.PUBLISHED
        self._apply_recognition(record, payload)
        self._validate_recognition_publishable(record)
        self._audit("recognition.updated", "recognition", record.id, administrator)
        self._commit_or_raise()
        if was_published or record.publication_state == PublicationState.PUBLISHED:
            self._invalidate_studio()
        return _recognition_response(record)

    def reorder(
        self,
        kind: StudioContentKind,
        payload: StudioContentReorderRequest,
        administrator: AdminUser,
    ) -> AdminStudioMemberListResponse | AdminRecognitionListResponse:
        record_type = self._record_type(kind)
        records = cast(
            list[StudioContentRecord],
            self.session.scalars(
                select(record_type)
                .order_by(record_type.display_order, record_type.created_at, record_type.id)
                .with_for_update()
            ).all(),
        )
        if {record.id for record in records} != set(payload.identifiers):
            raise StudioContentReorderError(
                "the complete studio content collection is required for reordering"
            )
        by_id = {record.id: record for record in records}
        ordered = [by_id[record_id] for record_id in payload.identifiers]
        for position, record in enumerate(ordered, start=1):
            record.display_order = -position
        self.session.flush()
        target_type = "person" if kind == "people" else "recognition"
        for position, record in enumerate(ordered):
            record.display_order = position
            self._audit(f"{kind}.reordered", target_type, record.id, administrator)
        self._commit_or_raise()
        if any(record.publication_state == PublicationState.PUBLISHED for record in ordered):
            self._invalidate_studio()
        return self.list_people() if kind == "people" else self.list_recognitions()

    def delete(self, kind: StudioContentKind, record_id: UUID, administrator: AdminUser) -> None:
        record = self._record_or_raise(kind, record_id, lock=True)
        was_published = record.publication_state == PublicationState.PUBLISHED
        self._audit(
            f"{kind}.deleted",
            "person" if kind == "people" else "recognition",
            record.id,
            administrator,
        )
        self.session.delete(record)
        self._commit_or_raise()
        if was_published:
            self._invalidate_studio()

    @staticmethod
    def _apply_person(record: StudioMember, payload: AdminStudioMemberWriteRequest) -> None:
        record.publication_state = payload.publication_state
        record.name = payload.name
        record.role_en = payload.role_en
        record.role_fa = payload.role_fa
        record.biography_en = payload.biography_en
        record.biography_fa = payload.biography_fa

    @staticmethod
    def _apply_recognition(record: Recognition, payload: AdminRecognitionWriteRequest) -> None:
        record.publication_state = payload.publication_state
        record.title_en = payload.title_en
        record.title_fa = payload.title_fa

    @staticmethod
    def _validate_person_publishable(record: StudioMember) -> None:
        if record.publication_state != PublicationState.PUBLISHED:
            return
        fields = [
            field for field in ("name", "role_en", "role_fa") if not getattr(record, field).strip()
        ]
        biography_values = (record.biography_en or "", record.biography_fa or "")
        if any(value.strip() for value in biography_values) and not all(
            value.strip() for value in biography_values
        ):
            fields.extend(("biography_en", "biography_fa"))
        if fields:
            raise StudioContentPublishingValidationError(fields)

    @staticmethod
    def _validate_recognition_publishable(record: Recognition) -> None:
        if record.publication_state != PublicationState.PUBLISHED:
            return
        fields = [field for field in ("title_en", "title_fa") if not getattr(record, field).strip()]
        if fields:
            raise StudioContentPublishingValidationError(fields)

    def _record_or_raise(
        self, kind: StudioContentKind, record_id: UUID, *, lock: bool
    ) -> StudioContentRecord:
        record_type = self._record_type(kind)
        statement = select(record_type).where(record_type.id == record_id)
        if lock:
            statement = statement.with_for_update()
        record = cast(StudioContentRecord | None, self.session.scalar(statement))
        if record is None:
            raise StudioContentNotFoundError()
        return record

    @staticmethod
    def _record_type(kind: StudioContentKind) -> type[StudioMember] | type[Recognition]:
        return StudioMember if kind == "people" else Recognition

    def _lock_collection_for_append(self, kind: StudioContentKind) -> None:
        if self.session.get_bind().dialect.name != "postgresql":
            return
        table = "studio_members" if kind == "people" else "recognitions"
        self.session.execute(text(f"LOCK TABLE {table} IN SHARE ROW EXCLUSIVE MODE"))

    def _audit(
        self, action: str, target_type: str, target_id: UUID, administrator: AdminUser
    ) -> None:
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
        )

    def _commit_or_raise(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise StudioContentConflictError() from error

    def _invalidate_studio(self) -> None:
        self.cache.invalidate({"home", "home:en", "home:fa", "studio", "studio:en", "studio:fa"})


def _person_response(record: StudioMember) -> AdminStudioMemberResponse:
    return AdminStudioMemberResponse(
        id=record.id,
        publication_state=record.publication_state,
        display_order=record.display_order,
        name=record.name,
        role_en=record.role_en,
        role_fa=record.role_fa,
        biography_en=record.biography_en,
        biography_fa=record.biography_fa,
        updated_at=record.updated_at,
    )


def _recognition_response(record: Recognition) -> AdminRecognitionResponse:
    return AdminRecognitionResponse(
        id=record.id,
        publication_state=record.publication_state,
        display_order=record.display_order,
        title_en=record.title_en,
        title_fa=record.title_fa,
        updated_at=record.updated_at,
    )
