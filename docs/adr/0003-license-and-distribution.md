# ADR 0003: Publish the repository under the MIT License

## Status

Accepted — 2026-09-15. This supersedes the initial private and unlicensed
development decision recorded for this ADR.

## Context

During initial development, the project had no selected distribution license and no
public redistribution intent. The repository is now public, and the owner has chosen
an open-source license for the original project work.

## Decision

Publish the repository under the MIT License. The root [`LICENSE`](../../LICENSE)
file is the canonical license grant, and the frontend and backend package metadata
must identify the project as `MIT`.

The frontend `private` package setting remains a registry-publication safeguard; it
does not describe the visibility or license of this GitHub repository.

The MIT License applies only to original project work. Third-party assets, including
the bundled Vazirmatn and Instrument Sans fonts, retain their existing licenses and
notices under `frontend/src/app/fonts/licenses/`. Their terms continue to govern those
files.

## Consequences

Recipients may use, copy, modify, distribute, sublicense, and sell the original
project work under the MIT License terms. Future contributions and release
documentation must preserve the root license notice and must not remove or replace
third-party license notices.
