import { mkdir } from "node:fs/promises";
import { resolve } from "node:path";

import { chromium } from "@playwright/test";

const baseUrl = process.env.VOLUMA_BASE_URL ?? "http://127.0.0.1:3000";
const outputDirectory = resolve(process.cwd(), "..", "docs", "design", "phase-1-review");

const openings = [
  { locale: "en", name: "home-en-desktop", viewport: { width: 1440, height: 1000 } },
  { locale: "fa", name: "home-fa-desktop", viewport: { width: 1440, height: 1000 } },
  { locale: "en", name: "home-en-mobile", viewport: { width: 390, height: 844 } },
  { locale: "fa", name: "home-fa-mobile", viewport: { width: 390, height: 844 } },
];

const routeReviews = [
  {
    locale: "en",
    name: "projects-en-desktop-light",
    path: "/projects",
    theme: "light",
    viewport: { width: 1440, height: 1000 },
  },
  {
    locale: "fa",
    name: "projects-fa-mobile-dark",
    path: "/projects",
    theme: "dark",
    viewport: { width: 390, height: 844 },
  },
  {
    locale: "en",
    name: "project-en-desktop-light",
    path: "/projects/courtyard-house",
    theme: "light",
    viewport: { width: 1440, height: 1000 },
  },
  {
    locale: "fa",
    name: "project-fa-mobile-dark",
    path: "/projects/courtyard-house",
    theme: "dark",
    viewport: { width: 390, height: 844 },
  },
];

await mkdir(outputDirectory, { recursive: true });

const browser = await chromium.launch({ channel: "chrome" });

async function capture({ locale, name, path = "", theme, viewport }, fullPage = false) {
  const context = await browser.newContext({
    colorScheme: theme,
    reducedMotion: "reduce",
    viewport,
  });
  await context.addInitScript((selectedTheme) => {
    window.localStorage.setItem("voluma-theme", selectedTheme);
  }, theme);

  const page = await context.newPage();
  await page.goto(`${baseUrl}/${locale}${path}`, { waitUntil: "networkidle" });
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({
    animations: "disabled",
    fullPage,
    path: resolve(outputDirectory, `${name}${fullPage ? "-full" : ""}.jpg`),
    quality: 86,
    type: "jpeg",
  });
  await context.close();
}

for (const opening of openings) {
  for (const theme of ["light", "dark"]) {
    await capture({ ...opening, name: `${opening.name}-${theme}`, theme });
  }
}

for (const review of routeReviews) {
  await capture(review);
}

await capture(
  {
    locale: "en",
    name: "home-en-desktop-light",
    theme: "light",
    viewport: { width: 1440, height: 1000 },
  },
  true,
);
await capture(
  {
    locale: "fa",
    name: "home-fa-mobile-dark",
    theme: "dark",
    viewport: { width: 390, height: 844 },
  },
  true,
);

await browser.close();
