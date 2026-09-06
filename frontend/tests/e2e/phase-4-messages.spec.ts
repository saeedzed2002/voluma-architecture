import { expect, test } from "@playwright/test";

const administratorEmail = process.env.VOLUMA_E2E_ADMIN_EMAIL;
const administratorPassword = process.env.VOLUMA_E2E_ADMIN_PASSWORD;

test.skip(
  !administratorEmail || !administratorPassword,
  "requires isolated runtime administrator credentials",
);

test("administrator triages a contact message without exposing it publicly", async ({ page, request }, testInfo) => {
  const suffix = `${testInfo.project.name}-${Date.now()}`.toLowerCase().replace(/[^a-z0-9-]/g, "-");
  const email = `message-${suffix}@example.com`;
  const body = "A private architectural enquiry that must only be visible in the protected administrator workspace.";

  const created = await request.post("/api/v1/contact", {
    data: {
      company: null,
      email,
      message: body,
      name: "E2E contact visitor",
      phone: null,
      project_type: "architecture",
      source_locale: "en",
      started_at: Date.now() - 5_000,
      website: "",
    },
  });
  await expect(created).toBeOK();

  await page.goto("/admin/login");
  await page.getByLabel("Email").fill(administratorEmail ?? "");
  await page.getByLabel("Password").fill(administratorPassword ?? "");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.getByRole("link", { name: "Messages" }).click();
  await expect(page.getByRole("heading", { name: "Messages", exact: true })).toBeVisible();
  await expect(page.getByText(email)).toBeVisible();
  await expect(page.getByText(body)).toBeVisible();

  await page.getByRole("combobox", { name: `State for message from ${email}` }).selectOption("archived");
  await expect(page.locator(".admin-form__message")).toHaveText("Message state saved.");
  await expect(page.locator("nextjs-portal [data-nextjs-dialog]")).toHaveCount(0);
});
