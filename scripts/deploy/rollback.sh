#!/usr/bin/env bash
# Rollback script for failed Vercel deployments
# Usage: ./rollback.sh --project-id <id> --token <token> --failed-deployment <id> --reason <reason>
#
# Exit codes:
#   0 = rollback successful
#   1 = rollback failed

set -euo pipefail

PROJECT_ID=""
TOKEN=""
FAILED_DEPLOYMENT=""
REASON="unknown"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-id) PROJECT_ID="$2"; shift 2 ;;
    --token) TOKEN="$2"; shift 2 ;;
    --failed-deployment) FAILED_DEPLOYMENT="$2"; shift 2 ;;
    --reason) REASON="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$PROJECT_ID" || -z "$TOKEN" || -z "$FAILED_DEPLOYMENT" ]]; then
  echo "Usage: $0 --project-id <id> --token <token> --failed-deployment <id> --reason <reason>"
  exit 1
fi

echo "============================================"
echo "Vercel Deployment Rollback"
echo "============================================"
echo "Project ID: $PROJECT_ID"
echo "Failed Deployment: $FAILED_DEPLOYMENT"
echo "Reason: $REASON"
echo ""

# Step 1: Get the current production deployment
echo "[1/4] Fetching current production deployment..."
CURRENT_PROD=$(curl -s -X GET \
  "https://api.vercel.com/v13/deployments?projectId=$PROJECT_ID&target=production&state=READY" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

CURRENT_DEPLOYMENT_ID=$(echo "$CURRENT_PROD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['deployments'][0]['uid'] if d.get('deployments') else '')" 2>/dev/null || echo "")

if [[ -z "$CURRENT_DEPLOYMENT_ID" ]]; then
  echo "WARNING: Could not find current production deployment"
  CURRENT_DEPLOYMENT_ID="unknown"
fi
echo "Current production deployment: $CURRENT_DEPLOYMENT_ID"

# Step 2: Get the last successful deployment before the failed one
echo ""
echo "[2/4] Finding last successful deployment..."
ALL_DEPLOYS=$(curl -s -X GET \
  "https://api.vercel.com/v13/deployments?projectId=$PROJECT_ID&limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

LAST_SUCCESSFUL=$(echo "$ALL_DEPLOYS" | python3 -c "
import sys, json
deployments = json.load(sys.stdin).get('deployments', [])
for d in deployments:
  if d.get('readyState') == 'READY' and d.get('uid') != '$FAILED_DEPLOYMENT':
    print(d['uid'])
    break
" 2>/dev/null || echo "")

if [[ -z "$LAST_SUCCESSFUL" ]]; then
  echo "ERROR: No previous successful deployment found"
  exit 1
fi
echo "Will rollback to: $LAST_SUCCESSFUL"

# Step 3: Promote the last successful deployment to production
echo ""
echo "[3/4] Promoting last successful deployment to production..."
ROLLBACK_RESPONSE=$(curl -s -X POST \
  "https://api.vercel.com/v13/deployments/$LAST_SUCCESSFUL/production" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"failedDeploymentId\": \"$FAILED_DEPLOYMENT\"}")

ROLLBACK_URL=$(echo "$ROLLBACK_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url', 'unknown'))" 2>/dev/null || echo "unknown")
echo "Rollback deployment URL: $ROLLBACK_URL"

# Step 4: Wait for rollback deployment to be ready
echo ""
echo "[4/4] Waiting for rollback deployment to be ready..."
for i in {1..30}; do
  DEPLOY_STATE=$(curl -s -X GET \
    "https://api.vercel.com/v13/deployments/$LAST_SUCCESSFUL" \
    -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('readyState','INITIALIZING'))" 2>/dev/null || echo "INITIALIZING")

  echo "  Attempt $i: state=$DEPLOY_STATE"
  if [[ "$DEPLOY_STATE" == "READY" ]]; then
    echo ""
    echo "Rollback complete!"
    echo "============================================"
    echo "Rollback URL: https://$ROLLBACK_URL"
    echo "Failed deployment: $FAILED_DEPLOYMENT"
    echo "Reason: $REASON"
    exit 0
  elif [[ "$DEPLOY_STATE" == "ERROR" || "$DEPLOY_STATE" == "FAILED" ]]; then
    echo "ERROR: Rollback deployment also failed"
    exit 1
  fi
  sleep 10
done

echo "WARNING: Rollback deployment did not complete within 5 minutes"
echo "Check Vercel dashboard for status"
exit 1
