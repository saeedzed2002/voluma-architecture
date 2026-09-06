from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.admin import AdministratorDep, CsrfAdministratorDep
from app.db.session import get_session
from app.models.content import ContactMessageState
from app.schemas.contact import (
    AdminContactMessageListResponse,
    AdminContactMessageResponse,
    AdminContactMessageStateRequest,
)
from app.services.contact_messages import (
    ContactMessageNotFoundError,
    ContactMessageService,
    contact_message_response,
)

router = APIRouter(prefix="/messages", tags=["admin messages"])
SessionDep = Annotated[Session, Depends(get_session)]
PageLimit = Annotated[int, Query(ge=1, le=100)]
PageOffset = Annotated[int, Query(ge=0)]


@router.get("", response_model=AdminContactMessageListResponse)
def list_messages(
    _administrator: AdministratorDep,
    session: SessionDep,
    state: ContactMessageState | None = None,
    limit: PageLimit = 50,
    offset: PageOffset = 0,
) -> AdminContactMessageListResponse:
    return ContactMessageService(session).list(state=state, limit=limit, offset=offset)


@router.get("/{message_id}", response_model=AdminContactMessageResponse)
def get_message(
    message_id: UUID,
    _administrator: AdministratorDep,
    session: SessionDep,
) -> AdminContactMessageResponse:
    try:
        return contact_message_response(ContactMessageService(session).get(message_id))
    except ContactMessageNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="message not found"
        ) from error


@router.patch("/{message_id}", response_model=AdminContactMessageResponse)
def update_message_state(
    message_id: UUID,
    payload: AdminContactMessageStateRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
) -> AdminContactMessageResponse:
    try:
        return ContactMessageService(session).update_state(
            message_id, payload.state, authenticated[0]
        )
    except ContactMessageNotFoundError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="message not found"
        ) from error


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: UUID,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
) -> None:
    try:
        ContactMessageService(session).delete(message_id, authenticated[0])
    except ContactMessageNotFoundError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="message not found"
        ) from error
