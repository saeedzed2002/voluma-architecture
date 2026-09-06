from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast
from uuid import UUID, uuid4

from email_validator import EmailNotValidError, validate_email
from pwdlib import PasswordHash
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.admin import AdminUser, AuditEvent

SESSION_PREFIX = "voluma:session:"
LOGIN_IP_RATE_PREFIX = "voluma:rate:login:ip:"
LOGIN_ACCOUNT_RATE_PREFIX = "voluma:rate:login:account:"
LOGIN_IP_LIMIT = 5
LOGIN_IP_PERIOD_SECONDS = 15 * 60
LOGIN_ACCOUNT_LIMIT = 10
LOGIN_ACCOUNT_PERIOD_SECONDS = 60 * 60

_password_hash = PasswordHash.recommended()


class AdminAuthenticationUnavailableError(RuntimeError):
    """Raised when Redis is unavailable for an authentication decision."""


class InitialAdministratorConfigurationError(RuntimeError):
    """Raised when initial administrator deployment variables are unavailable or unsafe."""


@dataclass(frozen=True)
class AdminSession:
    admin_id: UUID
    csrf_token: str
    token: str


def normalize_email(email: str) -> str:
    return validate_email(email, check_deliverability=False).normalized.lower()


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _session_key(token: str) -> str:
    return f"{SESSION_PREFIX}{_fingerprint(token)}"


def _rate_key(prefix: str, value: str) -> str:
    return f"{prefix}{_fingerprint(value)}"


def _redis_call[T](operation: Callable[[], T]) -> T:
    try:
        return operation()
    except RedisError as error:
        raise AdminAuthenticationUnavailableError(
            "administrator authentication is unavailable"
        ) from error


class LoginRateLimiter:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def is_limited(self, *, ip_address: str, email: str) -> bool:
        ip_count = cast(
            str | None,
            _redis_call(lambda: self.redis.get(_rate_key(LOGIN_IP_RATE_PREFIX, ip_address))),
        )
        account_count = cast(
            str | None,
            _redis_call(lambda: self.redis.get(_rate_key(LOGIN_ACCOUNT_RATE_PREFIX, email))),
        )
        return (
            int(ip_count or 0) >= LOGIN_IP_LIMIT or int(account_count or 0) >= LOGIN_ACCOUNT_LIMIT
        )

    def record_failure(self, *, ip_address: str, email: str) -> None:
        self._increment(_rate_key(LOGIN_IP_RATE_PREFIX, ip_address), LOGIN_IP_PERIOD_SECONDS)
        self._increment(_rate_key(LOGIN_ACCOUNT_RATE_PREFIX, email), LOGIN_ACCOUNT_PERIOD_SECONDS)

    def clear(self, *, ip_address: str, email: str) -> None:
        _redis_call(
            lambda: self.redis.delete(
                _rate_key(LOGIN_IP_RATE_PREFIX, ip_address),
                _rate_key(LOGIN_ACCOUNT_RATE_PREFIX, email),
            )
        )

    def _increment(self, key: str, ttl_seconds: int) -> None:
        count = cast(int, _redis_call(lambda: self.redis.incr(key)))
        if count == 1:
            _redis_call(lambda: self.redis.expire(key, ttl_seconds))


def create_admin_session(redis: Redis, admin: AdminUser, settings: Settings) -> AdminSession:
    token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)
    payload = json.dumps({"admin_id": str(admin.id), "csrf_token": csrf_token})
    _redis_call(
        lambda: redis_set(redis, _session_key(token), payload, settings.admin_session_ttl_seconds)
    )
    return AdminSession(admin_id=admin.id, csrf_token=csrf_token, token=token)


def redis_set(redis: Redis, key: str, value: str, ttl_seconds: int) -> object:
    return redis.set(key, value, ex=ttl_seconds)


def delete_admin_session(redis: Redis, token: str) -> None:
    _redis_call(lambda: redis.delete(_session_key(token)))


def get_admin_session(redis: Redis, token: str) -> AdminSession | None:
    payload = cast(str | None, _redis_call(lambda: redis.get(_session_key(token))))
    if payload is None:
        return None
    try:
        decoded = json.loads(payload)
        admin_id = UUID(decoded["admin_id"])
        csrf_token = decoded["csrf_token"]
    except KeyError, TypeError, ValueError, json.JSONDecodeError:
        delete_admin_session(redis, token)
        return None
    if not isinstance(csrf_token, str):
        delete_admin_session(redis, token)
        return None
    return AdminSession(admin_id=admin_id, csrf_token=csrf_token, token=token)


def authenticate_admin(
    session: Session, redis: Redis, token: str
) -> tuple[AdminUser, AdminSession] | None:
    admin_session = get_admin_session(redis, token)
    if admin_session is None:
        return None
    admin = session.scalar(select(AdminUser).where(AdminUser.id == admin_session.admin_id))
    if admin is None or not admin.is_active:
        delete_admin_session(redis, token)
        return None
    return admin, admin_session


def validate_mutation_origin(origin: str | None, settings: Settings) -> bool:
    return origin is not None and hmac.compare_digest(origin, settings.public_origin)


def validate_csrf(submitted_token: str | None, expected_token: str) -> bool:
    return submitted_token is not None and hmac.compare_digest(submitted_token, expected_token)


def record_audit_event(
    session: Session,
    *,
    actor_id: UUID,
    action: str,
    target_type: str,
    target_id: UUID,
    correlation_id: UUID | None = None,
) -> AuditEvent:
    event = AuditEvent(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        correlation_id=correlation_id or uuid4(),
    )
    session.add(event)
    return event


def provision_initial_administrator(session: Session, settings: Settings) -> AdminUser:
    email = settings.initial_admin_email
    password = settings.initial_admin_password
    if email is None or password is None or len(password) < 12:
        raise InitialAdministratorConfigurationError(
            "initial administrator deployment configuration is incomplete"
        )
    try:
        normalized_email = normalize_email(email)
    except EmailNotValidError as error:
        raise InitialAdministratorConfigurationError(
            "initial administrator email is invalid"
        ) from error
    existing = session.scalar(select(AdminUser).where(AdminUser.email == normalized_email))
    if existing is not None:
        return existing
    administrator = AdminUser(
        email=normalized_email, password_hash=hash_password(password), is_active=True
    )
    session.add(administrator)
    session.flush()
    record_audit_event(
        session,
        actor_id=administrator.id,
        action="administrator.provisioned",
        target_type="admin_user",
        target_id=administrator.id,
    )
    return administrator
