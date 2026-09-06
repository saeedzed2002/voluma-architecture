import { expect, test } from "@playwright/test";

const administratorEmail = process.env.VOLUMA_E2E_ADMIN_EMAIL;
const administratorPassword = process.env.VOLUMA_E2E_ADMIN_PASSWORD;

test.skip(
  !administratorEmail || !administratorPassword,
  "requires isolated runtime administrator credentials",
);

test("administrator can upload an image and observe asynchronous media processing", async ({ page }) => {
  await page.goto("/admin/login");
  await page.getByLabel("Email").fill(administratorEmail ?? "");
  await page.getByLabel("Password").fill(administratorPassword ?? "");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.getByRole("link", { name: "Media" }).click();

  await expect(page.getByRole("heading", { name: "Managed media", exact: true })).toBeVisible();
  await page.getByLabel("Upload media source image").setInputFiles({
    buffer: Buffer.from(
      "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAEklEQVR4nGOUUDFgYGBgYgADAAUiAHD7661kAAAAAElFTkSuQmCC",
      "base64",
    ),
    mimeType: "image/png",
    name: "worker-proof.png",
  });

  await expect(page.getByText("Upload accepted. Browser transfer is complete; image processing is now queued.")).toBeVisible();
  await expect(page.getByText("ready", { exact: true })).toBeVisible({ timeout: 15_000 });
  await expect(page.locator("nextjs-portal [data-nextjs-dialog]")).toHaveCount(0);
});
