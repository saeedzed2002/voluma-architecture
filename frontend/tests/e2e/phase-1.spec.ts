import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";

test.beforeEach(({ page }) => {
  page.on("console", (message) => {
    if (message.type() === "error") console.error(`[browser:console] ${message.text()}`);
  });
  page.on("pageerror", (error) => console.error(`[browser:pageerror] ${error.stack}`));
  page.on("requestfailed", (request) => {
    if (request.resourceType() === "script") {
      console.error(`[browser:script-failed] ${request.url()} ${request.failure()?.errorText}`);
    }
  });
  page.on("response", (response) => {
    if (response.status() >= 400) {
      console.error(`[browser:http] ${response.status()} ${response.url()}`);
    }
  });
});

async function expectHydrated(page: Page) {
  await expect(page.locator("html")).toHaveAttribute("data-hydrated", "true", {
    timeout: 15_000,
  });
}

test("redirects unprefixed public routes to the default locale", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/en\/?$/);
});

test("renders the English editorial home and cycles theme without losing content", async ({
  page,
}) => {
  await page.goto("/en");
  await expectHydrated(page);
  await expect(
    page.getByRole("heading", { name: "Architecture for the life between walls." }),
  ).toBeVisible();
  await expect(page.getByRole("heading", { name: "Selected projects" })).toBeVisible();

  const theme = page.getByRole("button", { name: "System theme" });
  await theme.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await page.getByRole("button", { name: "Light theme" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
});

test("reloads the document for a locale change without losing the selected theme", async ({
  page,
}) => {
  await page.goto("/en/projects/archive-rooms");
  await expectHydrated(page);

  await page.getByRole("button", { name: "System theme" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await page.getByRole("button", { name: "Light theme" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");

  const localeControl = page.getByRole("link", { name: "View this page in Persian" });
  await expect(localeControl).toHaveAttribute("href", "/fa/projects/archive-rooms");
  await Promise.all([page.waitForNavigation(), localeControl.click()]);
  await expect(page).toHaveURL(/\/fa\/projects\/archive-rooms$/);

  await expectHydrated(page);
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
  await expect(page.getByRole("heading", { name: "اتاق‌های آرشیو" })).toBeVisible();
});

test("renders the Persian route with true RTL flow", async ({ page }) => {
  await page.goto("/fa");
  await expect(page.locator("html")).toHaveAttribute("lang", "fa");
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
  await expect(
    page.getByRole("heading", { name: "معماری برای زندگی میان دیوارها." }),
  ).toBeVisible();
});

test("serializes project filters and view mode in the URL", async ({ page }) => {
  await page.goto("/en/projects");
  await expectHydrated(page);
  await page.getByRole("button", { name: "Workspace" }).click();
  await expect(page).toHaveURL(/category=workspace/);
  await expect(page.getByRole("heading", { name: "Northline Atelier" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Courtyard House" })).toHaveCount(0);

  await page.getByRole("button", { name: "List" }).click();
  await expect(page).toHaveURL(/view=list/);
});

test("opens the mobile navigation and project gallery with keyboard-accessible controls", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/en");
  await expectHydrated(page);
  await page.getByRole("button", { name: "Menu" }).click();
  await expect(page.getByRole("navigation", { name: "Mobile" })).toBeVisible();

  await page.goto("/en/projects/courtyard-house");
  await expectHydrated(page);
  await page
    .getByRole("button", { name: /Open image in gallery/ })
    .first()
    .click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByRole("button", { name: "Close gallery" }).click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
});

for (const route of ["/en", "/fa", "/en/projects", "/fa/projects"]) {
  test(`has no automatically detectable accessibility violations on ${route}`, async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto(route);
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
}
