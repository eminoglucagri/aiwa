# Unit Test Generator — Step 3: Generate Tests
## AIWA-28 | Unit Test Generation Prompt Chain

**Step:** 3 of 3
**Purpose:** Write comprehensive tests for all exports with >80% coverage

---

## Context Passed by Control Plane

```json
{
  "task_id": "<uuid>",
  "project_id": "<uuid>",
  "repo_url": "https://github.com/<org>/<repo>",
  "module_type": "frontend" | "backend",
  "framework": "jest" | "vitest",
  "module_path": "frontend/src/" | "backend/src/",
  "coverage_target": 80
}
```

---

## Prompt

You are generating comprehensive unit tests for all modules. Test infrastructure is scaffolded in `tests/`.

## Project Context
- Project ID: {project_id}
- Repo: {repo_url}
- Module type: {module_type}
- Framework: {framework}
- Coverage target: {coverage_target}%
- Module path: {module_path}

## Test Infrastructure
Available at:
- `tests/mocks/api.ts` — API client mock factory
- `tests/mocks/store.ts` — state store mock
- `tests/mocks/handlers.ts` — MSW request handlers
- `tests/mocks/server.ts` — MSW server
- `tests/mocks/db.ts` — database mock
- `tests/mocks/external.ts` — external service mocks
- `tests/utils.ts` — render helpers, mock req/res/next

## Coverage Target
- Overall: >= {coverage_target}%
- Per-module: >= {coverage_target}% (no module below threshold)
- Every exported function: at least one test
- All branches, async paths, and error paths covered

---

## Test Generation by Category

Follow the dependency graph order: **utils → hooks → services → middleware → controllers → components**

---

### 3.1 Pure Utility Functions

**Test file:** `tests/unit/{module_path}/{feature}/utils.test.ts`

```typescript
import { functionName } from '{module_path}/{feature}/utils';

describe('functionName', () => {
  describe('happy path', () => {
    it('returns expected output for valid input', () => {
      const result = functionName(validInput);
      expect(result).toBe(expectedOutput);
    });
  });

  describe('edge cases', () => {
    it('handles empty input', () => {
      expect(functionName('')).toBe(expected);
    });
    it('handles boundary values', () => {
      expect(functionName(boundaryValue)).toBe(expected);
    });
    it('handles null/undefined inputs gracefully', () => {
      expect(() => functionName(null)).not.toThrow();
      expect(() => functionName(undefined)).not.toThrow();
    });
    it('throws descriptive error for invalid input', () => {
      expect(() => functionName(invalidInput)).toThrow(DescriptiveErrorName);
    });
  });

  describe('async variants', () => {
    it('resolves with correct data on success', async () => {
      const result = await asyncFunction(validInput);
      expect(result).toEqual(expectedData);
    });
    it('rejects with error on failure', async () => {
      await expect(asyncFunction(invalidInput)).rejects.toThrow(ErrorType);
    });
  });
});
```

---

### 3.2 Frontend Components (React)

**Test file:** `tests/unit/components/{ComponentName}.test.tsx`

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComponentName } from '@/components/{ComponentName}';

describe('ComponentName', () => {
  const defaultProps = {
    onSubmit: jest.fn(),
    onCancel: jest.fn(),
    isLoading: false,
    initialValues: {},
  };

  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<ComponentName {...defaultProps} />);
      expect(screen.getByRole('...')).toBeInTheDocument();
    });
    it('displays correct initial state', () => {
      render(<ComponentName {...defaultProps} />);
      expect(screen.getByText('...')).toBeInTheDocument();
    });
    it('shows loading state while fetching', () => {
      render(<ComponentName {...defaultProps} isLoading={true} />);
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });

  describe('user interactions', () => {
    it('calls onSubmit with correct values when form is submitted', async () => {
      const user = userEvent.setup();
      render(<ComponentName {...defaultProps} />);
      await user.click(screen.getByRole('button', { name: /submit/i }));
      expect(defaultProps.onSubmit).toHaveBeenCalledWith(expectedValues);
    });
    it('calls onCancel when cancel button is clicked', async () => {
      const user = userEvent.setup();
      render(<ComponentName {...defaultProps} />);
      await user.click(screen.getByRole('button', { name: /cancel/i }));
      expect(defaultProps.onCancel).toHaveBeenCalled();
    });
  });

  describe('error states', () => {
    it('displays error message on validation failure', () => {
      render(<ComponentName {...defaultProps} error="Validation failed" />);
      expect(screen.getByText('Validation failed')).toBeInTheDocument();
    });
    it('shows empty state when no data', () => {
      render(<ComponentName {...defaultProps} data={[]} />);
      expect(screen.getByText(/no items found/i)).toBeInTheDocument();
    });
  });
});
```

**Coverage requirements for components:**
- Render with null props
- Render with all prop states (loading, error, empty, success)
- Every button/link click handler
- Every form input interaction
- Conditional rendering branches
- useEffect cleanup and dependencies

---

### 3.3 Frontend Hooks

**Test file:** `tests/unit/hooks/{useHookName}.test.ts`

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useHookName } from '@/hooks/{useHookName}';
import { server } from '@/tests/mocks/server';
import { rest } from 'msw';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: any) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useHookName', () => {
  it('returns initial state', () => {
    const { result } = renderHook(() => useHookName(), { wrapper: createWrapper() });
    expect(result.current.isLoading).toBe(false);
  });

  it('fetches data on mount', async () => {
    server.use(
      rest.get('/api/endpoint', (req, res, ctx) => {
        return res(ctx.json({ data: mockData }));
      })
    );
    const { result } = renderHook(() => useHookName(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.data).toEqual(mockData));
  });

  it('handles error state', async () => {
    server.use(
      rest.get('/api/endpoint', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );
    const { result } = renderHook(() => useHookName(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
```

