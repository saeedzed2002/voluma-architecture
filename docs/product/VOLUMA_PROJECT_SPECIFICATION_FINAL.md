# VOLUMA — Architecture & Design

## Project specification and delivery baseline

| Field | Decision |
| --- | --- |
| Brand | VOLUMA |
| Presentation name | VOLUMA — Architecture & Design |
| Repository | voluma-architecture |
| Product | A premium bilingual architecture-studio website, editorial project archive, journal, and lightweight content-management system |
| Primary languages | English and Persian |
| Verification snapshot | 5 September 2026 |
| Delivery model | Frontend-first, then content model and backend, then deployment hardening |
| Specification status | Source of truth for the initial release |

## 1. Purpose, boundaries, and decisions already made

VOLUMA must feel like a serious architecture studio, not a generic portfolio template or a SaaS dashboard. Its visual language is minimal architectural editorial design: immersive photography, deliberate whitespace, strong typography, asymmetrical composition, restrained motion, and a real dark/light system.

The website must be usable for a solo architect at launch and must also support a small studio without a redesign. Content, branding, contacts, project order, and featured content are managed in the administrative application; they are not hard-coded.

This is deliberately a single, well-structured application. Do not introduce microservices, Kafka, RabbitMQ, Elasticsearch, MinIO, S3, Kubernetes, Helm, CQRS, a repository pattern, or a generic event bus in the initial release. Those additions would add operational cost without solving a present problem.

The approved stack is:

- Next.js, React, TypeScript, Tailwind CSS, Motion, and next-intl for the frontend.
- FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis, Celery, and Pillow for the backend and media pipeline.
- A persistent local media volume for master assets and public image derivatives.
- Nginx for TLS termination, reverse proxying, direct media delivery, compression, and immutable media caching.
- Docker Compose for development and single-server production deployment.

The following boundaries are mandatory for release 1:

- There are no public user accounts, registrations, comments, favorites, client portal, newsletter delivery system, careers workflow, map view, or general-purpose page builder.
- There is exactly one administrative role: Administrator. The data model may support more than one administrator account, but there is no roles/permissions matrix.
- Email notifications for contact messages are deferred. Messages are stored in PostgreSQL and handled in the admin application.
- There is no public access to originals. A lightbox uses the largest public derivative, never the uploaded source file.
- Redis does not store image bytes. It is for public API cache, rate-limit/session state, and Celery broker transport. Celery result storage is disabled; durable media processing state lives in PostgreSQL.
- All public content is published only when both English and Persian required fields are complete. Drafts are never exposed by a public API.

## 2. Product experience and art direction

### 2.1 Design principles

The visual reference is the quality bar of established architecture practices, not a copy of any one site. VOLUMA takes these useful patterns:

- Project archives should feel like curated editorial catalogues, with search, useful filters, an intentional grid/list switch, and clean metadata.
- Project detail pages should tell an architectural story through media, text, facts, and pacing instead of dumping a gallery.
- Studio, process, expertise, and journal content make the website credible beyond a set of project thumbnails.

The website must implement:

- Full-bleed and large-format photography where the content earns it.
- Editorial, sometimes asymmetrical layouts; not repeated 3x3 cards.
- Clear reading hierarchy, generous rhythm, and intentional image ratios.
- A strong wordmark treatment: VOLUMA, optionally paired with ARCHITECTURE & DESIGN.
- Local font files: Instrument Sans for Latin content and Vazirmatn for Persian content, loaded through next/font/local with WOFF2 files and font-display: swap.
- Design tokens for color, type scale, spacing, radii, z-index, and motion. Light and dark themes are token sets, not an afterthought that replaces white with black.

### 2.2 Motion policy

Motion must clarify hierarchy or feedback. Approved uses are hero entrance, menu state, project hover, subtle scroll reveal, gallery transition, theme transition, and restrained page transitions.

Motion must not use scroll hijacking, parallax that causes readability problems, auto-playing sound, decorative particles, WebGL, Three.js, or GSAP. Motion must respect prefers-reduced-motion: reduce. In that mode, essential state changes remain visible but nonessential animation is removed.

### 2.3 Responsive rules

Design and test these four combinations before any visual milestone is accepted:

1. English desktop.
2. English mobile.
3. Persian desktop.
4. Persian mobile.

Use CSS logical properties such as margin-inline, padding-inline, inset-inline, and text-align: start. The Persian experience must set dir=rtl at the document level and mirror navigation direction, alignment, breadcrumb direction, controls, and arrows where appropriate. Images themselves must never be visually mirrored merely because the page is RTL.

The primary target widths are 360 px, 768 px, 1024 px, 1440 px, and 1920 px. Touch controls have a minimum 44 by 44 CSS pixel target. Desktop hover interactions must have a clear focus and touch equivalent.

## 3. Public information architecture

All public routes are locale-prefixed. The only supported locale prefixes are /en and /fa. An unprefixed request redirects to the configured default locale without losing a valid path or query string.

| Route | Purpose |
| --- | --- |
| /en and /fa | Home |
| /{locale}/projects | Project archive |
| /{locale}/projects/{slug} | Project detail |
| /{locale}/expertise | Disciplines and expertise |
| /{locale}/process | Studio process |
| /{locale}/studio | Studio, people, recognition, collaborators |
| /{locale}/journal | Journal archive |
| /{locale}/journal/{slug} | Journal article |
| /{locale}/contact | Contact |
| /{locale}/privacy | Localized privacy notice for contact-form data |
| /{locale}/search?q= | Search results or search overlay destination |
| localized not-found | Branded 404 |

The project slug is an immutable ASCII identifier. It is shared between language routes, for example /en/projects/forest-house and /fa/projects/forest-house. Changing an existing published slug creates a permanent redirect from the old route. Do not use Persian slugs for the initial release.

### 3.1 Home

The home page includes:

