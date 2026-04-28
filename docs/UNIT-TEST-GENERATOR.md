# Unit Test Generator — Claude Code Prompt Chain
## AIWA-28 | Comprehensive Unit Test Generator for Frontend/Backend Modules

**Status:** Draft v1.0
**Date:** 2026-04-28
**Scope:** Given a frontend or backend module → production-ready Jest/Vitest test suite with >80% code coverage

---

## Overview

This prompt chain is invoked by a Claude Code agent worker after frontend or backend generation is complete. The chain runs in three sequential steps:

1. **Analyze** — Inspect the generated module, identify all exported functions, and map dependencies
2. **Scaffold** — Bootstrap test files and mocking infrastructure per project structure
3. **Generate** — Write comprehensive tests for all exports with edge case coverage

Output is a complete test suite integrated into the project's `tests/` directory, targeting >80% code coverage.

---

## Invoker Context

The Control Plane passes this context to the agent worker at task dispatch:

```json
{
  "task_id": "<uuid>",
  "project_id": "<uuid>",
  "repo_url": "https://github.com/<org>/<repo>",
  "module_type": "frontend" | "backend",
  "module_path": "frontend/src/" | "backend/src/",
  "framework": "jest" | "vitest",
  "coverage_target": 80,
  "generation_artifacts": {
    "frontend_path": "frontend/",
    "components": [ ... list of component paths ... ],
    "hooks": [ ... list of hook paths ... ],
    "services": [ ... list of service paths ... ],
    "utils": [ ... list of utility paths ... ]
  },
  "mocked_dependencies": {
    "api_client": "src/lib/api.ts",
    "state_store": "src/lib/store.ts",
    "external_services": [ ... ]
  }
}
```

---

## Step 1: Analyze Module

### Prompt

```
You are analyzing a generated module to prepare for comprehensive test generation.

## Project Context
- Project ID: {project_id}
- Repo: {repo_url}
- Module type: {module_type}
- Module path: {module_path}
- Test framework: {framework}

## Generation Artifacts
{insert generation artifacts from frontend/backend generation here}

## Mocked Dependencies
{insert mocked dependencies here}

## Instructions
1. Clone the repo at {repo_url} and checkout the branch with generated code
2. Scan {module_path} recursively to find all exported modules:
   - Frontend: components, hooks, lib utilities, API clients
   - Backend: routes, controllers, services, models, middleware, utils
3. For each exported module, identify:
   - All exported functions and classes
   - Function signatures (params, return types)
   - Internal dependencies (other local modules)
   - External dependencies (npm packages, HTTP calls, DB calls)
   - Side effects (logging, state mutation, async operations)
4. Build a dependency graph mapping:
   - Which modules depend on which
   - Which modules call external APIs or databases
   - Which modules have async logic requiring proper mocking
5. Identify test categories needed:
   - Pure utility functions → simple unit tests
   - Component render tests → React Testing Library
   - Hook tests → @testing-library/react-hooks
   - API integration → mocked HTTP (msw or jest.mock)
   - Business logic → mocked service dependencies
   - Middleware → unit tests with mocked req/res/next
6. Create a test plan file at `tests/.test-plan.json`:
   ```json
   {
     "modules": [ ... ],
     "coverage_target": {coverage_target},
     "framework": "{framework}",
     "estimated_tests": N
   }
   ```
7. Report the module map with dependency graph to the agent.

Respond with a summary of: number of modules, number of exports, dependency categories, and test categories identified.
```

### Deliverable
- `tests/.test-plan.json` with module map and test plan committed and pushed

---

## Step 2: Scaffold Test Infrastructure

### Prompt

