# VOLUMA Phase 1 visual system

This file turns the accepted ImageGen concept set into an implementation contract.
The product specification remains the source of truth when a generated image contains
incorrect or incomplete text.

## Accepted concept set

- `phase-1-concepts/home-opening-desktop.png`
- `phase-1-concepts/home-editorial-sections-desktop.png`
- `phase-1-concepts/home-journal-footer-desktop.png`
- `phase-1-concepts/projects-archive-desktop.png`
- `phase-1-concepts/project-detail-opening-desktop.png`
- `phase-1-concepts/project-detail-editorial-desktop.png`
- `phase-1-concepts/home-mobile-en.png`
- `phase-1-concepts/home-mobile-fa.png`

The failed dark-state generation is not an accepted concept. Dark-theme tokens are
derived from the accepted dark editorial bands and are verified in the browser.

## Creative direction

- Contemporary architecture monograph with a strict twelve-column editorial grid.
- True white light surface and deep neutral charcoal dark surface.
- Near-black or soft-white type with a restrained oxidized-copper accent.
- Large natural architectural photography, square corners, stable ratios, no image tint.
- Asymmetry, ruled indices, open bands, and deliberate whitespace replace generic cards.
- Motion is limited to reveal, menu, link-line, project-hover, gallery, and theme feedback.

## Tokens

| Role | Light | Dark |
| --- | --- | --- |
| Canvas | `#ffffff` | `#171918` |
| Elevated canvas | `#f4f5f3` | `#202321` |
| Primary text | `#111211` | `#f3f4f1` |
| Muted text | `#646762` | `#aeb2ac` |
| Hairline | `#d8dad6` | `#464a46` |
| Accent | `#c74f2c` | `#e16b46` |
| Focus | `#1e5b8f` | `#83bce8` |

- Radius: zero for layout/media; `999px` is prohibited for controls.
- Shadow: none in public editorial surfaces.
- Grid gutter: `clamp(1.25rem, 3vw, 3rem)`.
- Section block spacing: `clamp(5rem, 11vw, 11rem)`.
- Motion: 180 ms controls, 550 ms editorial reveal, standard easing
  `cubic-bezier(0.22, 1, 0.36, 1)`.

## Typography

- English/UI Latin: locally hosted Instrument Sans variable, weights 400–700.
- Persian: locally hosted Vazirmatn variable, weights 300–700.
- Display: fluid `clamp`, tight tracking, line height between 0.94 and 1.08.
- Body: 1.0–1.25 rem, line height between 1.45 and 1.75.
- Labels/controls: deliberate 0.75–0.9 rem sizing; never browser-default typography.
- Persian display sizes are optically reduced and use a more generous line height.

## Container and component rules

- Header: quiet wordmark, essential navigation, locale control, theme control.
- Mobile header: labelled Menu control and a full-width ruled navigation sheet.
- Buttons/links: text-first with a line or custom SVG arrow; no rounded button chrome.
- Project archive: toolbar plus asymmetric grid/list, never a card dashboard.
- Project detail: ordered editorial blocks, semantic figures, facts rail, modal gallery,
  related projects, previous/next navigation.
- Footer: structured charcoal band with columns and hairline separators.

## Image inventory and treatment

Production assets live in `frontend/public/media` and are standalone ImageGen outputs,
not crops of UI concepts. Every image is un-tinted, uses `object-fit: cover`, has a
stable aspect ratio, and is never mirrored for RTL.

- `voluma-mountain-house.png`: home hero and broad landscape moments.
- `courtyard-house.png`: Courtyard House covers and project-detail hero.
- `northline-atelier.png`: workplace covers and editorial interior.
- `material-shadow.png`: journal and material-detail moments.

The limited Phase 1 media set is intentionally reused with different crops. All names,
dates, locations, copy, and imagery are visibly identified as development fixtures.

## Icon inventory

- Theme: custom 24 px sun/moon/system SVG, 1.5 px stroke, `currentColor`.
- Directional links: custom 24 px arrow SVG, 1.25 px stroke; direction follows document.
- Grid/list switch: custom 18 px line icons, 1.25 px stroke.
- Menu close: custom 24 px cross SVG, 1.5 px stroke.
- No decorative icon family is permitted.

## Copy lock and known concept defects

- Navigation: Projects, Expertise, Process, Studio, Journal, Contact.
- Hero: “Architecture for the life between walls.”
- Hero body: “We shape quiet, enduring places through light, material, and use.”
- Hero CTA: “Explore selected work”.
- The desktop opening generator rendered `FR` instead of the required `FA`. The
  implementation must use `FA`; this is a correction, not a creative deviation.
- The visible Phase 1 fixture disclaimer is required by the product specification even
  though it is absent from the generated concepts.

## Responsive and interaction contract

- Verify at 360, 768, 1024, 1440, and 1920 CSS pixels.
- Desktop split layouts become deliberate linear editorial sequences on mobile.
- RTL reverses reading flow, controls, alignment, and arrows; photographs remain intact.
- Search, filters, and grid/list mode serialize to the URL.
- Mobile navigation, theme modes, project links, and gallery modal are keyboard operable.
- `prefers-reduced-motion` disables transforms and nonessential transitions.
