# Deployment Guide

## Overview

This document describes the automated CI/CD pipeline for the AI Web Development Automation Platform. The pipeline handles code push through to production deployment on Vercel, including smoke testing and automatic rollback on failure.

## Pipeline Flow

```
Code Push → Vercel Preview Deploy → Smoke Tests → [main branch only] Promote to Production
                                                                         ↓ [failure]
                                                                   Rollback
```

## Components

### 1. CI Workflow (`.github/workflows/vercel-deploy.yml`)

Triggers on every push to any branch. Runs in 4 jobs:

| Job | Trigger | Description |
|-----|---------|-------------|
| `preview` | All pushes | Deploys to Vercel preview URL |
| `smoke-test` | After `preview` | Validates preview URL health |
| `promote` | `main` + smoke passed | Promotes preview to production |
| `rollback` | `main` + smoke failed | Reverts to previous production |

### 2. Smoke Tests (`scripts/deploy/smoke-test.sh`)

Checks the preview deployment health:

1. HTTP 200 response from preview URL
2. Response body non-empty (>1KB)
3. No Vercel error pages in response
4. Critical CSS/JS assets loadable

### 3. Rollback Script (`scripts/deploy/rollback.sh`)

On smoke test failure on `main`:
1. Fetches last stable production deployment ID
2. Marks the failed deployment as inactive
3. Redeploys the last stable production build

## Vercel API Requirements

The pipeline uses these Vercel API endpoints:

- **Preview deploy**: `amond/vercel-action@v2` GitHub Action
- **Promote to production**: `POST /v13/deployments/{id}/production`
- **Deactivate failed deployment**: `PATCH /v13/deployments/{id}` with `{"inactive": true}`
- **Redeploy stable**: `POST /v13/deployments/{id}/redeploy`

## Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `VERCEL_TOKEN` | Vercel API token with deploy permissions |
| `VERCEL_ORG_ID` | Vercel organization ID (`team_xxx`) |
| `VERCEL_PROJECT_ID` | Vercel project ID |

## Branch Behavior

| Branch | Behavior |
|--------|----------|
| `main` | Preview deploy → smoke test → promote to production |
| Any feature branch | Preview deploy → smoke test → no promotion |

## Manual Promotion

To trigger a production deployment via API:

```bash
# Trigger via repository dispatch
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/{owner}/{repo}/dispatches \
  -d '{"event_type":"deploy-production","client_payload":{"ref":"main"}}'
```

## Adding New Environment Variables

1. Add the variable to Vercel dashboard → Project → Environment Variables
2. Reference it in `.github/workflows/vercel-deploy.yml` as `${{ vars.VAR_NAME }}`

## Troubleshooting

### Smoke tests fail
- Check the preview URL directly in browser
- Verify all API endpoints return proper status codes
- Check Vercel deployment logs in the Vercel dashboard

### Rollback didn't work
- Manually go to Vercel dashboard → Deployments
- Find the last green deployment and click "Promote to Production"

### Preview not triggering
- Verify GitHub Actions has access to the repository
- Check that the Vercel GitHub integration is connected in Vercel dashboard
- Ensure `VERCEL_TOKEN` secret is not expired