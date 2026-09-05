# VOLUMA Phase 1 fidelity ledger

This ledger records the final concept-to-browser comparison for the Phase 1 exit
review. The product specification remains authoritative over generated concept text.

## Review evidence and method

- Accepted concepts: `docs/design/phase-1-concepts/`.
- Browser captures: `docs/design/phase-1-review/`.
- Capture method: `frontend/tests/visual/capture-phase-1.mjs` with Playwright 1.62.1,
  installed Chrome 152.0.7977.82, local fonts, disabled animations, and explicit
  locale/theme state.
- Interactive browser inspection: English/Persian, light/dark, and widths 360, 768,
  1024, 1440, and 1920 CSS pixels.
- Automated browser coverage: desktop/mobile route, locale direction, theme state,
  URL-backed archive filtering/list mode, gallery focus/Escape behavior, and axe scans.

The Playwright-managed browser download was not used: its CDN returned a
location-based HTTP 403 on the review host. Stable local Chrome is configured
explicitly instead; this is a capture-environment deviation, not a product deviation.

## Fidelity comparisons

| # | Concept intent | Browser evidence | Result |
| --- | --- | --- | --- |
| 1 | `home-opening-desktop.png`: strict split-grid hero, oversized editorial display, restrained controls, full-height architectural image | `home-en-desktop-light.jpg`, `home-fa-desktop-light.jpg` | Preserved. The Persian composition reverses reading flow without mirroring the photograph. |
| 2 | `home-editorial-sections-desktop.png`: large whitespace, ruled indices, asymmetric project rhythm, no dashboard cards | `home-en-desktop-light-full.jpg` | Preserved across the featured work, expertise, and process bands; square media and hairlines replace card chrome. |
| 3 | `home-journal-footer-desktop.png`: quiet journal field followed by a structured charcoal footer | `home-en-desktop-light-full.jpg`, `home-en-desktop-dark.jpg` | Preserved. The dark surface uses neutral charcoal and soft-white type with no gradients or shadows. |
| 4 | `projects-archive-desktop.png`: editorial archive controls and asymmetric image-led grid | `projects-en-desktop-light.jpg`, `projects-fa-mobile-dark.jpg` | Preserved. Search, category, count, and grid/list controls remain part of one ruled toolbar and serialize state to the URL. |
| 5 | `project-detail-opening-desktop.png`: image-dominant opening, restrained facts, typographic hierarchy | `project-en-desktop-light.jpg`, `project-fa-mobile-dark.jpg` | Preserved. Desktop and mobile keep the monograph hierarchy while metadata follows locale direction. |
| 6 | `project-detail-editorial-desktop.png`: ordered narrative blocks, full-bleed imagery, gallery and related-work continuation | Interactive project-detail review plus automated gallery tests | Preserved. The dialog traps intent through managed focus, closes with Escape, and returns focus to its trigger. |
| 7 | `home-mobile-en.png` and `home-mobile-fa.png`: deliberate linear mobile sequence rather than a compressed desktop grid | `home-en-mobile-light.jpg`, `home-fa-mobile-dark-full.jpg` | Preserved at 360/390 CSS pixels; navigation becomes a ruled sheet and opening content remains readable without horizontal overflow. |
| 8 | Local type system: Instrument Sans for Latin/UI and Vazirmatn for Persian | All captures and computed browser inspection | Preserved through self-hosted variable WOFF2 files; rendering has no remote-font dependency. |

## Copy and content differences

- The generated desktop opening says `FR`; the implementation uses the specified
  `FA`. This corrects a generator defect.
- English and Persian navigation, project metadata, headings, and fixture copy come
  from the canonical content model, not text rendered inside concept images.
- A visible development-fixture disclosure is present on public pages because the
  specification requires honest fixture labeling; it is absent from the concepts.

## Approved implementation deviations

- Four standalone generated architectural images are intentionally reused with
  route-specific crops because Phase 1 calls for representative fixture media. UI
  concept images are never shipped as page backgrounds or sliced into assets.
- The responsive header collapses to the labelled menu at tablet/mobile widths to
  preserve reading space and keyboard order.
- No standalone dark-theme concept was accepted after the dark generation attempt
  failed. Dark tokens are derived from the accepted charcoal editorial bands and were
  reviewed in the browser in both locale directions.
- Project subject and crop vary slightly from concept renders because production media
  are separate generated assets with stable aspect ratios and semantic alt text.

## Exit-review conclusion

The Phase 1 implementation satisfies the agreed editorial direction: twelve-column
desktop structure, asymmetrical image rhythm, local typography, white/charcoal/copper
palette, square media, hairline hierarchy, full RTL inversion, and no generic cards,
rounded control chrome, gradients, or decorative shadows. Keyboard menu/theme/gallery
behavior, reduced motion, theme initialization, and the four locale/theme combinations
have browser evidence. Remaining routes and the complete browser/SEO matrix belong to
Phase 2 and are not represented as complete here.
