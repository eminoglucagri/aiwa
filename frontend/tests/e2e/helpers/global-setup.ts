import { chromium } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const authStatePath = path.join(__dirname, '..', '.auth', 'user.json');

export default async function globalSetup() {
  const baseURL = process.env.BASE_URL || 'http://localhost:3000';
  const email = process.env.TEST_EMAIL || 'test@example.com';
  const password = process.env.TEST_PASSWORD || 'testpass123';

  const browser = await chromium.launch();
  const context = await browser.newContext({ baseURL });
  const page = await context.newPage();

  try {
    await page.goto(`${baseURL}/login`);

    const emailInput = page.getByLabel(/email/i);
    const passwordInput = page.getByLabel(/password/i);
    const submitButton = page.getByRole('button', { name: /login|sign in/i });

    if (await emailInput.isVisible({ timeout: 5000 })) {
      await emailInput.fill(email);
      await passwordInput.fill(password);
      await submitButton.click();
      await page.waitForURL(/dashboard|home|projects/, { timeout: 15_000 });
    }

    const authDir = path.dirname(authStatePath);
    if (!fs.existsSync(authDir)) {
      fs.mkdirSync(authDir, { recursive: true });
    }

    await context.storageState({ path: authStatePath });
  } finally {
    await browser.close();
  }
}