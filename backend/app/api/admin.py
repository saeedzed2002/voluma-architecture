from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from redis import Redis
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.models.admin import AdminUser
from app.models.content import (
    ContactMessage,
    ContactMessageState,
    JournalArticle,
    Project,
    PublicationState,
)
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminLoginRequest,
    AdminSessionResponse,
    AdminUserResponse,
)
from app.services.admin_auth import (
    AdminAuthenticationUnavailableError,
    LoginRateLimiter,
    authenticate_admin,
    create_admin_session,
    delete_admin_session,
    normalize_email,
    validate_csrf,
    validate_mutation_origin,
    verify_password,
)

SESSION_COOKIE_NAME = "voluma_admin_session"
CSRF_HEADER_NAME = "X-VOLUMA-CSRF"

auth_router = APIRouter(prefix="/auth", tags=["admin authentication"])
router = APIRouter(tags=["admin"])

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_session)]


@lru_cache
def _redis_client() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


def get_admin_redis() -> Redis:
    return _redis_client()


RedisDep = Annotated[Redis, Depends(get_admin_redis)]


def _unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="administrator authentication is temporarily unavailable",
    )


def _invalid_credentials() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")


def _authentication_required() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")


def _too_many_attempts() -> HTTPException:
    return HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="try again later")


def _request_ip(request: Request) -> str:
    return request.client.host if request.client is not None else "unknown"


def _set_session_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.admin_session_ttl_seconds,
        path="/",
        samesite="lax",
        secure=settings.admin_session_cookie_secure,
    )


def _require_mutation_origin(request: Request, settings: Settings) -> None:
    if not validate_mutation_origin(request.headers.get("origin"), settings):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid origin")


def require_administrator(
    request: Request,
    session: SessionDep,
    redis: RedisDep,
) -> tuple[AdminUser, str]:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token is None:
        raise _authentication_required()
    try:
        authenticated = authenticate_admin(session, redis, token)
    except AdminAuthenticationUnavailableError as error:
        raise _unavailable() from error
    if authenticated is None:
        raise _authentication_required()
    administrator, _ = authenticated
    return administrator, token


AdministratorDep = Annotated[tuple[AdminUser, str], Depends(require_administrator)]


def require_csrf_mutation(
    request: Request,
    settings: SettingsDep,
    session: SessionDep,
    redis: RedisDep,
) -> tuple[AdminUser, str]:
    _require_mutation_origin(request, settings)
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token is None:
        raise _authentication_required()
    try:
        authenticated = authenticate_admin(session, redis, token)
    except AdminAuthenticationUnavailableError as error:
        raise _unavailable() from error
    if authenticated is None:
        raise _authentication_required()
    administrator, admin_session = authenticated
    if not validate_csrf(request.headers.get(CSRF_HEADER_NAME), admin_session.csrf_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid CSRF token")
    return administrator, token


CsrfAdministratorDep = Annotated[tuple[AdminUser, str], Depends(require_csrf_mutation)]


@auth_router.post("/login", response_model=AdminSessionResponse)
def login(
    payload: AdminLoginRequest,
    request: Request,
    response: Response,
    settings: SettingsDep,
    session: SessionDep,
    redis: RedisDep,
) -> AdminSessionResponse:
    _require_mutation_origin(request, settings)
    email = normalize_email(str(payload.email))
    ip_address = _request_ip(request)
    limiter = LoginRateLimiter(redis)
    try:
        if limiter.is_limited(ip_address=ip_address, email=email):
            raise _too_many_attempts()
        administrator = session.scalar(select(AdminUser).where(AdminUser.email == email))
        if (
            administrator is None
            or not administrator.is_active
            or not verify_password(payload.password, administrator.password_hash)
        ):
            limiter.record_failure(ip_address=ip_address, email=email)
            raise _invalid_credentials()
        limiter.clear(ip_address=ip_address, email=email)
        admin_session = create_admin_session(redis, administrator, settings)
        previous_token = request.cookies.get(SESSION_COOKIE_NAME)
        if previous_token is not None:
            delete_admin_session(redis, previous_token)
    except AdminAuthenticationUnavailableError as error:
        raise _unavailable() from error

    _set_session_cookie(response, admin_session.token, settings)
    return AdminSessionResponse(
        administrator=AdminUserResponse(id=administrator.id, email=administrator.email),
        csrf_token=admin_session.csrf_token,
    )


@auth_router.get("/me", response_model=AdminSessionResponse)
def current_administrator(
    session: SessionDep,
    redis: RedisDep,
    request: Request,
) -> AdminSessionResponse:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token is None:
        raise _authentication_required()
    try:
        authenticated = authenticate_admin(session, redis, token)
    except AdminAuthenticationUnavailableError as error:
        raise _unavailable() from error
    if authenticated is None:
        raise _authentication_required()
    administrator, admin_session = authenticated
    return AdminSessionResponse(
        administrator=AdminUserResponse(id=administrator.id, email=administrator.email),
        csrf_token=admin_session.csrf_token,
    )


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    administrator_and_token: CsrfAdministratorDep,
    response: Response,
    redis: RedisDep,
) -> Response:
    _, token = administrator_and_token
    try:
        delete_admin_session(redis, token)
    except AdminAuthenticationUnavailableError as error:
        raise _unavailable() from error
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/dashboard", response_model=AdminDashboardResponse)
def dashboard(session: SessionDep, _: AdministratorDep) -> AdminDashboardResponse:
    def count_records(model: type[Project] | type[JournalArticle], state: PublicationState) -> int:
        count = session.scalar(
            select(func.count()).select_from(model).where(model.publication_state == state)
        )
        return int(count or 0)

    return AdminDashboardResponse(
        projects={
            "draft": count_records(Project, PublicationState.DRAFT),
            "published": count_records(Project, PublicationState.PUBLISHED),
        },
        journal_articles={
            "draft": count_records(JournalArticle, PublicationState.DRAFT),
            "published": count_records(JournalArticle, PublicationState.PUBLISHED),
        },
        messages={
            state.value: int(
                session.scalar(
                    select(func.count())
                    .select_from(ContactMessage)
                    .where(ContactMessage.state == state)
                )
                or 0
            )
            for state in ContactMessageState
        },
    )
