from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from redis import Redis
from sqlalchemy.orm import Session

from app.api.admin import get_admin_redis
from app.db.session import get_session
from app.schemas.contact import ContactSubmissionRequest, ContactSubmissionResponse
from app.services.contact_messages import (
    ContactMessageService,
    ContactRateLimitUnavailableError,
    ContactSubmissionRateLimiter,
    completed_too_soon,
)

router = APIRouter(tags=["contact"])
SessionDep = Annotated[Session, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_admin_redis)]


def _client_address(request: Request) -> str:
    """Use the edge-sanitized forwarding header when the request passed through Next/Nginx."""

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first_address = forwarded_for.split(",", maxsplit=1)[0].strip()
        if first_address:
            return first_address
    return request.client.host if request.client is not None else "unknown"


@router.post("", response_model=ContactSubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_contact_message(
    payload: ContactSubmissionRequest,
    request: Request,
    session: SessionDep,
    redis: RedisDep,
) -> ContactSubmissionResponse:
    if payload.website:
        return ContactSubmissionResponse()
    if completed_too_soon(payload.started_at):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="form was submitted too quickly",
        )
    try:
        allowed = ContactSubmissionRateLimiter(redis).consume(_client_address(request))
    except ContactRateLimitUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="contact submission is temporarily unavailable",
        ) from error
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="try again later")
    ContactMessageService(session).create(payload)
    return ContactSubmissionResponse()
