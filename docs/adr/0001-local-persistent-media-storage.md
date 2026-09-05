# ADR 0001: Use a persistent local media volume for release 1

## Status

Accepted — 2026-09-05

## Context

VOLUMA launches on one server with a portfolio-scale media library. It needs private
original uploads, public immutable derivatives, and a durable worker hand-off without
introducing object-storage infrastructure prematurely.

## Decision

Use one persistent Docker media volume. The API and Celery worker mount it read/write;
Nginx mounts it read-only and exposes only `public/{media-id}/{version}/`. Originals
and staging files have no public URL. Media identity is UUID/ULID-based. PostgreSQL
stores metadata and processing state; Redis never stores image bytes.

## Consequences

PostgreSQL and the entire media volume must be backed up and restored together. This
design is intentionally limited to a single server. A storage interface and migration
to S3-compatible storage are deferred until measured horizontal-scaling need exists.
