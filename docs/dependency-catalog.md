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

- Packages: `@parcel/watcher` and `@swc/core`, both transitive dependencies of
  `next-intl@4.14.2` in the initial frontend graph.
- Decision: allow only these two packages to execute dependency lifecycle build scripts
  through the `allowBuilds` map in `frontend/pnpm-workspace.yaml`.
- Reason: pnpm 11 blocks undeclared dependency build scripts in CI. These packages need
  their install/postinstall steps to prepare their platform binaries.
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
