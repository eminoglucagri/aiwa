import { test as base, Page, Locator, expect, APIRequestContext } from '@playwright/test';

export class AuthPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly registerLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: /login|sign in/i });
    this.emailInput = page.getByLabel(/email/i);
    this.passwordInput = page.getByLabel(/password/i);
    this.submitButton = page.getByRole('button', { name: /login|sign in|submit/i });
    this.errorMessage = page.locator('[role="alert"], .error, [data-testid="error"]');
    this.registerLink = page.getByRole('link', { name: /register|sign up|create account/i });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async expectLoaded() {
    await expect(this.heading).toBeVisible();
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectErrorVisible() {
    await expect(this.errorMessage).toBeVisible();
  }
}

export class DashboardPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly createProjectButton: Locator;
  readonly projectList: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: /dashboard/i });
    this.createProjectButton = page.getByRole('button', { name: /create|new project/i });
    this.projectList = page.locator('[data-testid="project-list"], .project-list, section ul');
  }

  async goto() {
    await this.page.goto('/dashboard');
  }

  async expectLoaded() {
    await expect(this.heading).toBeVisible();
  }
}

export class RegisterPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly nameInput: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly loginLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: /register|sign up|create/i });
    this.nameInput = page.getByLabel(/name/i);
    this.emailInput = page.getByLabel(/email/i);
    this.passwordInput = page.getByLabel(/password/i);
    this.confirmPasswordInput = page.getByLabel(/confirm.*password|password.*confirm/i);
    this.submitButton = page.getByRole('button', { name: /register|sign up|create/i });
    this.errorMessage = page.locator('[role="alert"], .error');
    this.loginLink = page.getByRole('link', { name: /login|sign in/i });
  }

  async goto() {
    await this.page.goto('/register');
  }

  async expectLoaded() {
    await expect(this.heading).toBeVisible();
  }

  async register(name: string, email: string, password: string) {
    await this.nameInput.fill(name);
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    if (await this.confirmPasswordInput.isVisible()) {
      await this.confirmPasswordInput.fill(password);
    }
    await this.submitButton.click();
  }
}

export const test = base.extend<{ authenticatedPage: Page }>({
  authenticatedPage: async ({ browser, baseURL }, use) => {
    const context = await browser.newContext({ baseURL });
    const page = await context.newPage();

    const email = process.env.TEST_EMAIL || 'test@example.com';
    const password = process.env.TEST_PASSWORD || 'testpass123';

    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /login|sign in/i }).click();
    await page.waitForURL(/dashboard|home/, { timeout: 15_000 });

    await use(page);
    await context.close();
  },
});

export { expect };