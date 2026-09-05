# ADR 0003: Keep the repository private and unlicensed pending owner decision

## Status

Accepted for initial development — 2026-09-05

## Context

The product specification requires a license decision but provides no license or
redistribution intent.

## Decision

Set package metadata to `UNLICENSED` and make no public license grant. The repository
is private and all rights remain with the owner until they explicitly choose a license
or commercial distribution terms.

## Consequences

No third party may infer permission to copy, redistribute, or reuse the project. A
future licensing decision must update this ADR, package metadata, and any release
documentation together.
