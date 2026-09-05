import { mkdir } from "node:fs/promises";
import { resolve } from "node:path";

import { chromium } from "@playwright/test";

const baseUrl = process.env.VOLUMA_BASE_URL ?? "http://127.0.0.1:3000";
const outputDirectory = resolve(process.cwd(), "..", "docs", "design", "phase-2-review");

const reviews = [
  {
    name: "expertise-en-desktop-light",
    path: "/en/expertise",
    theme: "light",
    viewport: { width: 1440, height: 1000 },
  },
  {
    name: "process-fa-mobile-dark",
    path: "/fa/process",
    theme: "dark",
    viewport: { width: 390, height: 844 },
  },
  {
    name: "studio-en-desktop-dark",
    path: "/en/studio",
    theme: "dark",
    viewport: { width: 1440, height: 1000 },
  },
  {
    name: "journal-fa-desktop-light",
    path: "/fa/journal",
    theme: "light",
    viewport: { width: 1440, height: 1000 },
  },
  {
    name: "article-en-mobile-dark",
    path: "/en/journal/material-as-memory",
    theme: "dark",
    viewport: { width: 390, height: 844 },
  },
  {
    name: "contact-fa-desktop-light",
    path: "/fa/contact",
    theme: "light",
    viewport: { width: 1440, height: 1000 },
  },
  {
    name: "privacy-en-mobile-dark",
    path: "/en/privacy",
    theme: "dark",
    viewport: { width: 390, height: 844 },
  },
  {
    name: "search-fa-desktop-light",
    path: "/fa/search?q=%D8%A2%D8%B1%D8%B4%DB%8C%D9%88",
    theme: "light",
    viewport: { width: 1440, height: 1000 },
  },
  {
    name: "not-found-fa-mobile-dark",
    path: "/fa/not-a-public-route",
    theme: "dark",
    viewport: { width: 390, height: 844 },
  },
];

await mkdir(outputDirectory, { recursive: true });

const browser = await chromium.launch({ channel: "chrome" });

for (const review of reviews) {
  const context = await browser.newContext({
    colorScheme: review.theme,
    reducedMotion: "reduce",
    viewport: review.viewport,
  });
  await context.addInitScript((selectedTheme) => {
    window.localStorage.setItem("voluma-theme", selectedTheme);
  }, review.theme);
  const page = await context.newPage();
  await page.goto(`${baseUrl}${review.path}`, { waitUntil: "networkidle" });
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({
    animations: "disabled",
    fullPage: true,
    path: resolve(outputDirectory, `${review.name}.jpg`),
    quality: 86,
    type: "jpeg",
  });
  await context.close();
}

await browser.close();
