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

Phase 0 is establishing reproducible repository controls and exact dependency
manifests. Application features have not yet been implemented.

## Planned layout

```text
frontend/  Next.js public site and administrative interface
backend/   FastAPI API, migrations, services, and Celery tasks
nginx/     reverse-proxy and public derivative-media configuration
infra/     Compose, scripts, and backup operations
docs/      product source of truth, ADRs, and runbooks
```

## Bootstrap baseline

The project requires the exact Node.js, pnpm, Python, uv, package, and container
versions in the specification. Do not substitute a nearby runtime version when
generating lockfiles or release images.

```powershell
corepack pnpm --dir frontend install --frozen-lockfile
uv --directory backend sync --frozen --all-groups
```

Copy `.env.example` to `.env` only for local development and replace every placeholder
with local protected values. Never commit a populated `.env` file.

## License status

The codebase is private and unlicensed for redistribution until the owner explicitly
adopts a license. See ADR `0003`.
