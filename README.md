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

Phase 1 delivers the bilingual static public foundation: local fonts, design tokens,
light/dark/system themes, locale routing with real LTR/RTL behavior, the responsive
public shell, Home, Projects archive, and Project detail routes, plus representative
fixture media. Phase 2 is next and will complete the remaining public routes,
interactions, SEO surface, and browser-QA scope.

## Planned layout

```text
frontend/  Next.js public site and administrative interface
backend/   FastAPI API, migrations, services, and Celery tasks
nginx/     reverse-proxy and public derivative-media configuration
infra/     Compose, scripts, and backup operations
docs/      product source of truth, ADRs, and runbooks
```

## Run the current website locally

Install the exact Node.js `24.20.0` runtime, then run the following commands in
PowerShell. Corepack reads the locked `pnpm@11.25.0` package-manager version from
`frontend/package.json`.

```powershell
cd D:\Project\VOLUMA\frontend
corepack enable
corepack pnpm install --frozen-lockfile
corepack pnpm dev
```

Open `http://localhost:3000/en` for English or `http://localhost:3000/fa` for Persian.
The current Phase 1 routes are:

- `/en`, `/fa`
- `/en/projects`, `/fa/projects`
- `/en/projects/courtyard-house`, `/fa/projects/courtyard-house`

Other representative project slugs are generated from the fixture catalog. Phase 1
is static and does not require the backend, PostgreSQL, Redis, or environment secrets
to render these routes. Content and media are explicitly development fixtures, not
final client material.

## Frontend validation

Run these from `frontend/`:

```powershell
corepack pnpm lint
corepack pnpm typecheck
corepack pnpm test
corepack pnpm build
corepack pnpm test:e2e
```

The browser suite currently uses the locally installed stable Chrome channel. To
regenerate the Phase 1 visual-review evidence while the dev server is running:

```powershell
corepack pnpm visual:capture
```

The complete source of truth remains the product specification. Do not substitute a
nearby runtime or dependency version when regenerating lockfiles or release images.
Copy `.env.example` to `.env` only when a later phase requires local services, replace
every placeholder with protected local values, and never commit a populated `.env`.

## License status

The codebase is private and unlicensed for redistribution until the owner explicitly
adopts a license. See ADR `0003`.
