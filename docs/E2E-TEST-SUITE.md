# E2E Test Suite — Claude Code Prompt Chain
## AIWA-29 | Playwright E2E Test Suite for AIWA-Generated Frontends

**Status:** Draft v1.0
**Date:** 2026-04-28
**Scope:** Given a generated frontend application → Playwright E2E tests covering critical user journeys, integrated into the CI pipeline post-Vercel deployment (AIWA-20)

---

## Overview

This prompt chain runs after the Frontend Scaffold Generator (AIWA-17) completes and the Vercel preview deployment succeeds. It takes the feature specifications and generated pages, identifies key user flows, and produces a comprehensive Playwright test suite.

The chain produces:
1. Playwright configuration (`playwright.config.ts`)
2. Page object models for each page
3. Critical user journey tests (happy path + error paths)
4. Test data fixtures and setup/teardown
5. GitHub Actions CI integration (integrated into the existing vercel-deploy.yml pipeline)

---

## Input Contract

The chain expects a structured `APP_CONTEXT` block (same format as AIWA-17 Frontend Scaffold Generator):

```
APP_CONTEXT:
  name: string
  tagline: string
  domain: string
  features: Feature[]           # { name, description, priority, user_flows? }
  pages: Page[]                  # { name, route, components, auth_required }
  api_endpoints: Endpoint[]
  deployment_target: "vercel"
  test_user: { email, password }  # test account credentials for auth flows
```

The Control Plane provides additional context at dispatch:

```json
{
  "task_id": "<uuid>",
  "project_id": "<uuid>",
  "repo_url": "https://github.com/<org>/<repo>",
  "app_name": "<app-name>",
  "preview_url": "<vercel-preview-url>",
  "test_user": { "email": "...", "password": "..." }
}
```

---

## Prompt Chain

### Stage 1 — Playwright Configuration

```
You are setting up a Playwright E2E test suite for {APP_CONTEXT.name}.

## Project Context
- App name: {APP_CONTEXT.name}
- Domain: {APP_CONTEXT.domain}
- Preview URL: {PREVIEW_URL}
- Test user: {TEST_USER_EMAIL}

## Pages (from APP_CONTEXT)
{PAGES_LIST}

## Features (from APP_CONTEXT)
{FEATURES_LIST}

## Instructions
Create the test configuration and directory structure.

1. Create playwright.config.ts:
   - use @playwright/test
   - baseURL: process.env.BASE_URL || "{PREVIEW_URL}"
   - timeout: 30_000 (global), 10_000 (expect)
   - retries: 2 (CI mode), 0 (local)
   - workers: 4 (CI), 2 (local)
   - reporter: [["html", "playwright-report"]], [["list"]]
   - projects: chromium (default), mobile emulation (iPhone 12)
   - webServer: NOT configured — tests run against deployed preview, not local dev
   - define VIEWPORT_MOBILE: { width: 390, height: 844 }
   - define VIEWPORT_DESKTOP: { width: 1280, height: 720 }
   - fully_qualified error messages

2. Create tests/e2e/ directory with structure:
   tests/e2e/
   ├── pages/           # Page Object Models
   ├── specs/           # Test specifications
   ├── fixtures/        # Test data fixtures
   └── helpers/         # Shared test utilities

3. Create package.json entry (add to existing):
   "test:e2e": "playwright test",
   "test:e2e:ui": "playwright test --ui",
   "test:e2e:headed": "playwright test --headed",
   "test:e2e:mobile": "playwright test --project=chromium-mobile"

4. Create .env.example:
   BASE_URL=https://your-preview-url.vercel.app
   TEST_EMAIL=test@example.com
   TEST_PASSWORD=password123

5. Add to package.json devDependencies if not present:
   @playwright/test (^1.49)
   playwright (^1.49)

Write: playwright.config.ts, tests/e2e/fixtures/.gitkeep, .env.example
Update: package.json (scripts and deps if needed)

Respond with summary of files created.
```

### Stage 2 — Identify Critical User Journeys

