import { test, expect } from '@playwright/test';
import { testUsers } from '../fixtures/test-data';

test.describe('Authentication — User Journey', () => {
  test.describe.configure({ mode: 'serial' });

  test('login page loads with all elements', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: /login|sign in/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /login|sign in/i })).toBeVisible();
  });

  test('login with valid credentials redirects to dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(testUsers.valid.email);
    await page.getByLabel(/password/i).fill(testUsers.valid.password);
    await page.getByRole('button', { name: /login|sign in/i }).click();
    await page.waitForURL(/dashboard|home|projects/, { timeout: 15_000 });
  });

  test('login shows error on wrong password', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(testUsers.invalid.wrongPassword.email);
    await page.getByLabel(/password/i).fill(testUsers.invalid.wrongPassword.password);
    await page.getByRole('button', { name: /login|sign in/i }).click();
    await expect(page.locator('[role="alert"], .error')).toBeVisible();
  });

  test('login validation — missing email', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/password/i).fill(testUsers.valid.password);
    await page.getByRole('button', { name: /login|sign in/i }).click();
    await expect(page.getByText(/required|email/i)).toBeVisible();
  });

  test('login validation — missing password', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(testUsers.valid.email);
    await page.getByRole('button', { name: /login|sign in/i }).click();
    await expect(page.getByText(/required|password/i)).toBeVisible();
  });

  test('login validation — invalid email format', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('not-an-email');
    await page.getByLabel(/password/i).fill(testUsers.valid.password);
    await page.getByRole('button', { name: /login|sign in/i }).click();
    await expect(page.getByText(/email|valid/i)).toBeVisible();
  });

  test('login — mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: /login|sign in/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
  });

  test('register page loads with all elements', async ({ page }) => {
    await page.goto('/register');
    await expect(page.getByRole('heading', { name: /register|sign up|create/i })).toBeVisible();
    await expect(page.getByLabel(/name/i)).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
  });

  test('register validation — required fields', async ({ page }) => {
    await page.goto('/register');
    await page.getByRole('button', { name: /register|sign up|create/i }).click();
    await expect(page.getByText(/required|fill in|all fields/i)).toBeVisible();
  });

  test('register validation — password too short', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/name/i).fill('Test User');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill(testUsers.edge.shortPassword);
    await page.getByRole('button', { name: /register|sign up|create/i }).click();
    await expect(page.getByText(/password.*short|min.*8|at least/i)).toBeVisible();
  });
});