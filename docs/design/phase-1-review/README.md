# Phase 1 visual review evidence

This directory contains reproducible browser captures for the Phase 1 visual
checkpoint. The matrix covers English and Persian, LTR and RTL, desktop and
mobile viewports, and both explicit themes. It also includes representative
Projects archive and Project detail openings plus two full-page Home captures.

Run the local frontend first, then regenerate from `frontend/` with:

```powershell
pnpm visual:capture
```

The capture script uses the locally installed stable Chrome channel because the
Playwright browser CDN returned an explicit location-based HTTP 403 on the review
host. Browser behavior and accessibility are separately covered by the Playwright
test suite.