---

### 3.4 Backend Services

**Test file:** `tests/unit/services/{serviceName}.test.ts`

```typescript
import { serviceName } from '{module_path}/services/{serviceName}';
import { mockDb } from '@/tests/mocks/db';

jest.mock('{module_path}/models', () => mockDb);

describe('serviceName', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('create', () => {
    it('creates a new record and returns it', async () => {
      mockDb.resource.create.mockResolvedValue({ id: '1', ...validInput });
      const result = await serviceName.create(validInput);
      expect(result).toMatchObject({ id: expect.any(String) });
      expect(mockDb.resource.create).toHaveBeenCalledWith({ data: validInput });
    });

    it('throws ValidationError for invalid input', async () => {
      mockDb.resource.create.mockRejectedValue(new Error('Validation failed'));
      await expect(serviceName.create(invalidInput)).rejects.toThrow();
    });
  });

  describe('findById', () => {
    it('returns the resource when found', async () => {
      mockDb.resource.findUnique.mockResolvedValue(mockResource);
      const result = await serviceName.findById('1');
      expect(result).toEqual(mockResource);
    });

    it('returns null when resource not found', async () => {
      mockDb.resource.findUnique.mockResolvedValue(null);
      const result = await serviceName.findById('999');
      expect(result).toBeNull();
    });
  });
});
```

---

### 3.5 Backend Middleware

**Test file:** `tests/unit/middleware/{middlewareName}.test.ts`

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

  it('returns 401 when token is missing', () => {
    const req = createMockReq({ headers: {} });
    const res = createMockRes();
    const next = createMockNext();
    middlewareName(req, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  it('returns 403 when user lacks permission', () => {
    const req = createMockReq({ headers: { authorization: 'Bearer token' }, user: { role: 'guest' } });
    const res = createMockRes();
    const next = createMockNext();
    middlewareName(req, res, next);
    expect(res.status).toHaveBeenCalledWith(403);
    expect(next).not.toHaveBeenCalled();
  });
});
```

---

### 3.6 Backend Routes/Controllers (Integration)

**Test file:** `tests/integration/{routeName}.test.ts`

```typescript
import request from 'supertest';
import { app } from '{module_path}/app';

describe('POST /api/resource', () => {
  it('returns 201 with created resource on valid input', async () => {
    const res = await request(app)
      .post('/api/resource')
      .send(validPayload)
      .set('Authorization', 'Bearer valid-token');
    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ id: expect.any(String) });
  });

  it('returns 400 with validation errors on invalid input', async () => {
    const res = await request(app)
      .post('/api/resource')
      .send(invalidPayload);
    expect(res.status).toBe(400);
    expect(res.body.error).toBeDefined();
  });

  it('returns 401 without auth token', async () => {
    const res = await request(app)
      .post('/api/resource')
      .send(validPayload);
    expect(res.status).toBe(401);
  });
});
```

---

## Test Execution and Coverage

After generating all tests, run the test suite:

```bash
npm run test -- --coverage
```

### Verify Coverage

- Overall coverage >= {coverage_target}%
- No module below {coverage_target}%
- Every exported function has at least one test
- All branches (if/else, switch/case, try/catch) covered
- All async success and failure paths covered

If any module is below target, add more tests targeting uncovered lines.

### Cleanup Before Commit

- No `console.log` / `console.error` remaining in source files
- No `.skip` or `.only` blocks in test files
- All mocks properly reset between tests (beforeEach cleanup)
- TypeScript compilation succeeds on test files

## Output

Respond with: test file count, total test count, coverage percentage per module, and any modules below target requiring attention.

### Deliverable
Comprehensive test suite with >{coverage_target}% coverage committed and pushed

---

## Completion Webhook

After all tests pass and coverage is verified:

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

If coverage target is not met:
```
{
  "status": "partial",
  "coverage": "XX%",
  "below_target": [ ... modules below threshold ... ],
  "suggestion": "Manual review needed for [modules]"
}
```

If any step fails:
```
POST /agent/task/{task_id}/fail
{ "error": "...", "step": "step-3" }
```