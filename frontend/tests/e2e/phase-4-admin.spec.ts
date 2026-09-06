import { expect, test } from "@playwright/test";

test("administrator login rejects invalid credentials without a framework error", async ({ page }, testInfo) => {
  const consoleErrors: string[] = [];
  const rejectedAdminResponses: number[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => consoleErrors.push(error.message));
  page.on("response", (response) => {
    if (response.url().includes("/api/v1/admin/") && response.status() >= 400) {
      rejectedAdminResponses.push(response.status());
    }
  });

  await page.goto("/admin/login");

  await expect(page).toHaveTitle("Administration — VOLUMA");
  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
  await page.getByLabel("Email").fill(`nobody-${testInfo.project.name}@example.com`);
  await page.getByLabel("Password").fill("a valid test password");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText(
    "The email or password is not valid.",
  );
  await expect(page.locator("nextjs-portal [data-nextjs-dialog]")).toHaveCount(0);
  expect(rejectedAdminResponses.length).toBeGreaterThanOrEqual(2);
  expect(rejectedAdminResponses.every((status) => status === 401)).toBe(true);
  expect(
    consoleErrors.filter(
      (message) => !message.includes("Failed to load resource: the server responded with a status of 401"),
    ),
  ).toEqual([]);

  await page.screenshot({ path: testInfo.outputPath("admin-login-invalid-credentials.png") });
});
