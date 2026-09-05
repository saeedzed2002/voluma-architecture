# Phase 2 visual review evidence

This directory contains reproducible browser captures for the `Phase 2` public
route checkpoint. The matrix includes each newly completed route across English
and Persian, desktop and mobile, and explicit light and dark themes. It also
captures the localized `404` state.

From `frontend/`, run the local production frontend and then run:

```powershell
pnpm visual:capture:phase2
```

The capture script uses the installed stable Chrome channel because the
Playwright browser CDN returned an explicit location-based `HTTP 403` on the
review host. Browser interaction and accessibility coverage are maintained in
the Playwright end-to-end suite.
