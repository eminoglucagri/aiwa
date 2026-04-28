# Code Review Pipeline

Automated code review pipeline that runs on every pull request opened, updated, or ready for review.

## Trigger

- **Event**: `pull_request` (opened, synchronize, reopened, ready_for_review)
- **Branches**: `main`
- **Concurrency**: Cancels in-progress runs for the same PR

## Jobs

### 1. Frontend Checks (`frontend-checks`)

Runs on the `frontend/` directory (Node 20).

| Step | Tool | Config | Command |
|------|------|--------|---------|
| Style | ESLint | `.eslintrc.json` | `npx eslint src --max-warnings 0` |
| Formatting | Prettier | `.prettierrc` | `npx prettier --check src` |
| Type safety | TypeScript | `tsconfig.json` | `npx tsc --noEmit` |
| Tests | Vitest | `vite.config.ts` | `npm test -- --run` |

All steps fail the job on any warning/error.

### 2. Backend Checks (`backend-checks`)

Runs on the `backend/` directory (Python 3.12).

| Step | Tool | Config | Command |
|------|------|--------|---------|
| Linting | Ruff | `ruff.toml` | `ruff check app/` |
| Formatting | Ruff | `ruff.toml` | `ruff format --check app/` |
| Type safety | mypy | `mypy.ini` | `mypy app/` |
| Tests | pytest | `pytest.ini` (default) | `pytest tests/ -v` |

### 3. Security & Static Analysis (`security-checks`)

Runs at the repo root.

- **Semgrep**: `p/security-audit`, `p/secrets`, `p/typescript`, `p/python`
- **Secrets scan**: `detect-secrets` (skipped if not installed)
- **Node audit**: `npm audit --audit-level=high` on `frontend/`

### 4. AI Review Summary (`ai-review`)

Requires all previous jobs to pass. Skipped for draft PRs.

1. Fetches diff: `git diff origin/main...HEAD`
2. Calls Claude Opus 4.7 via `@anthropic-ai/sdk`
3. Posts a structured review comment to the PR via `gh pr comment`

Review format:

```
## AI Code Review Summary

### Changes Overview
[description]

### Findings
#### ✅ LGTM
#### ⚠️ Suggestions
#### 🔴 Critical Issues
#### 📝 Documentation

### Summary
[One-line verdict]
```

Required secret: `ANTHROPIC_API_KEY`

### 5. CI Gate (`ci-gate`)

Passes only when `frontend-checks`, `backend-checks`, and `security-checks` all succeed.

## Required Secrets

| Secret | Used by |
|--------|---------|
| `ANTHROPIC_API_KEY` | `ai-review` job |
| `GITHUB_TOKEN` | `gh pr comment` (auto-provided) |

## Config Files

| File | Purpose |
|------|---------|
| `.github/workflows/code-review.yml` | GitHub Actions pipeline |
| `frontend/package.json` | npm scripts for lint, format:check, typecheck, test, test:run |
| `frontend/.eslintrc.cjs` | ESLint rules for TypeScript/React (TypeScript ESLint plugin, react-hooks, react-refresh) |
| `frontend/.prettierrc` | Prettier formatting rules (no semicolons, single quotes, 100-char line width) |
| `frontend/vite.config.ts` | Vitest test configuration (jsdom environment, testing-library setup) |
| `frontend/src/test/setup.ts` | Vitest globals and cleanup (afterEach cleanup + jest-dom matchers) |
| `frontend/src/test/*.test.tsx` | Frontend test files |
| `frontend/tsconfig.json` | TypeScript compiler options |
| `backend/ruff.toml` | Ruff linting and formatting rules (isort, pyupgrade, bugbear, single-quote output) |
| `backend/mypy.ini` | mypy static type checking config |
| `backend/requirements.txt` | Python dependencies |
| `backend/tests/` | Backend pytest test files |
| `pyproject.toml` | Project-level tool config (Ruff + mypy + pytest settings for src/) |

## Running Locally

```bash
# Frontend checks
cd frontend && npm ci
npm run lint
npm run format:check
npm run typecheck
npm test -- --run

# Backend checks
cd backend
pip install -r requirements.txt ruff mypy pytest
ruff check app/
ruff format --check app/
mypy app/
pytest tests/ -v
```

## Branch Protection

This pipeline should be required in branch protection rules for `main`. Any PR that fails the pipeline cannot be merged.
