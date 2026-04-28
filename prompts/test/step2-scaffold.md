# Unit Test Generator — Step 2: Scaffold Test Infrastructure
## AIWA-28 | Unit Test Generation Prompt Chain

**Step:** 2 of 3
**Purpose:** Bootstrap test configuration, mocking infrastructure, and utilities

---

## Context Passed by Control Plane

```json
{
  "task_id": "<uuid>",
  "project_id": "<uuid>",
  "repo_url": "https://github.com/<org>/<repo>",
  "module_type": "frontend" | "backend",
  "framework": "{framework}",
  "module_path": "frontend/src/" | "backend/src/",
  "coverage_target": {coverage_target}
}
```

---

## Prompt

You are scaffolding the test infrastructure for a project. The module analysis is complete.

## Project Context
- Project ID: {project_id}
- Repo: {repo_url}
- Module type: {module_type}
- Framework: {framework}
- Module path: {module_path}
- Coverage target: {coverage_target}%

## Instructions

### 1. Configure {framework}

If not already present, create the configuration:

**Jest** — `jest.config.js`:
```js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom', // or 'node' for backend
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    '{module_path}/**/*.{ts,tsx}',
    '!{module_path}/**/*.d.ts',
    '!{module_path}/**/index.{ts,tsx}'
  ],
  coverageThreshold: {
    global: {
      branches: {coverage_target},
      functions: {coverage_target},
      lines: {coverage_target},
      statements: {coverage_target}
    }
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  testPathIgnorePatterns: ['/node_modules/', '/coverage/'],
  clearMocks: true,
  restoreMocks: true
}
```

**Vitest** — `vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: { branches: {coverage_target}, functions: {coverage_target}, lines: {coverage_target}, statements: {coverage_target} }
    }
  }
});
```

### 2. Create Test Setup Files

**`tests/setup.ts`** — global configuration:
```typescript
// jest setup or vitest setup
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Reset all mocks after each test
afterEach(() => {
  jest.clearAllMocks();
  server.resetHandlers();
});

// Set up MSW server for API mocking
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterAll(() => server.close());
```

**`tests/teardown.ts`** — cleanup:
```typescript
// Run after all tests
jest.clearAllMocks();
server.close();
```

### 3. Create Mocking Infrastructure

**`tests/mocks/api.ts`** — mock API client factory:
```typescript
import { rest } from 'msw';

export const createMockApiClient = (overrides = {}) => ({
  get: jest.fn().mockResolvedValue({ data: {} }),
  post: jest.fn().mockResolvedValue({ data: {} }),
  put: jest.fn().mockResolvedValue({ data: {} }),
  delete: jest.fn().mockResolvedValue({ data: {} }),
  ...overrides,
});
```

**`tests/mocks/store.ts`** — mock state store:
```typescript
// For Zustand/Jotai/Redux stores
export const createMockStore = (initialState = {}) => ({
  getState: () => initialState,
  setState: (state) => Object.assign(initialState, state),
  subscribe: jest.fn(),
  destroy: jest.fn(),
});
```

**`tests/mocks/handlers.ts`** — MSW request handlers:
```typescript
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/endpoint', (req, res, ctx) => {
    return res(ctx.json({ id: '1', name: 'Test' }));
  }),
  rest.post('/api/endpoint', (req, res, ctx) => {
    return res(ctx.status(201), ctx.json({ id: '1', ...req.body }));
  }),
  // Add more handlers as needed per feature
];

export const errorHandlers = [
  rest.get('/api/endpoint', (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({ error: 'Server error' }));
  }),
];
```

**`tests/mocks/server.ts`** — MSW server setup:
```typescript
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

**`tests/mocks/db.ts`** — mock database layer:
```typescript
// For backend tests
const mockDb = {
  users: {
    findMany: jest.fn().mockResolvedValue([]),
    findUnique: jest.fn().mockResolvedValue(null),
    create: jest.fn().mockResolvedValue({ id: '1' }),
    update: jest.fn().mockResolvedValue({ id: '1' }),
    delete: jest.fn().mockResolvedValue({ id: '1' }),
  },
  // Add all model collections
};

export { mockDb };
```

**`tests/mocks/external.ts`** — mock external services:
```typescript
// Mock third-party services (Stripe, SendGrid, etc.)
export const mockStripe = {
  customers: {
    create: jest.fn().mockResolvedValue({ id: 'cus_test' }),
  },
};

export const mockEmailService = {
  send: jest.fn().mockResolvedValue(true),
};
```

### 4. Create Test Utilities

**`tests/utils.ts`** — helper functions:
```typescript
// React Testing Library helpers
export const renderWithProviders = (ui: React.ReactElement, { route = '/' } = {}) => {
  // Wrap component with providers (QueryClient, Auth context, etc.)
  // Return rendered container and helpers
};

// Router mock
export const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  back: jest.fn(),
};

// Express mocks for middleware tests
export const createMockReq = (options = {}) => ({
  headers: {},
  body: {},
  params: {},
  query: {},
  user: null,
  ...options,
});

export const createMockRes = () => {
  const res: any = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  res.send = jest.fn().mockReturnValue(res);
  res.set = jest.fn().mockReturnValue(res);
  res.cookie = jest.fn().mockReturnValue(res);
  return res;
};

export const createMockNext = () => jest.fn();

// Async wait helpers
export { waitFor, act } from '@testing-library/react';
```

### 5. Install Missing Dependencies

Ensure these are in package.json:
- **Frontend**: @testing-library/react, @testing-library/user-event, @testing-library/jest-dom, msw, jest-environment-jsdom
- **Backend**: jest, supertest, msw, @types/jest, jest-environment-node

Install with: `npm install --save-dev <package>` (or add to devDependencies)

### 6. Coverage Ignore

Create `tests/.coverageignore`:
```
**/node_modules/**
**/types/**
**/*.d.ts
**/index.ts
setup.ts
teardown.ts
mocks/**
utils.ts
```

### 7. TypeScript Types

Ensure all modules have proper TypeScript interface exports so tests can import types cleanly.

## Output

Respond with a summary of test infrastructure created: configuration files, mock modules, utility helpers.

### Deliverable
Test configuration, mocks directory, utilities, and MSW server committed and pushed