```
Analyze the pages and features to identify all critical user journeys.

## Pages
{PAGES_LIST}

## Features
{FEATURES_LIST}

## Classification

For each page, classify its criticality:

**P0 (Must Have — core business value):**
- Authentication flows (login, register, logout)
- Primary feature actions (CRUD operations, submit forms)
- Navigation that affects app state

**P1 (Should Have — important but not critical):**
- Secondary features, list/detail views
- Error states and validation
- Empty states

**P2 (Nice to Have):**
- Edge cases, performance tests

## User Journey Mapping

For each P0/P1 page, define:

```
Journey {N}: {Journey Name}
- Route: /{route}
- Steps:
  1. {action}
  2. {assertion/result}
  3. ...
- Happy path assertions: [list of things to assert]
- Error path assertions: [list of negative cases]
- Auth required: true/false
- Mobile testable: true/false
```

## Auth Flow Detection

Check which pages require authentication and map the login flow:
- Does the app use JWT + localStorage? (check auth context from FRONTEND-SCAFFOLD)
- What is the login URL? (/login or similar)
- Does logout redirect to home or login?

Map out the auth cookie/token persistence pattern so tests can authenticate.

## API Endpoint Awareness

Identify which API calls each journey triggers (for realistic data setup):
- {ENDPOINT.method} {ENDPOINT.path} → triggered by {action}
- Used to set up test data via API calls (bypassing UI for setup where appropriate)

Respond with a structured journey map. This will drive the test generation.
```

### Stage 3 — Page Object Models

```
Create Page Object Models for each page in the test suite.

## Journeys (from Stage 2)
{JOURNEY_MAP}

## Auth Pattern
{AUTH_PATTERN}

## Instructions

For each page, create a Page Object Model in tests/e2e/pages/.

Pattern:
```typescript
import { Page, Locator, expect } from '@playwright/test';

export class {PageName}Page {
  readonly page: Page;
  // Selectors
  readonly heading: Locator;
  readonly subheading: Locator;
  readonly submitButton: Locator;
  // Form fields (for auth pages)
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  // Nav elements
  readonly navLink: Locator;

  constructor(page: Page) {
    this.page = page;
    // Initialize all locators as getByRole, getByLabel, or locator() chains
  }

  async goto() {
    await this.page.goto('/{route}');
  }

  async expectLoaded() {
    await expect(this.heading).toBeVisible();
  }
}
```

Requirements:
- Use getByRole, getByLabel, getByText — avoid CSS selectors like [data-testid]
- All locators as readonly class properties
- Typed with Locator from @playwright/test
- Constructor initializes ALL locators (no lazy loading)
- Helper methods for common sequences (e.g., login(page, email, pass))
- Auth pages: include methods for successful login, failed login, logout
- Nav pages: include methods for navigation to other sections

For auth pages specifically:
- Create a shared auth POM in tests/e2e/pages/AuthPage.ts
- login(email, password) → authenticates, returns page context
- logout() → clears auth state

Write ALL Page Object Models. Do not skip any page.

Respond with list of POMs created.
```

### Stage 4 — Happy Path Tests

```
Create Playwright test specs for all P0 critical journeys.

## Journeys
{JOURNEY_MAP}

## Page Object Models
Already created in Stage 3 — import them directly.

## Test Data Fixtures

Create test data in tests/e2e/fixtures/test-data.ts:
```typescript
export const testUsers = {
  valid: {
    email: process.env.TEST_EMAIL || 'test@example.com',
    password: process.env.TEST_PASSWORD || 'testpass123',
  },
  invalid: {
    noEmail: { password: 'testpass123' },
    noPassword: { email: 'test@example.com' },
    wrongPassword: { email: 'test@example.com', password: 'wrongpass' },
  },
};

export const featureTestData = {
  // Per-feature test data based on API endpoint schemas
};
```

## Test Spec Pattern

For each journey, create a spec file at tests/e2e/specs/{journey-slug}.spec.ts:

```typescript
import { test, expect } from '@playwright/test';
import { POM_NAME } from '../pages/POM_NAME';

