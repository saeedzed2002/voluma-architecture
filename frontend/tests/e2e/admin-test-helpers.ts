import { expect, type Page } from "@playwright/test";

type AdministratorSession = {
  csrf_token: string;
};

async function administratorCsrfToken(page: Page) {
  const response = await page.request.get("/api/v1/admin/auth/me");
  expect(response.ok()).toBe(true);
  return (await response.json() as AdministratorSession).csrf_token;
}

export async function deleteAdminTestResource(page: Page, path: string) {
  const response = await page.request.delete(`/api/v1/admin${path}`, {
    headers: {
      Origin: new URL(page.url()).origin,
      "X-VOLUMA-CSRF": await administratorCsrfToken(page),
    },
  });
  expect(response.status()).toBe(204);
}
