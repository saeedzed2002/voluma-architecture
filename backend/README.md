# VOLUMA backend

This directory contains the Phases 3 and 4 FastAPI foundation: typed configuration,
SQLAlchemy models, Alembic migrations, published-only response schemas, Redis tagged
cache, health endpoints, authenticated administration, contact intake, audit events,
and explicit development-only fixture seeding.

Apply migrations before starting the API. Do not call `metadata.create_all` in an
application or deployment path.

```powershell
uv sync --frozen --all-groups
uv run alembic upgrade head
uv run python -m app.fixtures.seed
uv run python -m app.commands.provision_initial_administrator
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The fixture command is idempotent and must only be used for local development. It does
not run at application startup. The provisioning command requires protected
`VOLUMA_INITIAL_ADMIN_EMAIL` and `VOLUMA_INITIAL_ADMIN_PASSWORD` values. Media processing,
worker behavior, and production Compose/Nginx deployment remain in their documented later
phases.
