# Dependency catalog

The direct dependency baseline is canonical in
[`VOLUMA_PROJECT_SPECIFICATION_FINAL.md`](product/VOLUMA_PROJECT_SPECIFICATION_FINAL.md),
section 9. This file is an append-only decision log; it intentionally does not repeat
version tables that would drift from the specification and lockfiles.

## Baseline

The initial locked frontend and backend direct dependencies use the specification's
2026-09-05 baseline, including the compatibility correction below.

## 2026-09-05 — Redis Python client compatibility correction

- Owner: project owner, authorized during Phase 0 remediation.
- Change: `redis[hiredis]` from `8.1.0` to exact version `6.4.0`.
- Reason: `celery[redis]==5.6.3` enables `kombu[redis]`; Kombu 5.6.1 requires the
  Python Redis client to be at least 4.5.2 and below 6.5, excluding 4.5.5 and 5.0.2.
  The original direct pin made the backend dependency graph unsatisfiable.
- Scope: Python client only. The Redis server image remains `redis:8.10.1`.
- Files: `backend/pyproject.toml`, `backend/uv.lock`, and the canonical product
  specification.
- Evidence: official PyPI metadata plus `uv 0.12.9` resolution under Python 3.14.7.
  Frozen sync and container evidence are recorded with the Phase 0 validation result.
- Rollback: restore a newer client only together with a verified Celery/Kombu upgrade
  whose published constraints and integration tests support it.

## 2026-09-05 — Approved frontend dependency build scripts

- Packages: `@parcel/watcher`, `@swc/core`, and `unrs-resolver`. The first two are
  transitive dependencies of `next-intl@4.14.2` in the initial frontend graph;
  `unrs-resolver@1.12.2` enters through `eslint-config-next@16.3.4` and its official
  `eslint-import-resolver-typescript` dependency.
- Decision: allow only these three packages to execute dependency lifecycle build
  scripts through the `allowBuilds` map in `frontend/pnpm-workspace.yaml`.
- Reason: pnpm 11 blocks undeclared dependency build scripts in CI. These packages need
  their install/postinstall steps to prepare or select their platform binaries. The
  reviewed `unrs-resolver` postinstall delegates only to `napi-postinstall` with the
  package's published N-API target metadata.
- Security boundary: every other present or future dependency build script remains
  unapproved and causes the frozen CI install to fail pending explicit review.
- Evidence: `pnpm why`, local lifecycle rebuild, frozen install, and GitHub Actions run.

## Required entry for a future dependency change

- Date and owner
- Package and exact target version
- Concrete feature, security, or compatibility reason
- Changelog/advisory review evidence
- Manifest and lockfile paths changed
- Test, container-build, and rollback evidence

## 2026-09-05 — TypeScript 7 compiler with TypeScript 6 tooling API

- Owner: project owner, authorized as part of Phase 1 implementation.
- Packages: `@typescript/native` aliased to `typescript==7.0.2`, and `typescript`
  aliased to `@typescript/typescript6==6.0.2`.
- Reason: TypeScript 7.0 keeps the required native compiler and command-line interface,
  while the current `typescript-eslint` dependency in Next.js' official lint preset
  still consumes the TypeScript 6 JavaScript API. TypeScript 7 intentionally does not
  expose that legacy API.
- Evidence: Microsoft's TypeScript 7 release guidance explicitly documents this
  side-by-side alias arrangement. Both package versions were verified against their
  official npm metadata on 2026-09-05.
- Files: `frontend/package.json`, `frontend/pnpm-lock.yaml`, and this catalog.
- Validation and rollback: the TypeScript 7 native typecheck, ESLint, Vitest, and the
  Next.js production build must all pass. Remove the compatibility alias after the
  lint toolchain publishes native TypeScript 7 API support and the full validation
  suite stays green.

## 2026-09-05 — Phase 1 compiler and framework lint support

- Owner: project owner, authorized as part of Phase 1 implementation.
- Packages: `@types/react==19.2.18`, `@types/react-dom==19.2.7`,
  `@types/node==24.6.1`, and `eslint-config-next==16.3.4`.
- Reason: the canonical frontend baseline includes TypeScript and ESLint but did not
  list the declaration packages or Next.js' official lint preset required to typecheck
  and lint a real App Router application. The Node declarations stay on the project's
  locked Node 24 runtime major; the lint preset exactly matches Next.js 16.3.4.
- Evidence: the official npm package pages and Next.js ESLint documentation were
  reviewed on 2026-09-05. No runtime library or alternate framework was introduced.
- Files: `frontend/package.json`, `frontend/pnpm-lock.yaml`, and
  `frontend/eslint.config.mjs`.
- Validation and rollback: frozen install, lint, TypeScript, Vitest, Next.js build,
  and browser checks must pass. Roll back the four direct dependencies together only
  if the compiler/lint pipeline is replaced with an approved equivalent.

## 2026-09-05 — ESLint 10 rule-API compatibility

- Owner: project owner, authorized as part of Phase 1 implementation.
- Package: `@eslint/compat==2.1.0`.
- Reason: `eslint-config-next==16.3.4` currently includes React, JSX accessibility,
  and import plugins whose published rules use the pre-ESLint-10 context API. With
  the specification's exact `eslint==10.9.1` baseline, linting failed while loading
  `react/display-name` because `contextOrFilename.getFilename` was unavailable.
- Decision: wrap the two imported Next.js flat configurations with ESLint's official
  `fixupConfigRules()` compatibility utility. The three exact transitive plugin/ESLint
  pairs are recorded in pnpm's scoped `peerDependencyRules.allowedVersions` after the
  compatibility run passed. Rules remain enabled; no diagnostics are disabled or
  downgraded, and future plugin versions receive no automatic exception.
- Evidence: the ESLint compatibility documentation and official npm metadata were
  reviewed on 2026-09-05. `@eslint/compat==2.1.0` declares support for ESLint 10 and
  the locked Node 24 runtime.
- Files: `frontend/package.json`, `frontend/pnpm-lock.yaml`,
  `frontend/eslint.config.mjs`, and this catalog.
- Validation and rollback: the frozen install and ESLint 10 run must pass. Remove the
  compatibility layer after all plugins in the matching Next.js preset publish native
  ESLint 10 rule-API support and the full lint suite remains green.
