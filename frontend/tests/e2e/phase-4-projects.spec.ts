import { expect, test } from "@playwright/test";

const administratorEmail = process.env.VOLUMA_E2E_ADMIN_EMAIL;
const administratorPassword = process.env.VOLUMA_E2E_ADMIN_PASSWORD;

test.skip(
  !administratorEmail || !administratorPassword,
  "requires isolated runtime administrator credentials",
);

test("administrator creates, publishes, and renders a bilingual project block", async ({ page }, testInfo) => {
  const slug = `browser-project-${testInfo.project.name}-${Date.now()}`;
  await page.goto("/admin/login");
  await page.getByLabel("Email").fill(administratorEmail ?? "");
  await page.getByLabel("Password").fill(administratorPassword ?? "");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page).toHaveURL(/\/admin$/);
  await page.getByRole("link", { name: "Projects" }).click();
  await expect(page.getByRole("heading", { name: "Projects" })).toBeVisible();
  await page.getByRole("link", { name: "Create project" }).click();

  await page.getByLabel("Immutable slug").fill(slug);
  await page.getByLabel("Title / EN", { exact: true }).fill("Browser Courtyard");
  await page.getByLabel("Title / FA", { exact: true }).fill("حیاط مرورگر");
  await page
    .getByLabel("Summary / EN", { exact: true })
    .fill("A project created through the protected administrator flow.");
  await page
    .getByLabel("Summary / FA", { exact: true })
    .fill("پروژه‌ای که از مسیر امن مدیریت ساخته شده است.");
  await page.getByLabel("Location / EN", { exact: true }).fill("Tehran");
  await page.getByLabel("Location / FA", { exact: true }).fill("تهران");
  await page.getByRole("button", { name: "Create project" }).click();

  await expect(page).toHaveURL(/\/admin\/projects\/[^/]+\/edit$/);
  await page.getByRole("tab", { name: "Content" }).click();
  await page.getByRole("button", { name: "Add text block" }).click();
  await page.getByLabel("Text body / EN").fill("A measured sequence of light and shadow.");
  await page.getByLabel("Text body / FA").fill("توالی سنجیده‌ای از نور و سایه.");
  await page.getByRole("button", { name: "Save editorial blocks" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Editorial blocks saved.");

  await page.getByRole("tab", { name: "Publishing" }).click();
  await page.getByLabel("State").selectOption("published");
  await page.getByRole("button", { name: "Save project" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Project details saved.");

  await page.goto(`/en/projects/${slug}`);
  await expect(page.getByRole("heading", { name: "Browser Courtyard" })).toBeVisible();
  await expect(page.getByText("A measured sequence of light and shadow.")).toBeVisible();
  await expect(page.locator("nextjs-portal [data-nextjs-dialog]")).toHaveCount(0);
});
