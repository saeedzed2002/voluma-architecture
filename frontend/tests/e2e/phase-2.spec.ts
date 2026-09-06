import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const routeMatrix = [
  {
    en: "Places for a more attentive life.",
    fa: "فضاهایی برای زندگیِ دقیق‌تر.",
    path: "/expertise",
  },
  { en: "From question to built space.", fa: "از پرسش تا فضای ساخته‌شده.", path: "/process" },
  {
    en: "A practice built around attentive looking.",
    fa: "ممارستی بر پایهٔ نگاه دقیق.",
    path: "/studio",
  },
  { en: "Reading between projects.", fa: "برای خواندنِ میان پروژه‌ها.", path: "/journal" },
  { en: "A conversation to begin.", fa: "گفت‌وگویی برای شروع.", path: "/contact" },
  { en: "Privacy, in plain language.", fa: "حریم خصوصی، به زبان روشن.", path: "/privacy" },
  { en: "Find a line of thought.", fa: "برای یافتن یک مسیر.", path: "/search" },
] as const;

for (const route of routeMatrix) {
  test(`renders ${route.path} structurally in both locales`, async ({ page }) => {
    await page.goto(`/en${route.path}`);
    await expect(page.locator("html")).toHaveAttribute("dir", "ltr");
    await expect(page.getByRole("heading", { level: 1, name: route.en })).toBeVisible();

    await page.goto(`/fa${route.path}`);
    await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
    await expect(page.getByRole("heading", { level: 1, name: route.fa })).toBeVisible();
  });
}

test("renders the journal article and localized not-found state", async ({ page }) => {
  await page.goto("/en/journal/material-as-memory");
  await expect(
    page.getByRole("heading", { level: 1, name: "Material as a memory of place" }),
  ).toBeVisible();

  const missingResponse = await page.goto("/fa/not-a-public-route");
  expect(missingResponse?.status()).toBe(404);
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
  await expect(page.getByRole("heading", { level: 1, name: "این صفحه پیدا نشد." })).toBeVisible();
});

test("keeps nonessential reveal motion disabled when reduced motion is requested", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/en/studio");
  await expect(page.locator("[data-reveal]").first()).toHaveCSS("opacity", "1");
  await expect(page.locator("[data-reveal]").first()).toHaveCSS("transform", "none");
});

test("navigates gallery images with keyboard controls and restores the trigger focus", async ({
  page,
}) => {
  await page.goto("/en/projects/courtyard-house");
  const trigger = page.getByRole("button", { name: /Open image in gallery/ }).first();
  await trigger.click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog.getByText("Image 1 of 2")).toBeVisible();
  await page.keyboard.press("ArrowRight");
  await expect(dialog.getByText("Image 2 of 2")).toBeVisible();
  await page.getByRole("button", { name: "Previous image" }).click();
  await expect(dialog.getByText("Image 1 of 2")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(trigger).toBeFocused();
});

test("submits a validated contact enquiry through the secured service", async ({
  page,
}) => {
  await page.goto("/en/contact");
  await page.getByRole("textbox", { name: "Name" }).fill("Preview visitor");
  await page.getByRole("textbox", { name: "Email address" }).fill("visitor@example.com");
  await page
    .getByRole("textbox", { name: "Tell us about the place or question" })
    .fill("A quiet place with a careful relationship to street life and daylight.");
  await page.waitForTimeout(3_100);
  await page.getByRole("button", { name: "Send enquiry" }).click();
  await expect(page.getByText("Thank you. Your enquiry has been received.")).toBeVisible();
});

test("searches only public project and journal fixture summaries", async ({ page }) => {
  await page.goto("/en/search");
  await page.getByRole("searchbox", { name: "Search projects and journal" }).fill("Archive");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page).toHaveURL(/\/en\/search\?q=Archive/);
  await expect(page.getByRole("heading", { level: 2, name: "Archive Rooms" })).toBeVisible();
  await expect(page.getByText("1 results")).toBeVisible();
});

test("publishes the static discovery shell and keeps search out of the sitemap", async ({
  request,
}) => {
  const robots = await request.get("/robots.txt");
  await expect(robots).toBeOK();
  await expect(await robots.text()).toContain("Disallow: /admin");

  const sitemap = await request.get("/sitemap.xml");
  await expect(sitemap).toBeOK();
  const sitemapText = await sitemap.text();
  expect(sitemapText).toContain("/fa/privacy");
  expect(sitemapText).not.toContain("/en/search");
});

test("emits localized canonical, alternate, and structured discovery metadata", async ({
  page,
}) => {
  await page.goto("/fa/journal/material-as-memory");
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute(
    "href",
    /\/fa\/journal\/material-as-memory$/,
  );
  await expect(page.locator('link[hreflang="en"]')).toHaveAttribute(
    "href",
    /\/en\/journal\/material-as-memory$/,
  );
  const structuredData = await page.locator('script[type="application/ld+json"]').textContent();
  expect(structuredData).toContain('"WebSite"');
});

for (const route of ["/en/contact", "/fa/journal/material-as-memory"]) {
  test(`has no automatically detectable accessibility violations on ${route}`, async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto(route);
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
}