1. Accessible global navigation, locale control, and theme control.
2. A cinematic hero selected in site settings. It may use one image, a restrained image sequence, or an optional muted video with poster image. Video is optional and must have a mobile image fallback.
3. A concise studio statement.
4. Selected projects in an editorial arrangement.
5. Expertise or disciplines teaser.
6. A featured project story.
7. An architectural philosophy or process teaser.
8. Studio teaser and selected recognition/statistics only when real data exists.
9. Latest journal items.
10. Contact call to action and footer.

The hero image is the likely LCP resource. It must receive priority/preload treatment, explicit dimensions, and a responsive derivative. It must not be lazy-loaded.

### 3.2 Projects archive

The archive supports:

- Search across published project title, subtitle, location, and selected metadata.
- Filters: discipline, typology, project status, location, and year.
- Grid and list view. View preference may be retained locally, but it must not alter shared URLs unexpectedly.
- URL-addressable filter state. A filtered result can be shared and restored.
- A bounded, accessible pagination or Load more mechanism. Do not render an unlimited list in one response.
- Editorial project presentation: image, title, discipline, typology when useful, location, and year.

There is no map view in release 1. PostgreSQL search is sufficient for the expected content volume; do not deploy Elasticsearch.

### 3.3 Project detail

Every project detail page contains, where data exists:

- Project number or archive marker, title, subtitle, discipline, typology, location, completion year, and status.
- Large hero image.
- Short introduction and structured facts: client, location, year, status, area, discipline, typology, architect, collaborators, and completion date.
- Ordered editorial blocks, including text, quote, single image, full-width image, two-image pair, and gallery reference.
- Image caption and credit when supplied.
- Fullscreen gallery with keyboard navigation, visible counter, captions, previous/next controls, Escape to close, focus management, and mobile swipe.
- Related projects based on shared discipline or typology.
- Previous and next project navigation.

Facts with no value are omitted. Do not show empty labels or fake data.

### 3.4 Expertise, process, and studio

Expertise contains ordered bilingual entries for architecture, interior design, landscape, renovation, concept design, visualization, or equivalent real capabilities. It uses images and prose, not generic icon cards.

Process contains a fixed sequence of content-managed steps such as Discover, Research, Concept, Design, Develop, and Deliver. Each step has bilingual title, short explanation, optional image, and display order.

Studio contains the introduction, philosophy, people, selected numbers, recognitions, collaborators/clients when approved, studio gallery, and contact link. People are managed entries with portrait, name, bilingual role, optional biography, and order. Recognition is simple ordered content, not a separate awards product.

### 3.5 Journal and search

Journal contains published articles categorized by Architecture, Design, Process, Studio, Ideas, or configured equivalent categories. An article has title, excerpt, cover, publish date, estimated reading time, structured blocks, related articles, SEO fields, and both language versions.

Search is limited to published projects and journal articles. It returns only safe public summary data. It is not an administrative search or a site-wide crawler.

### 3.6 Contact

The contact form collects name, email, optional phone, optional company, optional project type, and message. It stores a message in PostgreSQL with New, Read, or Archived state.

The form must have server-side validation, a honeypot field, a minimum-completion-time check, Redis-backed rate limiting, and an accessible success/error result. It must not log message bodies. A CAPTCHA provider is not part of release 1, but the form boundary must allow one later.

### 3.7 Privacy

Because the contact form collects personal information, VOLUMA includes a localized privacy page at `/{locale}/privacy`.

The page explains, in plain language:
- what contact information is collected,
- why it is collected,
- where/how it is stored at a high level,
- the intended retention/deletion process,
- and how to contact the site owner about that data.

The English and Persian privacy content is managed through Site Settings. The initial text is operational placeholder content only; a commercial deployment must replace it with jurisdiction-appropriate wording supplied or approved by the site owner. Do not present generated placeholder legal text as legal advice.

## 4. Content model and administrative application

The admin frontend lives at /admin and is intentionally visually distinct from the public website. It is a clean operational interface, not a third-party admin skin. The public locale middleware must exclude /admin, /api, and /_next.

### 4.1 Admin routes

| Route | Capability |
| --- | --- |
| /admin/login | Administrator sign-in |
| /admin | Dashboard: published/draft counts, recent content/messages, processing/failed images |
| /admin/projects | Project list, filters, create, ordering |
| /admin/projects/new | Project creation |
| /admin/projects/{id}/edit | Tabbed project editor |
| /admin/disciplines | Discipline CRUD and ordering |
| /admin/typologies | Typology CRUD and ordering |
| /admin/expertise | Expertise CRUD and ordering |
| /admin/process | Process-step CRUD and ordering |
| /admin/journal | Journal article and category management |
| /admin/people | Studio member management |
| /admin/recognition | Recognition management |
| /admin/media | Media library and processing state |
| /admin/messages | Contact message triage |
| /admin/settings | Branding, contact, social, home, privacy content, appearance, and default SEO |

The dashboard must not contain decorative charts without a real question to answer.

### 4.2 Project editor

The project editor has these explicit tabs:

- General: bilingual title/subtitle, immutable slug, disciplines, typologies, location, year, status, featured state, and display order.
- Content: bilingual introduction and structured editorial blocks.
- Details: client, area, architect, collaborators, completion date, and other optional project facts.
- Gallery: upload, status, cover selection, alt text, caption, credit, reorder, remove, and retry processing.
- SEO: bilingual SEO title, meta description, and selected Open Graph image.
- Publishing: draft/published state and publication date.

The editorial block system is deliberate scope control. It supports validated text, quote, single-image, full-width image, paired-image, and gallery blocks. It does not accept arbitrary HTML, raw scriptable content, or a generic page-builder schema. Render blocks as React components; do not use dangerouslySetInnerHTML.

### 4.3 Data entities

Use PostgreSQL migrations to create at least these entities:

