import { expect, test } from "@playwright/test";

const administratorEmail = process.env.VOLUMA_E2E_ADMIN_EMAIL;
const administratorPassword = process.env.VOLUMA_E2E_ADMIN_PASSWORD;

test.skip(
  !administratorEmail || !administratorPassword,
  "requires isolated runtime administrator credentials",
);

test("administrator drafts, publishes, and orders an expertise entry", async ({ page }, testInfo) => {
  const title = `Browser expertise ${testInfo.project.name} ${Date.now()}`;
  await page.goto("/admin/login");
  await page.getByLabel("Email").fill(administratorEmail ?? "");
  await page.getByLabel("Password").fill(administratorPassword ?? "");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page).toHaveURL(/\/admin$/);
  await page.getByRole("link", { name: "Expertise" }).click();
  await expect(page.getByRole("heading", { name: "Expertise" })).toBeVisible();
  await page.getByRole("button", { name: "Create draft" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Draft created.");

  await page.getByRole("button", { name: "Edit" }).last().click();
  await page.getByLabel("Title / EN").fill(title);
  await page.getByLabel("Title / FA").fill("تخصص مرورگر");
  await page
    .getByLabel("Description / EN")
    .fill("A complete bilingual expertise entry published through the administrator workflow.");
  await page
    .getByLabel("Description / FA")
    .fill("یک مدخل تخصصی دوزبانه که از مسیر امن ادمین منتشر شده است.");
  await page.getByLabel("Publication state").selectOption("published");
  await page.getByRole("button", { name: "Save entry" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Entry saved.");
  await expect(page.getByRole("heading", { name: title })).toBeVisible();

  await page.goto("/en/expertise");
  await expect(page.getByRole("heading", { name: title })).toBeVisible();
  await expect(page.locator("nextjs-portal [data-nextjs-dialog]")).toHaveCount(0);
  await page.screenshot({ path: testInfo.outputPath("expertise-published.png"), fullPage: false });
});
