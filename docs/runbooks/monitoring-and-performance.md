# Monitoring and performance checklist

## Continuous operational checks

- Nginx: certificate expiry, HTTP-to-HTTPS redirects, `5xx` rate, upstream failures,
  response latency, and public derivative cache headers.
- API: `/api/healthz` and `/api/readyz`, error rate, request latency, contact and
  administrator rate-limit responses, and absence of leaked error details.
- Worker: Celery process availability, failed/retried media jobs, queue age, and media
  processing duration. Celery results remain disabled; use logs and durable media state
  rather than a result backend.
- Storage: free capacity of `postgres_data`, `redis_data`, and `media_data`; media
  volume write permissions for API/worker; Nginx read-only media access.
- Backup: most recent encrypted off-host artifact, checksum verification, retention,
  and the date/result of the latest restore exercise.

Never put passwords, session cookies, contact text, uploaded file contents, or full
authorization headers in dashboards or alert messages.

## Release performance budget

For each release candidate, run Lighthouse or Web Vitals measurement on a
production-like HTTPS build with mobile throttling and one representative published
project. Record the tool/version, URL, date, network profile, and raw report outside
the repository's public output.

Verify all of the following rather than promising a score without evidence:

- The LCP image is a prioritized responsive AVIF/WebP derivative, not an original.
- Offscreen project and journal images are lazy-loaded.
- Every public media URL has a versioned fingerprint and immutable cache header.
- No original-media request appears in the browser network log.
- The initial public route does not load administrator/editor-only code.
- Server-rendered public data avoids client-side API waterfalls.

Treat a regression in LCP, JavaScript payload, render-blocking work, or image bytes as
a release issue until it is explained and accepted by the project owner.