| Entity | Essential responsibility |
| --- | --- |
| admin_users | Administrator email, Argon2id password hash, active state, timestamps |
| site_settings | Single site record with bilingual studio/home/privacy content, contacts, social links, defaults, logo/favicons |
| projects | Bilingual core project data, slug, publication, selected/featured state, facts, SEO |
| disciplines and typologies | Ordered bilingual taxonomy |
| project_disciplines and project_typologies | Project taxonomy join tables |
| project_blocks | Ordered, schema-validated bilingual editorial blocks |
| media_assets | Original metadata, derivative version, dimensions, processing state, alt/caption/credit, usage data |
| project_media | Ordered project-media relationship and cover designation |
| expertise | Ordered bilingual expertise entries |
| process_steps | Ordered bilingual process entries |
| studio_members | Ordered people entries |
| recognitions | Ordered bilingual recognition entries |
| journal_categories | Ordered bilingual categories |
| journal_articles | Bilingual articles, publication, SEO, cover, reading time |
| article_blocks | Ordered, schema-validated article blocks |
| contact_messages | Validated inquiries, state, timestamps, minimal request metadata |
| audit_events | Administrator mutations: actor, action, target, timestamp, correlation ID; never secret values or full contact body |

Use created_at and updated_at timestamps consistently. Use UUID or ULID primary identifiers for public-facing/media identity; do not expose sequential database IDs in public media URLs.

### 4.4 Publishing and order rules

- Save Draft never makes a resource public.
- Publish validates both localized title/content requirements, slug uniqueness, alt text on public images, and required SEO fallback fields.
- Unpublish immediately removes public API access, canonical/sitemap inclusion, and archive appearance.
- Reordering is transactional and avoids duplicate positions.
- A content mutation invalidates the affected Redis cache tags only after its database transaction commits.
- An administrator cannot delete a media asset while it is referenced. The UI must show its usage and require detachment or replacement first.

## 5. System architecture

    Browser
      |
      v
    Nginx
      |-- /              -> Next.js frontend
      |-- /api           -> FastAPI
      |-- /media         -> immutable public derivatives on the media volume
      |
      v
    FastAPI ----- PostgreSQL
      |
      |----- Redis: public API cache, sessions/rate limits, Celery broker
      |
      v
    Celery worker ----- same persistent media volume

Only Nginx exposes host ports in production. Next.js, FastAPI, PostgreSQL, Redis, and Celery use the internal Compose network. PostgreSQL and Redis must never receive a public port mapping in production.

### 5.1 Frontend

Use the Next.js App Router and server components by default. Use client components only for interaction that requires the browser: navigation/menu, theme choice, locale UI, filters, gallery, drag-and-drop admin interactions, upload progress, and motion.

Public pages are server-rendered for crawlability and request their data from FastAPI through the internal network or same-origin API path. In release 1, use no-store at the Next.js data-fetch layer and let FastAPI's explicit Redis tag cache control freshness. This avoids contradictory stale windows between Next data cache and backend cache. Add Next on-demand revalidation only in a later, separately tested optimization.

The theme choice has system, light, and dark modes. It is persisted locally and applied before paint to prevent a theme flash. System remains the initial default unless site settings intentionally select another default.

### 5.2 FastAPI

FastAPI owns:

- Pydantic request/response validation.
- Public read APIs.
- Administrative sessions and CRUD APIs.
- Contact form intake.
- Media upload validation, initial write, metadata creation, task enqueueing, and retry/deletion commands.
- Redis cache invalidation.
- Health/readiness endpoints.
- OpenAPI in development only.

Use SQLAlchemy 2.x directly with clear application services. Do not invent a repository abstraction around normal ORM queries. Use Alembic for every schema change; never use metadata.create_all as a production migration mechanism.

Public API endpoints return purpose-built response schemas and only published content. Admin endpoints require an authenticated session and CSRF protection. Endpoint paths may be grouped as:

- /api/v1/public/site, home, projects, projects/{slug}, expertise, process, studio, journal, journal/{slug}, and search.
- /api/v1/contact.
- /api/v1/admin/auth/login, logout, me.
- /api/v1/admin/projects, taxonomies, expertise, process, journal, people, recognitions, media, messages, settings, and audit events.
- /api/healthz and internal /api/readyz.

### 5.3 PostgreSQL and Redis

Use PostgreSQL for durable business data and media metadata. Add indexes for published archive queries, slug uniqueness, ordered relations, publication date, taxonomy joins, contact triage state, and case-insensitive search fields. For the expected archive size, a bounded ILIKE search over indexed normalized title/location fields is adequate. Revisit PostgreSQL full-text search only after measured need.

Redis responsibilities are deliberately narrow:

- Redis logical DB 0: `voluma:cache:*` for public JSON response cache, `voluma:session:*` for hashed opaque administrator sessions, and `voluma:rate:*` for rate-limit counters.
- Redis logical DB 1: Celery broker transport.
- No Celery result backend is configured; `task_ignore_result = True` (or equivalent) is required for normal media tasks.
- Durable media processing state is stored only in PostgreSQL (`PROCESSING`, `READY`, `FAILED`, `DELETED`).

Logical Redis databases prevent key collisions, not memory contention. Keep cache cardinality bounded, give cache/session/rate-limit keys explicit TTLs, configure a production memory policy intentionally, and monitor Redis memory so cache growth cannot destabilize sessions or queued work.

Never use FLUSHALL or `KEYS` in production request paths, and never issue an unprefixed destructive cache command. A Redis restart may discard cache and sessions; administrators can sign in again. Celery tasks must remain idempotent and the media reconciliation command must recover assets left in PROCESSING.

### 5.4 Public response cache

Cache public API payloads in Redis by content/version tag and locale. Typical tags include site, home, project-list, project:{slug}, expertise, process, studio, journal-list, and article:{slug}.

On an admin write:

1. Validate and write the database transaction.
2. Commit.
3. Invalidate only the related cache tags.
4. Return the result.

If invalidation fails after a successful commit, record a structured error and retry/clear only the known tag family. Do not return success before attempting invalidation. Search responses are not cached initially.

## 6. Media storage and asynchronous image pipeline

### 6.1 Storage contract

Store originals and derivatives on the persistent shared Docker media volume, never in PostgreSQL or Redis. This is the right initial production choice for one server and a portfolio-scale media library.

