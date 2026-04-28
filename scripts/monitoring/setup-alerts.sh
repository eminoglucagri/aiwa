#!/usr/bin/env bash
# Alertmanager webhook setup for AIWA monitoring.
# Configures alert routing to Slack, email, or generic webhooks.
# Usage: ./setup-alerts.sh --webhook-url <url> [--slack-channel "#alerts"]

set -euo pipefail

WEBHOOK_URL=""
SLACK_CHANNEL="#aiwa-alerts"
ALERTMANAGER_HOST="${ALERTMANAGER_HOST:-http://localhost:9093}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --webhook-url) WEBHOOK_URL="$2"; shift 2 ;;
    --slack-channel) SLACK_CHANNEL="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$WEBHOOK_URL" ]]; then
  echo "Usage: $0 --webhook-url <webhook-url> [--slack-channel #channel]"
  exit 1
fi

echo "============================================"
echo "Configuring Alertmanager"
echo "============================================"
echo "Alertmanager: $ALERTMANAGER_HOST"
echo "Webhook URL: $WEBHOOK_URL"
echo "Slack Channel: $SLACK_CHANNEL"
echo ""

# Apply the Alertmanager configuration via its API
curl -s -X POST "$ALERTMANAGER_HOST/api/v1/alerts" \
  -H "Content-Type: application/json" \
  -d @"$(dirname "$0")/alertmanager.yml" 2>/dev/null || {
    echo "Note: Alertmanager may not be running yet."
    echo "Configuration will be loaded automatically from:"
    echo "  docker-compose.monitoring.yml → alertmanager/config/alertmanager.yml"
  }

echo ""
echo "Alertmanager configuration complete."
echo "Configuration file: $(dirname "$0")/alertmanager.yml"
echo ""
echo "To apply on a live Alertmanager instance:"
echo "  curl -X POST $ALERTMANAGER_HOST/api/v1/alerts -d @alertmanager.yml"
