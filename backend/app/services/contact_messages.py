from __future__ import annotations

import hashlib
import time
from datetime import UTC, datetime
from typing import Literal, cast
from uuid import UUID

from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.admin import AdminUser
from app.models.content import ContactMessage, ContactMessageState
from app.schemas.contact import (
    AdminContactMessageListResponse,
    AdminContactMessageResponse,
    ContactSubmissionRequest,
)
from app.services.admin_auth import normalize_email, record_audit_event

CONTACT_IP_RATE_PREFIX = "voluma:rate:contact:ip:"
CONTACT_IP_LIMIT = 5
CONTACT_IP_PERIOD_SECONDS = 60 * 60
MINIMUM_COMPLETION_MILLISECONDS = 3_000


class ContactMessageNotFoundError(RuntimeError):
    pass


class ContactRateLimitUnavailableError(RuntimeError):
    pass


class ContactSubmissionRateLimiter:
    """Bound accepted submissions per client address without retaining the address itself."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def consume(self, client_address: str) -> bool:
        key = f"{CONTACT_IP_RATE_PREFIX}{_fingerprint(client_address)}"
        try:
            count = cast(int, self.redis.incr(key))
            if count == 1:
                self.redis.expire(key, CONTACT_IP_PERIOD_SECONDS)
        except RedisError as error:
            raise ContactRateLimitUnavailableError(
                "contact submission is temporarily unavailable"
            ) from error
        return count <= CONTACT_IP_LIMIT


class ContactMessageService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, payload: ContactSubmissionRequest) -> ContactMessage:
        message = ContactMessage(
            name=payload.name,
            email=normalize_email(str(payload.email)),
            phone=payload.phone,
            company=payload.company,
            project_type=payload.project_type,
            body=payload.message,
            source_locale=payload.source_locale,
            state=ContactMessageState.NEW,
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def list(
        self,
        *,
        state: ContactMessageState | None,
        limit: int,
        offset: int,
    ) -> AdminContactMessageListResponse:
        statement = select(ContactMessage)
        count_statement = select(func.count()).select_from(ContactMessage)
        if state is not None:
            statement = statement.where(ContactMessage.state == state)
            count_statement = count_statement.where(ContactMessage.state == state)
        total = int(self.session.scalar(count_statement) or 0)
        messages = self.session.scalars(
            statement.order_by(ContactMessage.created_at.desc(), ContactMessage.id)
            .offset(offset)
            .limit(limit)
        ).all()
        return AdminContactMessageListResponse(
            items=[contact_message_response(message) for message in messages], total=total
        )

    def get(self, message_id: UUID, *, lock: bool = False) -> ContactMessage:
        statement = select(ContactMessage).where(ContactMessage.id == message_id)
        if lock:
            statement = statement.with_for_update()
        message = self.session.scalar(statement)
        if message is None:
            raise ContactMessageNotFoundError()
        return message

    def update_state(
        self,
        message_id: UUID,
        state: ContactMessageState,
        administrator: AdminUser,
    ) -> AdminContactMessageResponse:
        message = self.get(message_id, lock=True)
        now = datetime.now(UTC)
        message.state = state
        if state == ContactMessageState.NEW:
            message.read_at = None
            message.archived_at = None
        elif state == ContactMessageState.READ:
            message.read_at = message.read_at or now
            message.archived_at = None
        else:
            message.archived_at = now
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="contact_message.state_updated",
            target_type="contact_message",
            target_id=message.id,
        )
        self.session.commit()
        self.session.refresh(message)
        return contact_message_response(message)

    def delete(self, message_id: UUID, administrator: AdminUser) -> None:
        message = self.get(message_id, lock=True)
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="contact_message.deleted",
            target_type="contact_message",
            target_id=message.id,
        )
        self.session.delete(message)
        self.session.commit()


def completed_too_soon(started_at: int) -> bool:
    return int(time.time() * 1_000) - started_at < MINIMUM_COMPLETION_MILLISECONDS


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def contact_message_response(message: ContactMessage) -> AdminContactMessageResponse:
    return AdminContactMessageResponse(
        id=message.id,
        name=message.name,
        email=message.email,
        phone=message.phone,
        company=message.company,
        project_type=message.project_type,
        body=message.body,
        source_locale=cast(Literal["en", "fa"], message.source_locale),
        state=message.state,
        read_at=message.read_at,
        archived_at=message.archived_at,
        created_at=message.created_at,
        updated_at=message.updated_at,
    )