Suggested physical layout:

    /var/lib/voluma-media/
      originals/{media-uuid}/source.{extension}
      staging/{task-or-media-uuid}/
      public/{media-uuid}/{derivative-version}/
        w320.webp
        w640.avif
        w640.webp
        w1024.avif
        w1024.webp
        w1600.avif
        w1600.webp
        w2400.avif
        w2400.webp
        placeholder.webp
        og.webp

Nginx exposes only the public subtree at /media/. The originals and staging paths are never mapped to a web URL. Media identity is UUID/ULID-based, not project-slug-based, so a project rename never requires moving files.

Every public derivative URL includes the immutable derivative version/fingerprint. Nginx may therefore send:

    Cache-Control: public, max-age=31536000, immutable

Do not overwrite a publicly referenced derivative in place. Generate a new derivative version, update the database reference atomically, and allow normal cache expiry for old URLs.

### 6.2 Upload validation

The upload endpoint accepts only JPEG, PNG, and WebP in release 1. It rejects TIFF, SVG, HEIC/HEIF, animated images, arbitrary binary data, and unsupported formats.

Mandatory checks before permanent write:

- Maximum upload size: 50 MiB.
- Maximum dimension: 12,000 pixels on either axis.
- Maximum total pixels: 100,000,000.
- Extension is not trusted. Detect content and decode it with the image library.
- Treat decompression-bomb warnings/errors as validation failures.
- Correct orientation before derivative generation.
- Strip EXIF and other metadata from public derivatives, including location metadata. Preserve only audited minimal source metadata in the database if needed.
- Store the source under generated identity, not the user-supplied filename.

The application-level maximum source image size is 50 MiB. Configure Nginx `client_max_body_size` to approximately 60 MiB so a valid 50 MiB file plus multipart/form-data overhead can reach FastAPI; FastAPI remains authoritative for the 50 MiB file limit. The admin UI makes the distinction clear: upload progress measures browser-to-server transfer; processing progress measures Celery work after the server responds.

### 6.3 Celery workflow

After FastAPI validates and writes an original:

1. Create the `media_assets` row with status `PROCESSING`, record source metadata, and commit that durable state.
2. Queue an idempotent Celery task successfully.
3. Only after the broker accepts the task, return HTTP 202 with media identity and status.
4. If enqueueing fails, mark the asset `FAILED` with a sanitized queueing error (while preserving the original for retry) and return an appropriate 5xx response rather than falsely returning 202.
5. The worker decodes safely, applies orientation, derives dimensions, creates a tiny placeholder, WebP and AVIF derivatives at 640, 1024, 1600, and 2400 widths, and generates a 1200 by 630 Open Graph derivative when suitable.
6. Write outputs to a staging directory.
7. Verify all expected derivative files and dimensions.
8. Move staged output into the versioned public directory atomically on the same mounted volume.
9. Update metadata and state to READY in a transaction, then invalidate affected public cache tags.

The 320 px thumbnail is for the admin library. The 640 px derivative is for small cards/mobile; 1024 px for normal content; 1600 px for desktop content; 2400 px for hero/full-width presentation. Do not generate 2560 px until profiling shows a real need.

Use Pillow plus pillow-avif-plugin. The image-worker Docker build and an integration test must prove AVIF encoding before the feature is accepted; no unverified codec assumption is acceptable.

Processing state is one of PROCESSING, READY, FAILED, or DELETED. On failure, retain a safe diagnostic message for administrators, preserve the original for retry, increment attempts, and show Retry processing. Use Celery retry policy for transient faults. Tasks must be safe if delivered more than once. A media cleanup task runs only after a soft-delete transaction and must never delete shared/referenced media.

Celery must use Redis deliberately: acknowledgment/retry settings are configured for at-least-once delivery, worker loss requeues tasks, task time limits protect the worker, and processing is idempotent. Redis persistence is enabled for the broker volume, but Redis is not treated as the system of record.

### 6.4 Image delivery

Frontend image components use picture/source or equivalent responsive markup with AVIF first, WebP fallback, srcset, sizes, width/height, and accurate alt text. Offscreen images use lazy loading. The hero uses priority/preload. Use blur placeholders only when the image already has a generated placeholder; never embed high-resolution data URIs.

Nginx serves derivative files directly. FastAPI does not read and stream public media files. Nginx enables compression for applicable text assets, not already-compressed AVIF/WebP files.

### 6.5 Backup and future migration

Back up both PostgreSQL and the entire media volume. A database-only backup is not a recovery plan. Run encrypted off-host backups daily, define retention, and perform a documented restore test at least quarterly.

Local volume storage remains correct while the app runs on one server. When horizontal application/worker scaling is actually required, introduce a storage interface and migrate to S3-compatible object storage through a separately approved project. Do not pre-install MinIO now.

## 7. Internationalization, SEO, and accessibility

### 7.1 Bilingual content

Store explicitly localized fields such as title_en/title_fa, description_en/description_fa, alt_en/alt_fa, and caption_en/caption_fa. Do not create a generic translation table for exactly two known locales.

English renders with lang=en and dir=ltr. Persian renders with lang=fa and dir=rtl. Localized numeric/date display uses the appropriate locale, but database values for identifiers and dates remain normalized. Persian content is real content, not machine-translated filler.

### 7.2 SEO

For every published public route:

- Generate title, description, canonical URL, Open Graph, and Twitter metadata in its locale.
- Emit alternate hreflang links for English, Persian, and x-default.
- Include published pages only in the sitemap; drafts and admin routes are excluded.
- Provide robots.txt that disallows /admin and private/internal API paths.
- Generate Organization and WebSite JSON-LD globally; use CreativeWork/architecture-project structured data for projects and Article structured data for journal articles when complete enough to be truthful.
- Use a selected, processed public Open Graph image rather than an original upload.
- Return a genuine localized 404 for missing/unpublished public content.

SEO fields have content fallbacks: project/article title and excerpt may generate default metadata, but an admin validation warning appears when a published item lacks a deliberate SEO title or description.

### 7.3 Accessibility acceptance standard

The target is WCAG 2.2 AA for the public and admin applications.

