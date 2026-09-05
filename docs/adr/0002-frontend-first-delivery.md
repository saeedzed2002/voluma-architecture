# ADR 0002: Deliver and approve the public visual system before backend integration

## Status

Accepted — 2026-09-05

## Context

VOLUMA's primary value is a bilingual editorial architecture experience. Implementing
content services before validating the responsive visual product risks turning the
website into a technically complete but generic portfolio.

## Decision

Complete static mock-data Home, Projects archive, and Project detail first. Verify
English/Persian, desktop/mobile, light/dark, keyboard behavior, and design direction
before FastAPI, PostgreSQL, Redis, admin, or media integration begins.

## Consequences

Frontend data contracts must be deliberate and fixtures clearly development-only. The
backend later conforms to the already-approved public presentation rather than driving
it. Browser and visual evidence are required before Phase 3 begins.