```
You are scaffolding the test infrastructure for a project. The module analysis is complete.

## Project Context
- Project ID: {project_id}
- Repo: {repo_url}
- Module type: {module_type}
- Framework: {framework}

## Module Map
{insert the module map from Step 1 here}

## Mocked Dependencies
{insert mocked dependencies here}

## Instructions
1. Configure {framework} in the project if not already set up:
   - **Jest**: Ensure jest.config.js exists with:
     ```js
     module.exports = {
       preset: 'ts-jest',
       testEnvironment: 'node', // or 'jsdom' for frontend
       coverageDirectory: 'coverage',
       collectCoverageFrom: [
         '{module_path}/**/*.{ts,tsx}',
         '!{module_path}/**/*.d.ts',
         '!{module_path}/**/index.{ts,tsx}'
       ],
       coverageThreshold: {
         global: { branches: {coverage_target}, functions: {coverage_target}, lines: {coverage_target}, statements: {coverage_target} }
       },
       moduleNameMapper: {
         '^@/(.*)$': '<rootDir>/src/$1'
       }
     }
     ```
   - **Vitest**: Ensure vitest.config.ts exists with equivalent config
2. Create test setup files:
   - `tests/setup.ts` — global test configuration
   - `tests/teardown.ts` — cleanup after each test
3. Create mocking infrastructure:
   - `tests/mocks/` directory
   - `tests/mocks/api.ts` — mock API client factory
   - `tests/mocks/store.ts` — mock state store (Zustand/Jotai/Redux)
   - `tests/mocks/handlers.ts` — MSW request handlers for API mocking
   - `tests/mocks/db.ts` — mock database layer for backend tests
   - `tests/mocks/external.ts` — mock external service calls
4. Create test utility helpers:
   - `tests/utils.ts`:
     - `renderWithProviders()` — wrap components with needed providers
     - `mockRouter()` — mock Next.js / React Router
     - `createMockReq()` / `createMockRes()` — for middleware tests
     - `waitFor()` helpers for async assertions
     - `fireEvent` from RTL for component interactions
5. Configure MSW (Mock Service Worker) for API mocking:
   - `tests/mocks/server.ts` — set up msw server
   - Browser: `setupServer()` with request handlers
   - Node: `setupServer()` for backend tests
6. Ensure {module_path} has proper TypeScript types for all interfaces — generate missing type exports if needed
7. Install any missing test dependencies:
   - Frontend: @testing-library/react, @testing-library/user-event, @testing-library/jest-dom, msw
   - Backend: jest, supertest, msw, @types/jest
8. Create `tests/.coverageignore` to exclude non-testable files (types, configs, entry points)
9. Commit and push

Respond with a summary of test infrastructure created.
```

### Deliverable
- Test configuration, mocks directory, utilities, and MSW server committed and pushed

---

## Step 3: Generate Tests

### Prompt

```
You are generating comprehensive unit tests for all modules. Test infrastructure is scaffolded.

## Project Context
- Project ID: {project_id}
- Repo: {repo_url}
- Module type: {module_type}
- Framework: {framework}
- Coverage target: {coverage_target}%

## Module Map
{insert module map from Step 1 here}

## Test Infrastructure
Scaffolded at: tests/mocks/, tests/utils.ts, tests/setup.ts

## Instructions

For each module in the dependency order (start with leaf/utility modules, build up):

### 3.1 Pure Utility Functions
Test file: `tests/unit/{module_path}/utils.test.ts`
```typescript
import { functionName } from '{module_path}/utils';

describe('functionName', () => {
  describe('happy path', () => {
    it('returns expected output for valid input', () => {
      const result = functionName(validInput);
      expect(result).toBe(expectedOutput);
    });
  });

  describe('edge cases', () => {
    it('handles empty input', () => { ... });
    it('handles boundary values', () => { ... });
    it('handles null/undefined inputs gracefully', () => { ... });
    it('throws descriptive error for invalid input', () => { ... });
  });
});
```

### 3.2 Frontend Components (React)
Test file: `tests/unit/components/{ComponentName}.test.tsx`
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComponentName } from '@/components/{ComponentName}';

describe('ComponentName', () => {
  const defaultProps = { ... };

  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<ComponentName {...defaultProps} />);
      expect(screen.getByRole('...')).toBeInTheDocument();
    });
    it('displays correct initial state', () => { ... });
    it('shows loading state while fetching', () => { ... });
  });

  describe('user interactions', () => {
    it('calls onSubmit with correct values when form is submitted', async () => {
      const user = userEvent.setup();
      render(<ComponentName {...defaultProps} />);
      await user.click(screen.getByRole('button', { name: /submit/i }));
      expect(defaultProps.onSubmit).toHaveBeenCalledWith(expectedValues);
    });
  });

  describe('error states', () => {
    it('displays error message on validation failure', () => { ... });
    it('shows empty state when no data', () => { ... });
  });
});
```

### 3.3 Frontend Hooks
Test file: `tests/unit/hooks/{useHookName}.test.ts`
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useHookName } from '@/hooks/{useHookName}';

describe('useHookName', () => {
  it('returns initial state', () => { ... });
  it('fetches data on mount', async () => {
    server.use(
      rest.get('/api/endpoint', (req, res, ctx) => {
        return res(ctx.json(mockData));
      })
    );
    const { result } = renderHook(() => useHookName());
    await waitFor(() => expect(result.current.data).toEqual(mockData));
  });
  it('handles error state', async () => { ... });
  it('handles loading state', () => { ... });
});
```

### 3.4 Backend Services
Test file: `tests/unit/services/{serviceName}.test.ts`
```typescript
import { serviceName } from '{module_path}/services/{serviceName}';
import { mockDb } from '@/tests/mocks/db';

jest.mock('{module_path}/models', () => mockDb);

