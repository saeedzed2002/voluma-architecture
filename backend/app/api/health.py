from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_session

router = APIRouter(tags=["health"])

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDependency = Annotated[Session, Depends(get_session)]


@router.get("/healthz", include_in_schema=False)
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", include_in_schema=False)
def readyz(settings: SettingsDep, session: SessionDependency) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
        Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1).ping()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="not ready"
        ) from error

    return {"status": "ready"}