test.describe('{Journey Name}', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the page
    const pom = new POM_NAME(page);
    await pom.goto();
    await pom.expectLoaded();
  });

  test('{description}', async ({ page }) => {
    const pom = new POM_NAME(page);
    // Steps...
    // Assertions...
  });

  test('{description} — mobile', async ({ page }) => {
    // Same test on mobile viewport
    await page.setViewportSize({ width: 390, height: 844 });
  });
});
```

## Auth Test Pattern

For pages requiring auth:
```typescript
test.describe.configure({ mode: 'serial' }); // auth state shared within describe

test.beforeEach(async ({ page }) => {
  // Authenticate via login POM
  const auth = new AuthPage(page);
  await auth.login(testUsers.valid.email, testUsers.valid.password);
});

test('{feature} — authenticated user', async ({ page }) => {
  // Test with authenticated session
});
```

## Test Naming Convention

- File: `{feature}-journey.spec.ts`
- Describe block: `{Feature Name} — User Journey`
- Test: `{action} {should} {expected result}` (e.g., "login form submits and redirects to dashboard")
- Mobile test: append `— mobile` to test name

## Happy Path Coverage

For each P0 journey, write tests for:
1. Page loads with correct elements (heading, subheading, CTAs)
2. User can complete the primary action (form submission, navigation)
3. On success: correct redirect or state change
4. On success: success message or state confirmation
5. Mobile layout is usable (no overflow, tap targets work)

Write all P0 happy path tests. Respond with count per journey.
```

### Stage 5 — Error Path Tests

```
Create error path tests for all critical forms and interactions.

## Journeys
{JOURNEY_MAP}

## Auth Pattern
{AUTH_PATTERN}

## Test Spec Pattern

For validation error paths:
```typescript
test('{form name} validation — required fields', async ({ page }) => {
  await page.goto('/{route}');
  await page.getByRole('button', { name: /submit|login|register/i }).click();
  // Assert validation errors appear
  await expect(page.getByText(/required|must be filled/i)).toBeVisible();
});

test('{form name} — wrong credentials', async ({ page }) => {
  await page.goto('/{route}');
  await page.getByLabel('Email').fill('wrong@email.com');
  await page.getByLabel('Password').fill('wrongpass');
  await page.getByRole('button', { name: /login/i }).click();
  // Assert error message
  await expect(page.getByText(/invalid|incorrect|wrong/i)).toBeVisible();
});

test('{form name} — invalid email format', async ({ page }) => {
  await page.goto('/{route}');
  await page.getByLabel('Email').fill('not-an-email');
  await page.getByRole('button', { name: /submit/i }).click();
  // Assert email validation error
});

test('{form name} — password too short', async ({ page }) => {
  await page.getByLabel('Password').fill('123');
  await page.getByRole('button', { name: /submit/i }).click();
  // Assert password min-length error
});
```

For network/API error paths:
```typescript
test('{action} — shows error on network failure', async ({ page }) => {
  // Intercept and fail API calls
  await page.route('**/api/**', route => route.abort());
  await page.getByRole('button', { name: /{action}/i }).click();
  await expect(page.getByText(/error|failed|try again/i)).toBeVisible();
});
```

## Error Path Coverage

For each P0/P1 form, write tests for:
1. Empty required field submission → validation error
2. Wrong credentials → auth error message (no sensitive data leaked)
3. Invalid email format → format error
4. Password too short → length error
5. Network failure → retry or error message
6. 404 on async action → not found error
7. 500 from API → friendly error (no stack trace exposed)

For auth flows specifically:
- Wrong password: error message, no account lockout hint
- Non-existent email: same error as wrong password (don't reveal which is wrong)
- Rate limiting: graceful backoff message

Write all error path tests. Respond with count.
```

### Stage 6 — Test Setup and Teardown

```
Create test data setup and teardown utilities.

## API Endpoints (for test data management)
{API_ENDPOINTS}

## Instructions

1. Create tests/e2e/helpers/setup.ts:

```typescript
import { request } from '@playwright/test';

/**
 * Setup utilities for test data lifecycle.
 * Uses API calls directly (bypassing UI) to create/cleanup test data.
 */

export async function createTestProject(apiBase: string, authToken: string, name: string) {
  const response = await request.post(`${apiBase}/projects`, {
    headers: { Authorization: `Bearer ${authToken}` },
    data: { name, description: 'E2E test project' },
  });
  return response.json();
}