- Use semantic landmarks, a visible skip link, one logical H1, and correct heading order.
- All actionable controls have accessible names, visible keyboard focus, and full keyboard operation.
- Menu, locale picker, theme selector, filters, modal gallery, dialog, and drag/reorder controls have keyboard alternatives and correct focus restoration.
- Images require meaningful localized alt text before publication. Decorative images explicitly use empty alt text. Captions and credits are rendered when supplied.
- Meet normal-text contrast of at least 4.5:1 and large-text contrast of at least 3:1 in both themes. Do not rely on color alone for state.
- Preserve zoom/reflow at 200 percent and avoid horizontal scrolling at mobile widths.
- Honor prefers-reduced-motion and never autoplay audio.
- Form errors are associated with their fields, announced appropriately, and preserve valid user input after an error.
- Automated axe checks are necessary but do not replace manual keyboard, screen-reader, RTL, and visual contrast review.

## 8. Security and privacy requirements

### 8.1 Authentication and sessions

Administrator passwords are hashed with Argon2id; no plaintext password, reset token, or secret appears in logs, browser storage, source control, screenshots, or seed data. The first administrator is created through an idempotent provisioning command using protected deployment environment variables; there is no default password.

Use a random opaque session token stored only in an HttpOnly, Secure, SameSite=Lax cookie. Store only a hash of that session token in Redis with an 8-hour absolute expiry. Session rotation occurs at login. Logout deletes the server-side session. Do not use JWTs in localStorage.

All state-changing admin requests require:

- Authentication.
- Same-origin/allowlisted Origin validation.
- A session-bound CSRF token submitted in a custom header and compared in constant time.

Rate-limit login by IP and normalized account identifier. Recommended initial limits are 5 failed attempts per 15 minutes per IP and 10 per hour per account, with safe generic error responses.

### 8.2 Application and network hardening

- Production is same-origin through Nginx. CORS is disabled by default; development may allow only the configured local frontend origin.
- Request models reject unexpected fields where appropriate. Validate query pagination, sort/filter allowlists, UUIDs, slugs, and MIME/image data.
- Parameterized SQLAlchemy operations only. Never concatenate user values into SQL.
- Do not render user/admin text as arbitrary HTML.
- Hide FastAPI docs and detailed tracebacks in production.
- Set security headers. CSP uses a per-request nonce generated by Next.js middleware; do not apply an unsafe static CSP just to make a build work. Also send frame-ancestors 'none', X-Content-Type-Options: nosniff, Referrer-Policy: strict-origin-when-cross-origin, and a restrictive Permissions-Policy.
- Redirect HTTP to HTTPS. Enable HSTS only after a valid HTTPS deployment is confirmed.
- Containers run as non-root where the base image permits, have minimal packages, read-only root filesystems where feasible, and writable mounts only where required.
- Secrets are injected through protected environment configuration. Commit only .env.example with names and harmless placeholders.
- Rotate administrator/session/signing secrets through documented operational procedure.

### 8.3 Privacy and abuse

Contact-message data is collected only for communication. Log only minimal operational metadata needed for abuse handling; do not log message text, passwords, cookies, or uploaded file contents. Define a retention policy before launch and provide a manual admin delete/archive process.

Dependency updates are not assumed safe. Review changelogs and advisories, update lockfiles in an isolated pull request, run the full test suite and container build, and only then deploy.

## 9. Version baseline verified on 5 September 2026

This is a reproducibility baseline, not permission to use floating versions. Pin direct dependencies exactly in package manifests, commit pnpm-lock.yaml and uv.lock, and build container images from immutable digests recorded during release. Do not use latest tags in source-controlled Compose or Dockerfiles.

### 9.1 Runtime and container baseline

| Component | Exact baseline |
| --- | --- |
| Node.js LTS | 24.20.0 |
| npm bundled with Node baseline | 11.19.0 |
| pnpm package manager | 11.25.0 |
| Python | 3.14.7 |
| uv package/project manager | 0.12.9 |
| Docker Desktop (Windows development baseline) | 4.89.0 |
| Docker Compose (development baseline) | 5.4.0 |
| PostgreSQL official image | postgres:18.6, then pin the tested platform digest |
| Redis official image | redis:8.10.1, then pin the tested platform digest |
| Nginx stable official image | nginx:1.30.4-alpine, then pin the tested platform digest |
| Node build image | node:24.20.0-bookworm-slim, then pin the tested platform digest |
| Python API/worker image | python:3.14.7-slim-bookworm, then pin the tested platform digest |

### 9.2 Frontend package baseline

| Package | Exact version | Role |
| --- | --- | --- |
| next | 16.3.4 | App Router framework |
| react | 19.2.8 | UI runtime |
| react-dom | 19.2.8 | DOM/server renderer |
| typescript | 7.0.2 | Type checking |
| tailwindcss | 4.3.3 | Token-driven styling |
| @tailwindcss/postcss | 4.3.3 | Tailwind PostCSS integration |
| motion | 13.2.0 | Restrained UI motion |
| next-intl | 4.14.2 | Locale routing and messages |
| react-hook-form | 7.87.0 | Admin/contact form state and validation integration |
| @hookform/resolvers | 5.9.1 | React Hook Form schema resolver |
| zod | 4.5.4 | Frontend schema validation |
| eslint | 10.9.1 | Static analysis |
| prettier | 3.9.6 | Deterministic formatting |
| vitest | 4.1.11 | Frontend unit/component tests |
| @playwright/test | 1.62.1 | End-to-end and visual-browser tests |
| @axe-core/playwright | 4.13.0 | Automated accessibility checks |

Use pnpm 11.25.0, enable Corepack where provided by the Node 24.20.0 toolchain, declare `packageManager: "pnpm@11.25.0"`, and commit `pnpm-lock.yaml`. Do not install a second animation library, Bootstrap, Material UI, Ant Design, Redux, Zustand, Three.js, or GSAP for release 1.

### 9.3 Backend package baseline

