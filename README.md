# VOLUMA — Architecture & Design

VOLUMA is a premium bilingual architecture-studio website, editorial project archive,
journal, and lightweight content-management system. It is designed as a single
application with a Next.js public/admin frontend and a FastAPI content/media backend.

[![Continuous integration](https://github.com/saeedzed2002/voluma-architecture/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/saeedzed2002/voluma-architecture/actions/workflows/ci.yml?query=branch%3Amain)

The complete source of truth is
[`docs/product/VOLUMA_PROJECT_SPECIFICATION_FINAL.md`](docs/product/VOLUMA_PROJECT_SPECIFICATION_FINAL.md).
It defines scope, design direction, architecture, security constraints, exact version
baseline, phases, validation, and the Definition of Done. This repository deliberately
does not duplicate that specification.

## Project status

VOLUMA is complete as a source-code portfolio. It is not deployed, and this repository
does not claim a public production deployment, clean-host deployment exercise, or
operational backup/restore exercise.

The current `main` branch passed the complete [GitHub Actions CI run](https://github.com/saeedzed2002/voluma-architecture/actions/runs/34763817085) for commit
[`dc30d55`](https://github.com/saeedzed2002/voluma-architecture/commit/dc30d556dfb79fe4b5c756374d764bffbd46d6ef). The observed gates include repository secret
scanning, locked frontend and backend validation, migrations and seed commands, browser
and worker integration checks, an isolated Compose build and HTTPS smoke test, and
high/critical Trivy scans of the API, frontend, and Nginx images.

## Implemented scope

Phases 1 through 6 are implemented. The approved public experience renders from
purpose-built, published-only FastAPI response schemas with `no-store` Next.js fetches.
The administrator workspace provides protected bilingual content, ordering, publishing,
message triage, singleton site-settings workflows, and a managed media library with audit
events and Redis tagged cache invalidation. Phase 5 adds validated JPEG/PNG/WebP uploads,
durable processing states, Celery derivative generation, versioned public media paths, and
project gallery selection. Phase 6 now supplies production Dockerfiles, immutable base-image
pins, private Compose networking, TLS Nginx routing, nonce-based CSP, runbooks, and release
automation. The completed CI run provides container-build, image-scan, browser, worker, and
Compose-smoke evidence. Deployment and restore remain deliberately unrun because this is a
source-code portfolio, not a live service.

Journal article covers are managed-media references. An administrator may also add a managed
single-image block directly within an article by dropping a `JPEG`, `PNG`, or `WebP` file into
the article editor. The upload is processed asynchronously; publication requires the image to be
`ready` with English and Persian alt text. The API refuses unavailable or unsafe references, and
media referenced by a journal cover or article block cannot be deleted until it is removed.

## Planned layout

```text
frontend/  Next.js public site and administrative interface
backend/   FastAPI API, migrations, services, and Celery tasks
infra/nginx/ Nginx image, reverse proxy, and public derivative-media configuration
infra/     Compose, scripts, and backup operations
docs/      product source of truth, ADRs, and runbooks
```

## Run the current application locally

Use the development Compose file for PostgreSQL and Redis. It binds their ports only to
`127.0.0.1`; it is deliberately separate from the production stack. Copy `.env.example`
to a protected local `.env`, replace every password placeholder consistently in the URLs,
then start the dependencies:

```powershell
Copy-Item .env.example .env
docker compose --env-file .env -f docker-compose.dev.yml up --detach --wait
```

Run the migration, load representative development-only content, and start the API:

```powershell
cd D:\Project\VOLUMA\backend
$env:DATABASE_URL = "postgresql+psycopg://voluma:<local-password>@127.0.0.1:54329/voluma"
$env:REDIS_URL = "redis://:<local-redis-password>@127.0.0.1:56379/0"
$env:CELERY_BROKER_URL = "redis://:<local-redis-password>@127.0.0.1:56379/1"
$env:VOLUMA_MEDIA_ROOT = "D:\Project\VOLUMA\.voluma-media"
uv run alembic upgrade head
uv run python -m app.fixtures.seed
uv run python -m app.commands.provision_initial_administrator
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Before running the provisioning command, set `VOLUMA_INITIAL_ADMIN_EMAIL` and
`VOLUMA_INITIAL_ADMIN_PASSWORD` in the current terminal or a protected local `.env`.
The command is idempotent and no administrator password is committed to this repository.

In a third terminal, use the same broker and media-root values to run the worker. The
API and worker must share this directory; it contains private originals and staging
files as well as the Nginx-readable `public/` derivative subtree.

```powershell
cd D:\Project\VOLUMA\backend
$env:DATABASE_URL = "postgresql+psycopg://voluma:<local-password>@127.0.0.1:54329/voluma"
$env:REDIS_URL = "redis://:<local-redis-password>@127.0.0.1:56379/0"
$env:CELERY_BROKER_URL = "redis://:<local-redis-password>@127.0.0.1:56379/1"
$env:VOLUMA_MEDIA_ROOT = "D:\Project\VOLUMA\.voluma-media"
uv run celery -A app.worker:celery_app worker --pool=solo --loglevel=INFO
```

`--pool=solo` is the compatible local Windows worker mode. The production worker
process and shared persistent volume are defined by the Phase 6 Compose release.

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

The seeded names, text, dates, locations, and media paths are representative development
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

## Production operations

Use only the documented procedures in
[`docs/runbooks/production-deployment.md`](docs/runbooks/production-deployment.md),
[`docs/runbooks/backup-and-restore.md`](docs/runbooks/backup-and-restore.md), and
[`docs/runbooks/monitoring-and-performance.md`](docs/runbooks/monitoring-and-performance.md).
Production uses valid TLS, exposes only Nginx ports `80` and `443`, and never receives
development fixtures or source bind mounts. The base-image provenance is recorded in
[`docs/runbooks/image-provenance.md`](docs/runbooks/image-provenance.md).

## License

This repository is licensed under the [MIT License](LICENSE). The MIT License applies
to the original project work; third-party assets and fonts remain subject to their own
licenses, including the font-license notices under
[`frontend/src/app/fonts/licenses/`](frontend/src/app/fonts/licenses/).