export async function cleanupTestProject(apiBase: string, authToken: string, projectId: string) {
  await request.delete(`${apiBase}/projects/${projectId}`, {
    headers: { Authorization: `Bearer ${authToken}` },
  });
}

export async function getAuthToken(email: string, password: string, apiBase: string) {
  const response = await request.post(`${apiBase}/auth/login`, {
    data: { email, password },
  });
  const body = await response.json();
  return body.token;
}

export async function seedTestData(apiBase: string, token: string) {
  // Per-feature seed data creation using POST /api/... calls
  // Returns created entity IDs for use in tests
}

export async function cleanupAllTestData(apiBase: string, token: string, entityIds: string[]) {
  // Cleanup created entities in teardown
  for (const id of entityIds) {
    try {
      // delete based on entity type
    } catch (e) {
      // ignore cleanup errors
    }
  }
}
```

2. Add global setup/teardown to playwright.config.ts:
   - globalSetup: tests/e2e/helpers/global-setup.ts
   - globalTeardown: tests/e2e/helpers/global-teardown.ts

3. Create tests/e2e/helpers/global-setup.ts:
```typescript
import { chromium } from '@playwright/test';

export default async () => {
  // Setup: authenticate and get test session
  // Store test user session in a global file
  // Setup: ensure test database is clean
};

const browser = await chromium.launch();
const context = await browser.newContext();
const page = await context.newPage();

// Login with test credentials
await page.goto(process.env.BASE_URL + '/login');
await page.getByLabel('Email').fill(process.env.TEST_EMAIL);
await page.getByLabel('Password').fill(process.env.TEST_PASSWORD);
await page.getByRole('button', { name: /login/i }).click();
await page.waitForURL('**/dashboard*');

// Save storage state (cookies + localStorage) to reuse in tests
await context.storageState({ path: 'tests/e2e/.auth/user.json' });
await browser.close();
```

4. Create tests/e2e/helpers/global-teardown.ts:
```typescript
// Cleanup any test data created during the session
// Called after all tests complete
```

5. Reference auth state in test specs:
```typescript
test.use({ storageState: 'tests/e2e/.auth/user.json' });
```

Write: setup.ts, global-setup.ts, global-teardown.ts, update playwright.config.ts

Respond with summary of setup/teardown created.
```

### Stage 7 — CI Integration

```
Integrate Playwright tests into the existing GitHub Actions pipeline.

## Current Pipeline (from vercel-deploy.yml)
The pipeline already has:
- preview job: deploys to Vercel preview
- smoke-test job: runs scripts/deploy/smoke-test.sh (8 bash checks)
- promote job: promotes to production on main
- rollback job: triggers on smoke test failure

## New E2E Test Job

Add a new job after smoke-test that runs Playwright tests against the preview URL:

```yaml
  e2e-tests:
    name: E2E Tests (Playwright)
    needs: [preview, smoke-test]
    if: needs.smoke-test.outputs.smoke_passed == 'true'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium

      - name: Run E2E tests
        env:
          BASE_URL: ${{ needs.preview.outputs.preview_url }}
          TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
        run: npx playwright test --reporter=list

      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report-${{ github.run_id }}
          path: playwright-report/
          retention-days: 7

      - name: Upload test screenshots on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-screenshots-${{ github.run_id }}
          path: test-results/
          retention-days: 7
```

Update the promote job dependency to also require e2e-tests:
```yaml
  promote:
    needs: [preview, smoke-test, e2e-tests]  # <- add e2e-tests
    if: github.ref == 'refs/heads/main' && needs.smoke-test.outputs.smoke_passed == 'true' && needs.e2e-tests.outputs.e2e_passed == 'true'
