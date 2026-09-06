import { expect, test } from "@playwright/test";

const administratorEmail = process.env.VOLUMA_E2E_ADMIN_EMAIL;
const administratorPassword = process.env.VOLUMA_E2E_ADMIN_PASSWORD;

test.skip(
  !administratorEmail || !administratorPassword,
  "requires isolated runtime administrator credentials",
);

test("administrator can open the protected site settings control", async ({ page }) => {
  await page.goto("/admin/login");
  await page.getByLabel("Email").fill(administratorEmail ?? "");
  await page.getByLabel("Password").fill(administratorPassword ?? "");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.getByRole("link", { name: "Settings" }).click();

  await expect(page.getByRole("heading", { name: "Settings", exact: true })).toBeVisible();
  await expect(page.getByLabel("Studio name")).toBeVisible();
  await expect(page.getByLabel("Default theme")).toBeVisible();
  await expect(page.getByRole("button", { name: "Save settings" })).toBeVisible();
  await expect(page.locator("nextjs-portal [data-nextjs-dialog]")).toHaveCount(0);
});
