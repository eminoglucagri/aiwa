import { APIRequestContext } from '@playwright/test';

export async function getAuthToken(
  apiBase: string,
  email: string,
  password: string
): Promise<{ token: string; userId: string }> {
  const request = globalThis as { __apiRequest?: APIRequestContext };
  const api = request.__apiRequest || (await import('@playwright/test')).request;

  const response = await api.post(`${apiBase}/auth/login`, {
    data: { email, password },
  });

  if (!response.ok()) {
    throw new Error(`Auth failed: ${response.status()} ${await response.text()}`);
  }

  const body = await response.json();
  return { token: body.access_token || body.token, userId: body.user_id || body.id };
}

export async function createTestProject(
  apiBase: string,
  token: string,
  name: string,
  description = 'E2E test project'
): Promise<{ id: string }> {
  const request = globalThis as { __apiRequest?: APIRequestContext };
  const api = request.__apiRequest || (await import('@playwright/test')).request;

  const response = await api.post(`${apiBase}/projects`, {
    headers: { Authorization: `Bearer ${token}` },
    data: { name, description },
  });

  if (!response.ok()) {
    throw new Error(`Failed to create project: ${response.status()} ${await response.text()}`);
  }

  const body = await response.json();
  return { id: body.id || body.project_id };
}

export async function cleanupTestProject(apiBase: string, token: string, projectId: string): Promise<void> {
  const request = globalThis as { __apiRequest?: APIRequestContext };
  const api = request.__apiRequest || (await import('@playwright/test')).request;

  await api.delete(`${apiBase}/projects/${projectId}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => {});
}

export async function waitForDeployment(apiBase: string, projectId: string, timeoutMs = 120_000): Promise<string> {
  const request = globalThis as { __apiRequest?: APIRequestContext };
  const api = request.__apiRequest || (await import('@playwright/test')).request;

  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const response = await api.get(`${apiBase}/projects/${projectId}`, {
      headers: { Authorization: `Bearer ${process.env.API_TOKEN || ''}` },
    });

    if (response.ok()) {
      const body = await response.json();
      if (body.deployment_url || body.preview_url) {
        return body.deployment_url || body.preview_url;
      }
      if (body.status === 'deployed' || body.status === 'ready') {
        return body.deployment_url || body.preview_url || '';
      }
    }

    await new Promise(resolve => setTimeout(resolve, 5000));
  }

  throw new Error(`Deployment timeout after ${timeoutMs}ms`);
}

export function generateTestEmail(): string {
  return `e2e-${Date.now()}-${Math.random().toString(36).slice(2)}@test.aiwa.dev`;
}

export function generateTestProjectName(): string {
  return `e2e-project-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}