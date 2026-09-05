# VOLUMA engineering instructions

The canonical product and architecture specification is
[`docs/product/VOLUMA_PROJECT_SPECIFICATION_FINAL.md`](docs/product/VOLUMA_PROJECT_SPECIFICATION_FINAL.md).
Read it before changing product scope, dependencies, architecture, deployment, security, or tests.

## Non-negotiable boundaries

- Build in the documented phases. Do not start backend/content integration until the
  static Home, Projects archive, and Project detail pass the documented EN/FA,
  desktop/mobile, and light/dark visual review.
- Use only the approved single-application stack: Next.js/React/TypeScript/Tailwind/
  Motion/next-intl; FastAPI/PostgreSQL/SQLAlchemy/Alembic/Redis/Celery/Pillow; Docker
  Compose and Nginx.
- Do not introduce microservices, Kafka, RabbitMQ, MinIO, S3, Elasticsearch,
  Kubernetes, Helm, CQRS, a repository wrapper, generic event bus, Three.js, GSAP,
  Redux, Zustand, Bootstrap, Material UI, or Ant Design.
- Never expose drafts, administrator data, originals, sessions, secrets, or unsafe
  content through public routes, metadata, caches, logs, or screenshots.
- Public content is bilingual (`en`, `fa`), locale-prefixed, and genuinely LTR/RTL.
  Use CSS logical properties and do not mirror imagery for RTL.
- Store original and derived media on the shared persistent media volume. Redis never
  stores image bytes and Celery has no result backend.
- Use Alembic for every persisted schema change. Do not use `metadata.create_all` as
  a production migration mechanism.
- Direct dependencies are exact-pinned. Any approved dependency change needs a
  documented reason, an updated lockfile, tests, and an entry in
  `docs/dependency-catalog.md`.

## Validation commands

Run only the checks relevant to the completed phase, and report their actual result:

```powershell
corepack pnpm --dir frontend install --frozen-lockfile
corepack pnpm --dir frontend lint
corepack pnpm --dir frontend typecheck
corepack pnpm --dir frontend test
uv --directory backend sync --frozen --all-groups
uv --directory backend run ruff format --check .
uv --directory backend run ruff check .
uv --directory backend run mypy app
uv --directory backend run pytest
git diff --check
```

Container, migration, worker, Nginx, browser, visual, accessibility, and CI evidence
are distinct from local static checks. Do not claim any unrun category as passing.

## Delivery discipline

Preserve unrelated user changes. Do not commit, push, deploy, rotate real secrets, or
run destructive database/media commands without explicit user authorization. Before a
commit or push, verify the remote and that the local identity is
`saeedzed2002 <saeedzed2002@gmail.com>`.
