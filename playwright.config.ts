/**
 * playwright.config.ts — EduBoost SA V2
 *
 * Place at the project root:
 *   playwright.config.ts
 *
 * Install:
 *   npm install -D @playwright/test
 *   npx playwright install --with-deps chromium firefox
 *
 * Run all E2E tests:
 *   npx playwright test
 *
 * Run a specific suite:
 *   npx playwright test tests/e2e/auth.spec.ts
 *
 * Run with UI (interactive):
 *   npx playwright test --ui
 *
 * Generate report:
 *   npx playwright show-report
 */

import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  // ── Test discovery ──────────────────────────────────────────────────────────
  testDir:  "./tests/e2e",
  testMatch: ["**/*.spec.ts"],

  // ── Parallelism ─────────────────────────────────────────────────────────────
  fullyParallel: true,
  workers:       process.env.CI ? 2 : undefined,   // cap workers on CI

  // ── Retry logic ─────────────────────────────────────────────────────────────
  retries: process.env.CI ? 2 : 0,

  // ── Reporting ───────────────────────────────────────────────────────────────
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }],
    // Uncomment for CI JUnit output:
    // ["junit", { outputFile: "test-results/junit.xml" }],
  ],

  // ── Global test settings ────────────────────────────────────────────────────
  use: {
    baseURL:            process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",

    // Navigation & network
    navigationTimeout:  15_000,
    actionTimeout:       8_000,

    // Capture artefacts on failure
    screenshot:         "only-on-failure",
    video:              "retain-on-failure",
    trace:              "on-first-retry",

    // Extra HTTP headers (pass auth cookies / CSRF tokens if needed)
    // extraHTTPHeaders: { "x-test-mode": "1" },
  },

  // ── Browser projects ────────────────────────────────────────────────────────
  projects: [
    {
      name:  "chromium",
      use:   { ...devices["Desktop Chrome"] },
    },
    {
      name:  "firefox",
      use:   { ...devices["Desktop Firefox"] },
    },
    {
      name:  "webkit",
      use:   { ...devices["Desktop Safari"] },
    },
    // Mobile viewports
    {
      name:  "Mobile Chrome",
      use:   { ...devices["Pixel 5"] },
    },
    {
      name:  "Mobile Safari",
      use:   { ...devices["iPhone 13"] },
    },
  ],

  // ── Dev-server auto-start ────────────────────────────────────────────────────
  // Uncomment if you want Playwright to spin up Next.js automatically:
  // webServer: {
  //   command:            "npm run dev",
  //   url:                "http://localhost:3000",
  //   reuseExistingServer: !process.env.CI,
  //   timeout:            120_000,
  // },

  // ── Output directories ───────────────────────────────────────────────────────
  outputDir: "test-results",
});
