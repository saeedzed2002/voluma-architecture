# VOLUMA — Architecture & Design

VOLUMA is a premium bilingual architecture-studio website, editorial project archive,
journal, and lightweight content-management system. It is designed as a single
application with a Next.js public/admin frontend and a FastAPI content/media backend.

The complete source of truth is
[`docs/product/VOLUMA_PROJECT_SPECIFICATION_FINAL.md`](docs/product/VOLUMA_PROJECT_SPECIFICATION_FINAL.md).
It defines scope, design direction, architecture, security constraints, exact version
baseline, phases, validation, and the Definition of Done. This repository deliberately
does not duplicate that specification.

## Current phase

Phase 3 delivers the public content foundation. The approved public experience now
renders from purpose-built, published-only FastAPI response schemas with `no-store`
Next.js fetches. It includes the initial Alembic migration, PostgreSQL archive indexes,
Redis tagged response cache, health/readiness endpoints, and explicit development-only
content fixtures. Phase 4 is next: authenticated administrative CMS workflows.

## Planned layout

```text
frontend/  Next.js public site and administrative interface
backend/   FastAPI API, migrations, services, and Celery tasks
nginx/     reverse-proxy and public derivative-media configuration
infra/     Compose, scripts, and backup operations
docs/      product source of truth, ADRs, and runbooks
```

## Run the current application locally

Phase 3 uses two temporary local containers for PostgreSQL and Redis. This is a
development-only bootstrap, not the production Compose deployment planned for Phase 6.
Choose a local password rather than committing one, then start the dependencies:

```powershell
docker run --rm -d --name voluma-phase3-postgres -e POSTGRES_DB=voluma -e POSTGRES_USER=voluma -e POSTGRES_PASSWORD=<local-password> -p 127.0.0.1:54329:5432 postgres:18.6
docker run --rm -d --name voluma-phase3-redis -p 127.0.0.1:56379:6379 redis:8.10.1 redis-server --save "" --appendonly no
```

Run the migration, load representative development-only content, and start the API:

```powershell
cd D:\Project\VOLUMA\backend
$env:DATABASE_URL = "postgresql+psycopg://voluma:<local-password>@127.0.0.1:54329/voluma"
$env:REDIS_URL = "redis://127.0.0.1:56379/0"
uv run alembic upgrade head
uv run python -m app.fixtures.seed
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, install the exact Node.js `24.20.0` runtime and run the frontend.
Corepack reads the locked `pnpm@11.25.0` package-manager version from
`frontend/package.json`.

```powershell
cd D:\Project\VOLUMA\frontend
corepack enable
corepack pnpm install --frozen-lockfile
$env:VOLUMA_API_BASE_URL = "http://127.0.0.1:8000"
corepack pnpm dev
```

Open `http://localhost:3000/en` for English or `http://localhost:3000/fa` for Persian.
The public routes are locale-prefixed:

- `/en`, `/fa`
- `/en/projects`, `/fa/projects`
- `/en/projects/{slug}`, `/fa/projects/{slug}`
- `/en/expertise`, `/en/process`, `/en/studio`, `/en/journal`, `/en/contact`
- `/en/privacy`, `/en/search`, and their Persian equivalents

The seeded names, text, dates, locations, and media are representative development
fixtures, not final client material. Never use the local commands or credentials above
as a deployment procedure.

## Frontend validation

Run these from `frontend/`:

```powershell
corepack pnpm lint
corepack pnpm typecheck
corepack pnpm test
corepack pnpm build
corepack pnpm test:e2e
```

Run the locked backend checks from the repository root:

```powershell
uv --directory backend sync --frozen --all-groups
uv --directory backend run ruff format --check .
uv --directory backend run ruff check .
uv --directory backend run mypy app
uv --directory backend run pytest
```

The browser suite currently uses the locally installed stable Chrome channel. To
regenerate the visual-review evidence while the dev server is running:

```powershell
corepack pnpm visual:capture
```

The complete source of truth remains the product specification. Do not substitute a
nearby runtime or dependency version when regenerating lockfiles or release images.
Copy `.env.example` to `.env` only for protected local configuration, replace every
placeholder with protected local values, and never commit a populated `.env`.

## License status

The codebase is private and unlicensed for redistribution until the owner explicitly
adopts a license. See ADR `0003`.
