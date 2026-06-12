# E2E Testing Guide

**Date**: 2026-06-12  
**Scope**: Running and maintaining Playwright E2E tests for EduBoost V2

---

## Prerequisites

- Node.js 20+
- Python 3.12+ with `.venv` activated
- Docker Compose running (for full integration tests)

---

## Quick Start

### 1. Install Dependencies

```bash
# Install Node dependencies
cd app/frontend
npm install
cd ../..

# Install Playwright browsers
npx playwright install --with-deps chromium firefox

# Activate Python venv
source .venv/bin/activate
```

### 2. Start Backend Services

```bash
# Start the full stack
docker-compose up -d

# Wait for services to be ready
sleep 10
```

### 3. Run Tests

```bash
# Run all E2E tests
npx playwright test

# Run specific suite
npx playwright test tests/e2e/auth.spec.ts

# Run with UI (interactive mode)
npx playwright test --ui

# Run specific browser only
npx playwright test --project=chromium
```

---

## Test Suites

| Suite | File | Coverage |
|-------|------|----------|
| Authentication | `tests/e2e/auth.spec.ts` | Register, login, logout, refresh |
| Learner Journey | `tests/e2e/learner-vertical-journey.spec.ts` | Full learner flow |
| Diagnostic | `tests/e2e/diagnostic.spec.ts` | Assessment flow |
| Lesson Generation | `tests/e2e/lesson_generation_flow.spec.ts` | Lesson creation |
| Study Plans | `tests/e2e/study_plan_and_lesson.spec.ts` | Study plan display |
| Parent Portal | `tests/e2e/parent_portal.spec.ts` | Parent features |
| Privacy | `tests/e2e/privacy.spec.ts` | POPIA export/erasure |
| Onboarding | `tests/e2e/onboarding.spec.ts` | New user setup |

---

## Configuration

### Environment Variables

```bash
# Frontend URL (default: http://127.0.0.1:3050)
export PLAYWRIGHT_BASE_URL=http://localhost:3000

# Backend URL (for API checks)
export API_BASE_URL=http://localhost:8000
```

### playwright.config.ts

Key settings:
- `testDir: "./tests/e2e"` — Test discovery
- `timeout: 60_000` — Per-test timeout
- `retries: 2` — Retry on CI
- `workers: 2` — Parallelism on CI

---

## CI Integration

### GitHub Actions Workflow

Tests run automatically on:
- Every PR to `main`
- Daily schedule at 3 AM

See: `.github/workflows/e2e.yml`

### Local CI Simulation

```bash
# Run with CI-like settings
CI=true npx playwright test
```

---

## Debugging Failed Tests

### View Screenshots

Failed tests automatically capture screenshots in `test-results/`:

```bash
ls test-results/
```

### View Traces

```bash
# Open trace in Playwright UI
npx playwright show-trace test-results/<trace-file>.zip
```

### Verbose Logging

```bash
# Run with debug output
DEBUG=pw:api npx playwright test
```

---

## Writing New Tests

### Basic Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/');
    // ... test steps
  });
});
```

### Authentication Helpers

Use the setup file for authenticated tests:

```typescript
test.use({ storageState: 'tests/e2e/auth.setup.ts' });
```

### Accessibility Testing

Add axe-core assertions:

```typescript
import { injectAxe } from '@axe-core/playwright';

test('should have no a11y violations', async ({ page }) => {
  await page.goto('/');
  await injectAxe(page);
  await expect(page.locator('main')).toHaveNoA11yViolations();
});
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Test hangs | Check backend is running, increase `navigationTimeout` |
| Auth fails | Update credentials in `auth.setup.ts` |
| Flaky tests | Increase wait times, use `expect.toBeVisible()` with timeout |
| Browser not found | Run `npx playwright install` |

---

## Maintenance

- Update tests when routes change
- Keep `playwright.config.ts` in sync with CI
- Review and archive flaky tests
- Run full suite before release