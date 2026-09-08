import { defineConfig, devices } from "@playwright/test";

const port = process.env.PLAYWRIGHT_PORT ?? "3000";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  // Next dev can exhaust local Windows socket resources when all browser projects
  // navigate concurrently. Keep the local and CI browser load deterministic.
  workers: 2,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    trace: "on-first-retry",
  },
  webServer: {
    command: `corepack pnpm start --port ${port}`,
    url: `http://127.0.0.1:${port}/en`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  projects: [
    {
      name: "desktop-chrome",
      // CI reaches the private BFF directly rather than through Nginx. Give
      // each browser project a distinct simulated, trusted-proxy address so a
      // negative-login test cannot consume the production IP rate-limit budget
      // of a valid-login test in the other project. Nginx replaces this header
      // with its remote address in production.
      use: {
        ...devices["Desktop Chrome"],
        channel: "chrome",
        extraHTTPHeaders: { "x-forwarded-for": "198.51.100.10" },
      },
    },
    {
      name: "mobile-chrome",
      use: {
        ...devices["Pixel 7"],
        channel: "chrome",
        extraHTTPHeaders: { "x-forwarded-for": "198.51.100.11" },
      },
    },
  ],
});
