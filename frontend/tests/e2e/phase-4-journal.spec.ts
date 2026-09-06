import { expect, test } from "@playwright/test";

const administratorEmail = process.env.VOLUMA_E2E_ADMIN_EMAIL;
const administratorPassword = process.env.VOLUMA_E2E_ADMIN_PASSWORD;

test.skip(
  !administratorEmail || !administratorPassword,
  "requires isolated runtime administrator credentials",
);

test("administrator publishes a bilingual journal article with an editorial text block", async ({ page }, testInfo) => {
  const suffix = `${testInfo.project.name}-${Date.now()}`.toLowerCase().replace(/[^a-z0-9-]/g, "-");
  const categorySlug = `field-notes-${suffix}`;
  const categoryTitle = `Field Notes ${suffix}`;
  const articleSlug = `measured-journal-${suffix}`;
  const articleTitle = `Measured Journal ${testInfo.project.name}`;

  await page.goto("/admin/login");
  await page.getByLabel("Email").fill(administratorEmail ?? "");
  await page.getByLabel("Password").fill(administratorPassword ?? "");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/admin$/);

  await page.getByRole("link", { name: "Journal" }).click();
  const categorySection = page.locator('section[aria-labelledby="journal-categories-title"]');
  await categorySection.getByLabel("Slug", { exact: true }).fill(categorySlug);
  await categorySection.getByLabel("Title / EN", { exact: true }).fill(categoryTitle);
  await categorySection.getByLabel("Title / FA", { exact: true }).fill("یادداشت‌های میدانی");
  await categorySection.getByRole("button", { name: "Create category" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Journal category created.");

  const articleSection = page.locator('section[aria-labelledby="journal-articles-title"]');
  const categorySelect = articleSection.getByRole("combobox", { name: "Category" });
  const categoryId = await categorySelect
    .getByRole("option", { name: categoryTitle, exact: true })
    .getAttribute("value");
  expect(categoryId).not.toBeNull();
  await categorySelect.selectOption(categoryId ?? "");
  await articleSection.getByLabel("Slug", { exact: true }).fill(articleSlug);
  await articleSection.getByLabel("Title / EN", { exact: true }).fill(articleTitle);
  await articleSection.getByLabel("Title / FA", { exact: true }).fill("یادداشت سنجیده");
  await articleSection
    .getByLabel("Excerpt / EN", { exact: true })
    .fill("A bilingual journal article published through the protected administrator flow.");
  await articleSection
    .getByLabel("Excerpt / FA", { exact: true })
    .fill("یک یادداشت دوزبانه که از مسیر امن مدیریت منتشر شده است.");
  await articleSection.getByLabel("Body / EN", { exact: true }).fill("A measured English journal paragraph.");
  await articleSection.getByLabel("Body / FA", { exact: true }).fill("یک بند فارسی سنجیده برای یادداشت.");
  await articleSection.getByRole("combobox", { name: "Publication state" }).selectOption("published");
  await articleSection.getByRole("button", { name: "Create journal draft" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Journal article published.");

  await page.goto(`/en/journal/${articleSlug}`);
  await expect(page.getByRole("heading", { name: articleTitle })).toBeVisible();
  await expect(page.getByText("A measured English journal paragraph.")).toBeVisible();
  await expect(page.locator("nextjs-portal [data-nextjs-dialog]")).toHaveCount(0);
});
