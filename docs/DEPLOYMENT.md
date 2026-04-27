# Deployment Workflow — AI Web Development Automation Platform

**Issue:** AIWA-20
**Status:** Implemented
**Last Updated:** 2026-04-28

---

## Overview

This document describes the automated deployment pipeline for the AIWA platform. The pipeline handles: code push → Vercel preview deployment → smoke tests → production promotion → rollback on failure.

---

## Pipeline Stages

```
Push to branch
    │
    ▼
┌─────────────────────┐
│  Preview Deployment  │
│  (every branch)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Smoke Tests        │─────────── FAIL ───────────┐
│  (8 checks)         │                             │
└──────────┬──────────┘                             │
           │ PASS                                    ▼
           ▼                              ┌─────────────────────┐
┌─────────────────────┐                   │  Rollback            │
│  Promote to Prod     │                   │  (main branch only)  │
│  (main branch only)  │                   └─────────────────────┘
└─────────────────────┘
```

---

## Stage 1: Preview Deployment

**Trigger:** Any push to any branch

**Actions:**
1. GitHub Actions checks out the code
2. Installs dependencies (`npm ci`)
3. Runs `npm run typecheck` (skipped if not configured)
4. Runs `npm run lint` (skipped if not configured)
5. Runs `npm test` (skipped if not configured)
6. Deploys to Vercel preview via `amond/vercel-action@v2`

**Outputs:**
- `preview_url` — URL of the preview deployment
- `preview_deployment_id` — Vercel deployment ID

**Secrets Required (GitHub Actions):**
| Secret | Description |
|---|---|
| `VERCEL_TOKEN` | Vercel API token |
| `VERCEL_ORG_ID` | Vercel organization ID |
| `VERCEL_PROJECT_ID` | Vercel project ID |

---

## Stage 2: Smoke Tests

**Trigger:** After preview deployment succeeds

**Test Suite (8 checks):**
1. **HTTP Status** — Expects 200 on root URL
2. **Health Endpoint** — Checks `/health`, `/api/health`, `/_health`, `/status`, `/api/status`
3. **Critical Assets** — Validates HTML structure and JS bundle references
4. **Security Headers** — Checks `X-Content-Type-Options`, `X-Frame-Options`
5. **API Endpoints** — Verifies `/api` responds with 200/404/405
6. **SSL Certificate** — Validates certificate is present and not expired
7. **Response Time** — Expects < 5 second response
8. **404 Handling** — Non-existent pages return 4xx, not 5xx

**Script:** `scripts/deploy/smoke-test.sh <preview_url>`

**Exit Codes:**
- `0` — All tests passed
- `1` — One or more tests failed

**On Failure:** Pipeline stops. On `main` branch, rollback is triggered.

---

## Stage 3: Promote to Production

**Trigger:** Push to `main` branch, smoke tests passed

**Actions:**
1. POST to `https://api.vercel.com/v13/deployments/{id}/production`
2. Vercel promotes the preview deployment to production URL
3. GitHub deployment record created (state: success)

---

## Stage 4: Rollback

**Trigger:** Smoke tests fail on `main` branch

**Actions:**
1. Identify the last successful production deployment
2. Promote it to production (replaces the failed deployment)
3. Wait up to 5 minutes for the rollback to become `READY`
4. Create GitHub deployment record (state: failure)

**Script:** `scripts/deploy/rollback.sh --project-id <id> --token <token> --failed-deployment <id> --reason <reason>`

**Rollback Logic:**
1. Fetch current production deployment ID
2. Find most recent `READY` deployment that is not the failed one
3. Promote that deployment to production
4. Poll for `READY` state (30 attempts × 10s = 5 min timeout)

---

## GitHub Actions Secrets Setup

### Required Secrets

Add these in **GitHub repo → Settings → Secrets and variables → Actions**:

```bash
VERCEL_TOKEN=ahor_xxxxxxxxxxxxxxxx
VERCEL_ORG_ID=team_xxxxxxxxxxxxxxxx
VERCEL_PROJECT_ID=prj_xxxxxxxxxxxxxxxx
```

### Getting Vercel Credentials

1. **Vercel Token:** [vercel.com/account/tokens](https://vercel.com/account/tokens) → Create token
2. **Org ID:** Run `vercel inspect <deployment-url>` or call `GET /v2/orgs/me`
3. **Project ID:** Found in project URL: `vercel.com/{org}/{project}/...` or via API

---

## Vercel Configuration

### vercel.json

```json
{
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm ci",
  "regions": ["iad1"],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

### Environment Variables (Vercel Dashboard)

For each environment (Production, Preview, Development):

| Variable | Description |
|---|---|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `REDIS_URL` | Upstash Redis connection string |
| `JWT_SECRET` | Secret for signing JWTs |
| `ANTHROPIC_API_KEY` | Anthropic/Minimax API key |

---

## Pipeline Failure Modes

| Failure Point | Behavior |
|---|---|
| Preview build fails | No deployment, job fails |
| Preview deploy fails | Job fails, no smoke tests |
| Smoke tests fail (non-main) | Job fails, no promotion, no rollback |
| Smoke tests fail (main) | Triggers rollback to previous deployment |
| Rollback times out | Logs warning, exit 1 — manual intervention needed |
| Rollback also fails | Exit 1 — manual intervention required |

---

## Local Deployment Testing

Test the smoke test script locally:

```bash
# Make sure script is executable
chmod +x scripts/deploy/smoke-test.sh

# Run against a preview URL
./scripts/deploy/smoke-test.sh https://your-app.vercel.app

# Test the rollback script
./scripts/deploy/rollback.sh \
  --project-id prj_xxx \
  --token vercel_token \
  --failed-deployment dep_xxx \
  --reason "smoke-test-failure"
```

---

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── vercel-deploy.yml     # GitHub Actions pipeline
├── scripts/
│   └── deploy/
│       ├── smoke-test.sh          # Smoke test suite
│       └── rollback.sh            # Rollback automation
├── vercel.json                    # Vercel project config
└── docs/
    └── DEPLOYMENT.md              # This document
```

---

## Current Status

- **Workflow:** `.github/workflows/vercel-deploy.yml` — Created
- **Smoke Tests:** `scripts/deploy/smoke-test.sh` — Created (8 checks)
- **Rollback:** `scripts/deploy/rollback.sh` — Created (auto-promotes last successful)
- **Documentation:** `docs/DEPLOYMENT.md` — Created
- **Pending:** `vercel.json` — Stub, needs project-specific configuration

---

## Next Steps

1. **Configure Vercel secrets** in GitHub repo
2. **Add `vercel.json`** with project-specific build settings
3. **Create project** at vercel.com and get org/project IDs
4. **Run first manual deployment** to verify pipeline end-to-end
5. **Add `npm run typecheck && npm run build`** to pipeline once React frontend exists
