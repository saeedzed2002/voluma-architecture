from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  # Register mapped content models before test DDL.
from app.db.base import Base
from app.fixtures.development import seed_development_content


@pytest.fixture
def session() -> Generator[Session]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, expire_on_commit=False)
    with sessions.begin() as database_session:
        seed_development_content(database_session)
    with sessions() as database_session:
        yield database_session
    Base.metadata.drop_all(engine)
    engine.dispose()