describe('serviceName', () => {
  describe('create', () => {
    it('creates a new record and returns it', async () => {
      const result = await serviceName.create(validInput);
      expect(result).toMatchObject({ id: expect.any(String), ... });
    });
    it('throws ValidationError for invalid input', async () => { ... });
    it('returns 404 when resource not found', async () => { ... });
  });
});
```

### 3.5 Backend Middleware
Test file: `tests/unit/middleware/{middlewareName}.test.ts`
```typescript
import { middlewareName } from '{module_path}/middleware/{middlewareName}';
import { createMockReq, createMockRes, createMockNext } from '@/tests/utils';

describe('middlewareName', () => {
  it('calls next() on valid request', () => {
    const req = createMockReq({ headers: { authorization: 'Bearer valid-token' } });
    const res = createMockRes();
    const next = createMockNext();
    middlewareName(req, res, next);
    expect(next).toHaveBeenCalled();
  });
  it('returns 401 when token is missing', () => { ... });
  it('returns 403 when user lacks permission', () => { ... });
});
```

### 3.6 Backend Routes/Controllers
Test file: `tests/integration/{routeName}.test.ts`
```typescript
import request from 'supertest';
import { app } from '{module_path}/app';

describe('POST /api/resource', () => {
  it('returns 201 with created resource on valid input', async () => {
    const res = await request(app)
      .post('/api/resource')
      .send(validPayload);
    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ id: expect.any(String) });
  });
  it('returns 400 with validation errors on invalid input', async () => { ... });
  it('returns 401 without auth token', async () => { ... });
});
```

### Coverage Requirements
- Every exported function must have at least one test
- Cover: happy path, edge cases, error paths, boundary conditions
- Mock ALL external dependencies (API calls, DB operations, file system)
- Use dependency injection patterns where possible to enable clean mocking
- For branches: if/else, switch/case, try/catch all need coverage
- For async: success and failure paths for every async call
- Run `npm run test -- --coverage` after generation and verify:
  - Overall coverage >= {coverage_target}%
  - Every module has >= {coverage_target}% coverage
  - No untested files in coverage report

### Cleanup
- Remove all `console.log`, `console.error` from source files before testing
- Ensure no `.skip` or `.only` remain in test files
- All mocks must be reset between tests (beforeEach cleanup)

### Completion
After all tests are generated and passing, commit and push. Then report coverage metrics.

Respond with: test file count, total test count, coverage percentage per module, and any modules below target requiring attention.
```

### Deliverable
- Comprehensive test suite with >{coverage_target}% coverage committed and pushed

---

## Completion

After all three steps, call the Control Plane webhook to report completion:

```
POST /agent/task/{task_id}/complete
{
  "status": "success",
  "artifacts": {
    "test_files": [ ... list of test files created ... ],
    "total_tests": N,
    "coverage": {
      "overall": "XX%",
      "by_module": { ... }
    },
    "framework": "{framework}",
    "framework_config": "jest.config.js | vitest.config.ts"
  }
}
```

If coverage target is not met, report with:
```
{
  "status": "partial",
  "coverage": "XX%",
  "below_target": [ ... modules below {coverage_target}% ... ],
  "suggestion": "Manual review needed for [modules]"
}
```

If any step fails, call:
```
POST /agent/task/{task_id}/fail
{ "error": "...", "step": "step-3" }
```

---

## Verification Checklist

Before reporting completion, verify:
- [ ] `npm run test` passes with zero failures
- [ ] Coverage report shows >= {coverage_target}% overall
- [ ] No modules below coverage threshold
- [ ] All exported functions have at least one test
- [ ] All mock setup/teardown properly isolated per test
- [ ] No flaky tests (no random failures on repeated runs)
- [ ] TypeScript compilation succeeds on test files
- [ ] No `console.log` / `console.error` remaining in source
- [ ] No `.only` or `.skip` blocks left in tests
- [ ] All changes pushed to {repo_url}
- [ ] CI pipeline (GitHub Actions) passes on the test branch

---

## Notes

- Run test generation AFTER frontend/backend generation completes, not in parallel — the module structure must be stable
- Coverage target of {coverage_target}% applies per-module, not just overall — a module at 79% is a failure
- For frontend components: prefer userEvent over fireEvent for realistic interaction simulation
- For backend services: mock at the database/ORM level, not the controller level — test services in isolation
- MSW (Mock Service Worker) is preferred over jest.mock for HTTP calls because it enables integration tests against a fake server
- If a module is difficult to test (e.g., heavy DOM dependencies), create a thin wrapper that can be tested separately
- Minimax M2.7 or Claude Opus recommended for test generation — Sonnet is insufficient for edge case coverage
- Test execution order: utils → hooks → services → middleware → controllers → components (follow dependency graph)