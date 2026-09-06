import { expect, test } from "@playwright/test";

const administratorEmail = process.env.VOLUMA_E2E_ADMIN_EMAIL;
const administratorPassword = process.env.VOLUMA_E2E_ADMIN_PASSWORD;

test.skip(
  !administratorEmail || !administratorPassword,
  "requires isolated runtime administrator credentials",
);

test("administrator publishes people and recognition that render on the public studio page", async ({ page }, testInfo) => {
  const suffix = `${testInfo.project.name} ${Date.now()}`;
  const personName = `Studio member ${suffix}`;
  const recognitionTitle = `Recognition ${suffix}`;

  await page.goto("/admin/login");
  await page.getByLabel("Email").fill(administratorEmail ?? "");
  await page.getByLabel("Password").fill(administratorPassword ?? "");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/admin$/);

  await page.getByRole("link", { name: "People" }).click();
  await page.getByRole("button", { name: "Create draft" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Draft created.");
  await page.getByRole("button", { name: "Edit" }).last().click();
  await page.getByLabel("Name").fill(personName);
  await page.getByLabel("Role / EN").fill("Architect");
  await page.getByLabel("Role / FA").fill("معمار");
  await page.getByLabel("Publication state").selectOption("published");
  await page.getByRole("button", { name: "Save entry" }).click();
  await expect(page.getByRole("heading", { name: personName })).toBeVisible();

  await page.getByRole("link", { name: "Recognition" }).click();
  await page.getByRole("button", { name: "Create draft" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Draft created.");
  await page.getByRole("button", { name: "Edit" }).last().click();
  await page.getByLabel("Title / EN").fill(recognitionTitle);
  await page.getByLabel("Title / FA").fill("تقدیر مرورگر");
  await page.getByLabel("Publication state").selectOption("published");
  await page.getByRole("button", { name: "Save entry" }).click();
  await expect(page.getByRole("heading", { name: recognitionTitle })).toBeVisible();

  await page.goto("/en/studio");
  await expect(page.getByRole("heading", { name: "People" })).toBeVisible();
  await expect(page.getByRole("heading", { name: personName })).toBeVisible();
  await expect(page.getByText(recognitionTitle, { exact: true })).toBeVisible();
  await expect(page.locator("nextjs-portal [data-nextjs-dialog]")).toHaveCount(0);
  await page.screenshot({ path: testInfo.outputPath("studio-content-published.png"), fullPage: false });
});