```

Update the rollback job similarly.

Update smoke-test job to pass e2e_passed output to dependent jobs.

## Required Secrets (add to GitHub repo)

| Secret | Description |
|---|---|
| `TEST_EMAIL` | Test account email for E2E auth flows |
| `TEST_PASSWORD` | Test account password |

## Report Format

Update playwright.config.ts reporter:
```typescript
reporter: [
  ['list'],
  ['html', { outputFolder: 'playwright-report', open: 'never' }],
]
```

Make sure the test failure screenshots include full page state.

## Mobile Testing in CI

Run mobile tests in a separate job (not blocking promotion) because mobile emulators can be flaky in GitHub Actions runners:
```yaml
  e2e-tests-mobile:
    name: E2E Tests (Mobile)
    needs: [preview]
    if: always()  # Don't block promotion, just report
    runs-on: ubuntu-latest
    steps:
      # ... same setup ...
      - name: Run mobile E2E tests
        run: npx playwright test --project=chromium-mobile --reporter=list
```

Write updates to: .github/workflows/vercel-deploy.yml, playwright.config.ts

Respond with summary of CI changes.
```

---

## File Outputs

```
tests/e2e/
├── playwright.config.ts         # Playwright configuration
├── .env.example                  # Environment variable template
├── .auth/
│   └── .gitkeep                  # Auth state (generated by global-setup)
├── helpers/
│   ├── global-setup.ts           # Authenticate and save session
│   ├── global-teardown.ts        # Cleanup test data
│   └── setup.ts                  # Test data API helpers
├── pages/
│   ├── AuthPage.ts               # Login/logout POM
│   └── {PageName}Page.ts         # One POM per page
├── specs/
│   ├── {feature}-journey.spec.ts  # Happy path tests
│   └── {feature}-errors.spec.ts   # Error path tests
├── fixtures/
│   └── test-data.ts              # Test data constants
└── .gitignore                    # Ignore .auth, playwright-report, test-results
```

---

## Completion Criteria

The chain is complete when:
- [ ] `playwright.config.ts` exists and is valid TypeScript
- [ ] All pages have Page Object Models in tests/e2e/pages/
- [ ] All P0 journeys have happy path tests in tests/e2e/specs/
- [ ] All P0 forms have error path tests
- [ ] Global setup authenticates and persists session
- [ ] Test data setup/teardown utilities are functional
- [ ] `.github/workflows/vercel-deploy.yml` has E2E test job integrated
- [ ] GitHub Actions E2E job passes for the preview URL
- [ ] E2E test job failure does NOT trigger rollback (smoke tests still gate rollback)
- [ ] `npm run test:e2e` runs successfully in the frontend project
- [ ] Mobile tests run as non-blocking report (do not block promotion)
- [ ] Playwright HTML report is generated and archived as GitHub Actions artifact

---

## Error Handling Standards

For E2E tests:
- **Flaky tests**: Retry 2x in CI config (retries: 2)
- **Auth failures**: Use global setup with storageState — do not hardcode credentials in test files
- **Screenshot on failure**: `screenshot: { mode: 'only-on-failure' }` in test config
- **Video on failure**: `video: { mode: 'retain-on-failure' }` in test config
- **Trace on failure**: `trace: { mode: 'retain-on-failure' }` in test config
- **No hardcoded URLs**: All URLs from BASE_URL env var
- **No hardcoded credentials**: From TEST_EMAIL/TEST_PASSWORD env vars
- **Mobile viewport tests**: Use separate `chromium-mobile` project, non-blocking
- **Timeout handling**: 30s global, 10s for individual expects

---

## Integration with AIWA Pipeline

This suite runs after AIWA-20 (Vercel deployment automation):

```
Generate Frontend (AIWA-17)
       │
       ▼
Deploy to Vercel Preview (AIWA-20)
       │
       ├──────────────────────────┐
       ▼                          ▼
Smoke Tests (bash)          E2E Tests (Playwright)
  (8 checks, fast)            (journey tests, slower)
       │                          │
       └──────────┬───────────────┘
                  ▼
            Promote to Prod (main only)
```

The E2E suite does not block rollback — smoke tests remain the rollback gate. E2E test failures on main branch create an alert but do not roll back (human reviews E2E failures and decides on next action).

---

## Verification Commands

```bash
# Run E2E tests against a preview URL
BASE_URL=https://your-app.vercel.app npm run test:e2e

# Run with UI mode (headed browser)
npm run test:e2e:ui

# Run mobile tests only
npm run test:e2e:mobile

# Generate HTML report
npx playwright show-report

# Run with trace viewer
npx playwright test --trace on
```