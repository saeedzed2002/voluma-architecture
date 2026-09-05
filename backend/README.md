# VOLUMA backend

This directory contains the Phase 3 FastAPI public-read foundation: typed configuration,
SQLAlchemy models, Alembic migrations, published-only response schemas, Redis tagged
cache, health endpoints, and explicit development-only fixture seeding.

Apply migrations before starting the API. Do not call `metadata.create_all` in an
application or deployment path.

```powershell
uv sync --frozen --all-groups
uv run alembic upgrade head
uv run python -m app.fixtures.seed
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The fixture command is idempotent and must only be used for local development. It does
not run at application startup. Administrative content management, contact intake,
media processing, worker behavior, and production Compose/Nginx deployment remain in
their documented later phases.