| Package | Exact version | Role |
| --- | --- | --- |
| fastapi[standard] | 0.141.1 | API framework/server tooling |
| uvicorn[standard] | 0.52.4 | Explicit production ASGI server pin |
| pydantic | 2.13.5 | Request/response/domain validation |
| python-multipart | 0.0.32 | Multipart upload parsing |
| sqlalchemy | 2.0.52 | ORM and query layer |
| alembic | 1.19.2 | Schema migrations |
| psycopg[binary] | 3.3.5 | PostgreSQL driver |
| pydantic-settings | 2.15.0 | Typed configuration |
| pwdlib[argon2] | 0.3.1 | Argon2id password hashing |
| redis[hiredis] | 6.4.0 | Redis client compatible with the Celery/Kombu Redis transport constraint |
| celery[redis] | 5.6.3 | Asynchronous image tasks using Redis broker only |
| pillow | 12.3.0 | Image decode/transform |
| pillow-avif-plugin | 1.6.0 | AVIF output support |
| email-validator | 2.3.0 | Email-address validation |
| pytest | 9.1.1 | Backend test runner |
| pytest-cov | 7.1.0 | Coverage reporting |
| mypy | 2.3.1 | Static type checking |
| ruff | 0.16.5 | Formatting and linting |
| httpx | 0.28.1 | FastAPI test/client transport |

Use uv for backend dependency management, define the Python requirement as ==3.14.7 initially, and commit uv.lock. The image codec test is mandatory because package installation alone does not prove codec behavior in the final Linux container.

Compatibility correction recorded on 5 September 2026: the Python Redis client is pinned to 6.4.0 because Celery 5.6.3 enables `kombu[redis]`, and Kombu 5.6.1 requires `redis>=4.5.2,<6.5` (excluding 4.5.5 and 5.0.2). This client-library correction does not change the independently pinned Redis server image `redis:8.10.1`.

### 9.4 Official version sources

The following official registries and project sources were consulted on 5 September 2026:

