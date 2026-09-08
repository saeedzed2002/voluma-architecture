import { expect, test } from "@playwright/test";

const administratorEmail = process.env.VOLUMA_E2E_ADMIN_EMAIL;
const administratorPassword = process.env.VOLUMA_E2E_ADMIN_PASSWORD;

test.skip(
  !administratorEmail || !administratorPassword,
  "requires isolated runtime administrator credentials",
);

test("administrator can use a processed image as a bilingual journal cover", async ({
  page,
}, testInfo) => {
  const suffix = `${testInfo.project.name}-${Date.now()}`.toLowerCase().replace(/[^a-z0-9-]/g, "-");
  const categorySlug = `media-notes-${suffix}`;
  const categoryTitle = `Media notes ${suffix}`;
  const articleSlug = `managed-cover-${suffix}`;
  const articleTitle = `Managed cover ${testInfo.project.name}`;

  await page.goto("/admin/login");
  await page.getByLabel("Email").fill(administratorEmail ?? "");
  await page.getByLabel("Password").fill(administratorPassword ?? "");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.getByRole("link", { name: "Media" }).click();

  await expect(page.getByRole("heading", { name: "Managed media", exact: true })).toBeVisible();
  const uploadResponse = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      new URL(response.url()).pathname === "/api/v1/admin/media" &&
      response.status() === 202,
  );
  await page.getByLabel("Upload media source image").setInputFiles({
    buffer: Buffer.from(
      "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAEklEQVR4nGOUUDFgYGBgYgADAAUiAHD7661kAAAAAElFTkSuQmCC",
      "base64",
    ),
    mimeType: "image/png",
    name: "worker-proof.png",
  });

  await expect(
    page.getByText(
      "Upload accepted. Browser transfer is complete; image processing is now queued.",
    ),
  ).toBeVisible();
  const mediaId = String((await (await uploadResponse).json()).id);
  expect(mediaId).not.toBe("");
  const uploadedCard = page
    .locator(".admin-media-card")
    .filter({ hasText: mediaId });
  await expect(uploadedCard).toHaveCount(1, { timeout: 15_000 });
  await expect(uploadedCard.getByText("ready", { exact: true })).toBeVisible({ timeout: 15_000 });
  await uploadedCard.getByLabel("Alt text / EN").fill("A managed journal cover image");
  await uploadedCard.getByLabel("Alt text / FA").fill("تصویر روی جلد مدیریت‌شدهٔ یادداشت");
  await uploadedCard.getByRole("button", { name: "Save metadata" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Media metadata saved.");

  await page.getByRole("link", { name: "Journal" }).click();
  const categorySection = page.locator('section[aria-labelledby="journal-categories-title"]');
  await categorySection.getByLabel("Slug", { exact: true }).fill(categorySlug);
  await categorySection.getByLabel("Title / EN", { exact: true }).fill(categoryTitle);
  await categorySection.getByLabel("Title / FA", { exact: true }).fill("یادداشت‌های رسانه");
  await categorySection.getByRole("button", { name: "Create category" }).click();

  const articleSection = page.locator('section[aria-labelledby="journal-articles-title"]');
  const categorySelect = articleSection.getByRole("combobox", { name: "Category" });
  const categoryId = await categorySelect
    .getByRole("option", { name: categoryTitle, exact: true })
    .getAttribute("value");
  expect(categoryId).not.toBeNull();
  await categorySelect.selectOption(categoryId ?? "");
  await articleSection.getByLabel("Slug", { exact: true }).fill(articleSlug);
  await articleSection.getByLabel("Title / EN", { exact: true }).fill(articleTitle);
  await articleSection.getByLabel("Title / FA", { exact: true }).fill("روی جلد مدیریت‌شده");
  await articleSection
    .getByLabel("Excerpt / EN", { exact: true })
    .fill("A bilingual journal article with a managed media cover.");
  await articleSection
    .getByLabel("Excerpt / FA", { exact: true })
    .fill("یک یادداشت دوزبانه با تصویر روی جلد مدیریت‌شده.");
  await articleSection
    .getByLabel("Body / EN", { exact: true })
    .fill("A measured journal paragraph.");
  await articleSection.getByLabel("Body / FA", { exact: true }).fill("یک بند سنجیده برای یادداشت.");
  await articleSection.getByRole("button", { name: "Add image block" }).click();
  const articleImagePicker = articleSection.getByLabel("Article image");
  await articleImagePicker.getByRole("button", { name: "Choose or upload image" }).click();
  const articleImageCard = articleImagePicker
    .locator(".admin-media-picker__card")
    .filter({ hasText: mediaId });
  await expect(articleImageCard).toHaveCount(1, { timeout: 15_000 });
  await expect(articleImageCard.getByText("ready", { exact: true })).toBeVisible();
  await articleImageCard.getByRole("button", { name: "Select image" }).click();
  const coverPicker = articleSection.getByLabel("Article cover image");
  await coverPicker.getByRole("button", { name: "Choose or upload image" }).click();
  const coverImageCard = coverPicker
    .locator(".admin-media-picker__card")
    .filter({ hasText: mediaId });
  await expect(coverImageCard).toHaveCount(1, { timeout: 15_000 });
  await expect(coverImageCard.getByText("ready", { exact: true })).toBeVisible();
  await coverImageCard.getByRole("button", { name: "Select image" }).click();
  await articleSection
    .getByRole("combobox", { name: "Publication state" })
    .selectOption("published");
  await articleSection.getByRole("button", { name: "Publish journal article" }).click();
  await expect(page.locator(".admin-form__message")).toHaveText("Journal article published.");

  await page.goto(`/en/journal/${articleSlug}`);
  await expect(page.getByRole("heading", { name: articleTitle })).toBeVisible();
  await expect(page.locator(".journal-article__cover img")).toHaveAttribute(
    "src",
    new RegExp(`/media/${mediaId}/`),
  );
  await expect(page.locator(".journal-article__image img")).toBeVisible();
  await expect(page.locator("nextjs-portal [data-nextjs-dialog]")).toHaveCount(0);
});