- [Node.js v24.20.0 archive](https://nodejs.org/en/download/archive/v24.20.0) and [Node.js release index](https://nodejs.org/dist/index.json)
- [Python 3.14.7 release](https://www.python.org/downloads/release/python-3147/)
- [PostgreSQL 18.6 release notes](https://www.postgresql.org/docs/release/18.6/), [Redis Open Source 8.10 release notes](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.10-release-notes/), and [Nginx stable download page](https://nginx.org/en/download.html)
- [Docker Desktop release notes](https://docs.docker.com/desktop/release-notes/)
- [pnpm](https://www.npmjs.com/package/pnpm), [Next.js](https://www.npmjs.com/package/next), [React](https://www.npmjs.com/package/react), [TypeScript](https://www.npmjs.com/package/typescript), and [Tailwind CSS](https://www.npmjs.com/package/tailwindcss)
- [Motion](https://www.npmjs.com/package/motion), [next-intl](https://www.npmjs.com/package/next-intl), [React Hook Form](https://www.npmjs.com/package/react-hook-form), [hookform resolvers](https://www.npmjs.com/package/@hookform/resolvers), [Zod](https://www.npmjs.com/package/zod), [ESLint](https://www.npmjs.com/package/eslint), [Prettier](https://www.npmjs.com/package/prettier), [Vitest](https://www.npmjs.com/package/vitest), [Playwright](https://www.npmjs.com/package/@playwright/test), and [axe for Playwright](https://www.npmjs.com/package/@axe-core/playwright)
- [FastAPI](https://pypi.org/project/fastapi/), [Uvicorn](https://pypi.org/project/uvicorn/), [Pydantic](https://pypi.org/project/pydantic/), [python-multipart](https://pypi.org/project/python-multipart/), [SQLAlchemy](https://pypi.org/project/SQLAlchemy/), [Alembic](https://pypi.org/project/alembic/), [Psycopg](https://pypi.org/project/psycopg/), [pydantic-settings](https://pypi.org/project/pydantic-settings/), [pwdlib](https://pypi.org/project/pwdlib/), [redis-py](https://pypi.org/project/redis/), [Celery](https://pypi.org/project/celery/), [Pillow](https://pypi.org/project/pillow/), [pillow-avif-plugin](https://pypi.org/project/pillow-avif-plugin/), [email-validator](https://pypi.org/project/email-validator/), [pytest](https://pypi.org/project/pytest/), [pytest-cov](https://pypi.org/project/pytest-cov/), [mypy](https://pypi.org/project/mypy/), [Ruff](https://pypi.org/project/ruff/), [HTTPX](https://pypi.org/project/httpx/), and [uv](https://pypi.org/project/uv/)
- [PostgreSQL official image](https://hub.docker.com/_/postgres), [Redis official image](https://hub.docker.com/_/redis), [Nginx official image](https://hub.docker.com/_/nginx), [Node official image](https://hub.docker.com/_/node), and [Python official image](https://hub.docker.com/_/python)

Before any later upgrade, re-check the official source and record the reason, target version, lockfile change, image digest, test evidence, and rollback plan in the pull request.

## 10. Repository layout

    voluma-architecture/
      frontend/
        src/
          app/
            [locale]/
              page.tsx
              projects/
              expertise/
              process/
              studio/
              journal/
              contact/
              privacy/
              search/
            admin/
          components/
            public/
            admin/
            layout/
            media/
            motion/
            ui/
          features/
            projects/
            journal/
            media/
          i18n/
          lib/
          styles/
        public/
          fonts/
          icons/
        tests/
        e2e/
        package.json
        pnpm-lock.yaml
        Dockerfile
      backend/
        app/
          api/
            public/
            admin/
          core/
          db/
          models/
          schemas/
          services/
          tasks/
          main.py
        alembic/
        tests/
          unit/
          integration/
        pyproject.toml
        uv.lock
        Dockerfile
      nginx/
        nginx.conf
        conf.d/
      infra/
        compose/
        scripts/
        backups/
      docs/
        adr/
        runbooks/
        api/
      .github/workflows/
      docker-compose.yml
      docker-compose.dev.yml
      .env.example
      .gitignore
      .dockerignore
      AGENTS.md
      README.md

Use a root AGENTS.md that points to this specification, lists validation commands, and preserves the architecture/security rules. Keep a short ADR whenever a material architectural decision changes. Avoid duplicate, drifting documentation.

## 11. Docker Compose deployment

### 11.1 Services and volumes

Production Compose has these application services:

| Service | Responsibility |
| --- | --- |
| frontend | Next.js production server |
| api | FastAPI application |
| worker | Celery image-processing and cleanup worker |
| postgres | PostgreSQL durable database |
| redis | Cache/session/rate-limit infrastructure plus Celery broker transport; never a Celery result backend |
| nginx | Only externally exposed reverse proxy and public media server |

Named persistent volumes are:

- postgres_data for database files.
- media_data mounted read/write by api and worker and read-only by nginx.
- redis_data for configured Redis append-only persistence.

Nginx routes / to frontend, /api to api, and /media to the read-only public media subtree. It has health-aware upstream configuration, correct forwarded headers, upload size protection, no cache for authenticated/API responses, and immutable cache headers only for fingerprinted public derivatives.

### 11.2 Development, deployment, and rollback

Development Compose may expose database/Redis ports only to localhost and may mount source code. Production Compose has no source bind mounts, no development reloaders, and no unnecessary port mappings.

The release procedure is:

1. Build immutable frontend, API/worker, and Nginx images from the committed lockfiles.
2. Scan images and record image digests.
3. Take verified PostgreSQL and media backups.
4. Run Alembic upgrade head as a one-shot release step before new API/worker processes receive traffic.
5. Start/update services and wait for health checks.
6. Run smoke checks through Nginx: localized home, localized project, media derivative, contact validation, admin authentication, and headers.
7. Monitor logs, queue failures, media volume capacity, backup result, and certificate expiry.

Rollback means returning to the prior image digests and executing only an explicitly prepared reversible migration plan. A schema migration that cannot be rolled back must be declared before deployment and backed by a tested restore procedure.

TLS uses a valid production certificate mounted/configured for Nginx. HTTP redirects to HTTPS. Certificate issuance and renewal are operationally documented; they are not left as an unexplained manual step.

## 12. Engineering rules

1. Work in phases. Do not build a backend-first project and discover the visual product at the end.
2. Do not begin backend/content integration until the static mock-data Home, Projects archive, and Project detail pass desktop/mobile, light/dark, and EN/FA visual review.
3. No placeholder claim, fake award, fictional client, fabricated metric, or unlicensed media may ship. Fixtures are clearly marked development-only.
4. Every new persisted field needs a migration, schema validation, admin behavior, public behavior if applicable, tests, and documentation update.
5. Every public image needs dimensions, a responsive delivery path, localized alt policy, and a defined cache strategy.
6. Do not expose draft/private/original media from a public endpoint, sitemap, metadata, or cache.
7. Do not use localStorage for secrets, authenticated sessions, or server-authoritative permissions.
8. Do not silently add dependencies. Explain the need, pin it, update the lockfile, test it, and record it in the dependency catalog.
9. Never run destructive database/media commands against production without a verified target and backup.
10. Keep diffs small and coherent. Avoid drive-by reformatting and unrelated refactors.
11. Treat linting and unit tests as necessary but insufficient. Verify containers, migrations, Nginx behavior, real worker processing, and browser flows.
12. Do not claim production readiness, successful deployment, delivery, or performance without the corresponding observed evidence.

## 13. Phased implementation plan

### Phase 0 — repository and scope freeze

Create the repository, root documentation, AGENTS.md, .editorconfig, gitignore, env examples, Docker ignore files, license decision, issue/PR templates if used, and CI skeleton. Record this specification in docs/product or docs/architecture. Initialize pnpm and uv lockfiles from the version baseline. Produce an ADR for local persistent media storage and one for frontend-first delivery.

Exit criteria: clean repository, reproducible local bootstrap, all direct versions locked, no secrets committed, and this specification referenced by AGENTS.md.

### Phase 1 — visual system and static frontend

Create local font loading, design tokens, theme primitives, locale routing, RTL/LTR foundations, responsive shell, navigation, footer, mock content types, and the full Home, Projects archive, and Project detail routes using representative fixture media.

Exit criteria: four-combination responsive review, no layout breaks, no generic dashboard/card aesthetic, theme flash avoided, keyboard navigation works, and static routes meet the agreed design direction.

### Phase 2 — interaction, remaining public routes, and browser QA

Implement motion policy, archive filter/list switch, accessible gallery, Expertise, Process, Studio, Journal, article, Contact, Privacy, Search, 404, SEO shell, sitemap/robots, and automated browser tests with screenshots.

Exit criteria: every public route exists, interactions have reduced-motion/keyboard behavior, both locales are complete structurally, and baseline accessibility/browser tests pass.

### Phase 3 — backend foundation and public read APIs

Create FastAPI configuration, models, Alembic initial migration, public read schemas/endpoints, PostgreSQL indexes, Redis tagged cache, content fixtures, and health endpoints. Render frontend from the real public API with no-store frontend data fetch.

Exit criteria: public response schemas are stable, cache invalidation is tested, unpublished content cannot leak, migrations apply to an empty PostgreSQL database, and frontend preserves the approved visual result with real API data.

### Phase 4 — administrative CMS and authentication

Implement initial administrator provisioning, opaque Redis sessions, CSRF, rate limiting, audit events, dashboard, CRUD/order flows for all scoped content, project block editor, publishing validation, messages, and settings.

Exit criteria: an administrator can create, order, draft, publish, unpublish, and update all scoped content in two languages without database access; authentication/security tests pass; public cache invalidates correctly.

### Phase 5 — media pipeline

Implement upload validation, media library, Celery worker, shared volume, image derivative generation, processing state, retry, cleanup, Nginx media delivery, and end-to-end image/cache tests.

Exit criteria: a 50 MiB boundary test behaves correctly; an accepted image becomes READY through a real Redis/Celery worker; AVIF/WebP derivatives are verified; originals are inaccessible; Nginx serves versioned media with immutable cache headers; retry and recovery work.

### Phase 6 — production hardening and release

Create production Dockerfiles and Compose, Nginx TLS/headers/routing, deployment runbook, backup/restore runbook, monitoring checklist, CI gates, image scan, performance budget evaluation, and release smoke suite.

Exit criteria: a clean host deployment from documented steps succeeds; restore procedure has evidence; all gates pass; production environment contains no development defaults or public database/Redis ports.

## 14. Quality, testing, and CI

### 14.1 Required test layers

| Layer | Required evidence |
| --- | --- |
| Frontend static analysis | ESLint, TypeScript noEmit, production build |
| Frontend unit/component | Vitest for locale utilities, formatters, navigation state, filter serialization, accessibility-sensitive components |
| Browser E2E | Playwright for public routes, EN/FA/RTL, themes, filters, gallery, contact, admin CRUD/auth, and mobile viewport |
| Automated accessibility | axe on representative pages in both themes/locales; manual keyboard and screen-reader smoke review |
| Visual regression | Playwright approved screenshots for key public pages at desktop/mobile in both locale directions |
| Backend unit | validation, permissions, service/cache rules, media path/version behavior |
| Backend integration | FastAPI with real PostgreSQL and Redis, Alembic migration, session/CSRF/rate limits, publish/unpublish cache invalidation |
| Worker integration | real Celery worker + Redis + mounted media volume; derivative/READY/retry behavior |
| Nginx/Compose | build, routes, forwarded headers, no public originals, media cache headers, health behavior |
| Security | dependency audit, secret scan, image scan, production configuration review |

### 14.2 CI gates

Every pull request runs:

1. Frontend install with frozen lockfile, lint, typecheck, unit tests, and production build.
2. Backend locked sync, Ruff format check/lint, mypy, pytest with coverage, and Alembic migration check.
3. Docker Compose build and smoke stack.
4. Playwright critical path plus axe tests.
5. Secret scanning, dependency audit, and container image vulnerability scan.
6. Markdown/link/documentation checks where configured.

CI failure is not waived by a local pass. Local success is not described as live CI evidence. Container build success is not described as browser or real-worker evidence.

### 14.3 Performance budgets

Measure on a production-like build with throttled mobile and a representative project:

- No original image request from a public page.
- LCP resource is a prioritized responsive derivative.
- Offscreen images are lazy.
- Public derivative image URLs are immutable and cacheable.
- Initial JavaScript excludes unneeded editor/admin/gallery code from public pages by route-level code splitting.
- Avoid client-side data waterfalls; use server-rendered public data.
- Document Lighthouse/Core Web Vitals measurements rather than making an unsupported score promise.

## 15. Definition of Done

The initial release is done only when all statements below have observed evidence:

- The repository is named voluma-architecture and its documentation identifies VOLUMA consistently.
- Every scoped public and admin route exists and has a real loading/error/empty state where needed.
- Home, archive, project detail, expertise, process, studio, journal, article, contact, privacy, search, and localized 404 work in English and Persian with genuine LTR/RTL layout.
- Light, dark, and system theme modes work without a flash and with usable contrast.
- The public visual product matches the editorial architecture direction and passes approved responsive visual review before backend integration is declared complete.
- An administrator can manage all scoped content, ordering, publications, SEO settings, messages, and media without direct SQL/filesystem work.
- Draft/unpublished content, originals, admin APIs, sessions, and secrets cannot leak into public pages or caches.
- The real Celery worker processes a valid uploaded image into verified AVIF/WebP responsive derivatives and recovers from a testable failure path.
- Nginx, not FastAPI, serves public derivative media with correct immutable cache headers.
- PostgreSQL migrations, Redis cache/session behavior, Celery delivery assumptions, shared media volume permissions, backup, and restore are verified in containers.
- Security headers, session/CSRF/rate limits, production CORS policy, upload validation, non-root containers, and secret handling have automated/manual evidence.
- Required lint, type, unit, integration, browser, accessibility, Compose, security, and migration gates pass in CI.
- Deployment and rollback/restore runbooks are executable and have been tested in a production-like environment.
- No prohibited scope has been quietly introduced and no unresolved critical/high security issue has been accepted without an explicit owner, mitigation, and release decision.

## 16. Final consistency review of this specification

The specification has been checked against the decisions captured for VOLUMA:

| Check | Result |
| --- | --- |
| Frontend-first delivery is enforced before backend integration | Pass |
| Final public scope includes Home, Projects, Expertise, Process, Studio, Journal, Contact, Privacy, Search, and 404 | Pass |
| Admin scope includes all public content, media, messages, and settings | Pass |
| FastAPI, PostgreSQL, Redis, Celery, local persistent media, and Nginx each have separate, non-overlapping responsibilities | Pass |
| Redis is explicitly not presented as image-byte cache | Pass |
| Celery uses Redis as broker only; durable task/media status remains in PostgreSQL and no result backend is configured | Pass |
| The upload contract allows multipart overhead at Nginx while keeping the authoritative source-file limit at 50 MiB | Pass |
| HTTP 202 is returned only after successful Celery enqueue; enqueue failure is recorded instead of producing a false accepted response | Pass |
| The localized Privacy route is included because the contact form collects personal information | Pass |
| Local volume is documented as single-server storage, with a future migration boundary rather than premature object storage | Pass |
| Image cache policy requires immutable versioned URLs and prevents original exposure | Pass |
| EN/FA routes, true RTL/LTR layout, dark/light/system themes, SEO, and accessibility are all acceptance criteria | Pass |
| Security design uses HttpOnly opaque server-side sessions, CSRF, rate limits, and Argon2id rather than JWT localStorage | Pass |
| Docker Compose deployment includes media/database persistence, migrations, backups, TLS, and rollback boundaries | Pass |
| Exact package/image baseline is separated from lockfile/digest policy to avoid floating-version contradictions | Pass |
| Prohibited unnecessary infrastructure remains explicit | Pass |

No contradiction remains between image performance and cache design: Celery creates derivatives, Nginx/browser caching delivers them, and Redis caches metadata/API payloads only.
