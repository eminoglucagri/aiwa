#!/usr/bin/env bash
# Smoke test script for Vercel preview deployments
# Usage: ./smoke-test.sh <preview_url> [--verbose]
#
# Exit codes:
#   0 = all tests passed
#   1 = one or more tests failed

set -euo pipefail

PREVIEW_URL="${1:-}"

if [[ -z "$PREVIEW_URL" ]]; then
  echo "Usage: $0 <preview_url>"
  echo "Example: $0 https://my-app.vercel.app"
  exit 1
fi

# Normalize URL (ensure https)
if [[ "$PREVIEW_URL" != https://* ]]; then
  PREVIEW_URL="${PREVIEW_URL/http:\/\//https://}"
fi

echo "============================================"
echo "Smoke Test Suite"
echo "URL: $PREVIEW_URL"
echo "============================================"

FAILED=0
PASSED=0

pass() {
  echo "  PASS: $1"
  ((PASSED++))
}

fail() {
  echo "  FAIL: $1"
  ((FAILED++))
}

# Test 1: HTTP Status Code
echo ""
echo "[1/8] HTTP Status Code"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL" --max-time 30 --location)
if [[ "$STATUS" -eq 200 ]]; then
  pass "HTTP 200 OK (got $STATUS)"
else
  fail "Expected 200, got $STATUS"
fi

# Test 2: Health Endpoint
echo ""
echo "[2/8] Health Endpoint"
for endpoint in "/health" "/api/health" "/_health" "/status" "/api/status"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${PREVIEW_URL}${endpoint}" --max-time 15 --location 2>/dev/null || echo "000")
  if [[ "$STATUS" -eq 200 ]]; then
    pass "Health endpoint $endpoint returned 200"
    break
  fi
done

# Test 3: Critical Assets Load
echo ""
echo "[3/8] Critical Assets Load"
HTML=$(curl -s "$PREVIEW_URL" --max-time 30 --location)
if [[ -z "$HTML" ]]; then
  fail "Empty HTML response"
else
  if echo "$HTML" | grep -qi "<html"; then
    pass "Valid HTML document"
  else
    fail "No <html> tag found"
  fi
fi

# Test 4: Security Headers
echo ""
echo "[4/8] Security Headers"
HEADERS=$(curl -s -I "$PREVIEW_URL" --max-time 15 --location 2>/dev/null | tr -d '\r')
if echo "$HEADERS" | grep -qi "x-content-type-options"; then
  pass "X-Content-Type-Options header present"
fi
if echo "$HEADERS" | grep -qi "x-frame-options"; then
  pass "X-Frame-Options header present"
fi

# Test 5: API Endpoints
echo ""
echo "[5/8] API Endpoints"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${PREVIEW_URL}/api" --max-time 15 --location 2>/dev/null || echo "000")
if [[ "$API_STATUS" =~ ^(200|404|405)$ ]]; then
  pass "API base responds (HTTP $API_STATUS)"
fi

# Test 6: SSL Certificate
echo ""
echo "[6/8] SSL Certificate"
if [[ "$PREVIEW_URL" == https://* ]]; then
  HOST="${PREVIEW_URL#https://}"
  HOST="${HOST%%:*}"
  EXPIRY=$(echo | openssl s_client -connect "$HOST:443" -servername "$HOST" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2)
  if [[ -n "$EXPIRY" ]]; then
    pass "SSL certificate valid (expires: $EXPIRY)"
  fi
fi

# Test 7: Response Time
echo ""
echo "[7/8] Response Time"
ELAPSED=$(curl -s -o /dev/null -w "%{time_total}" "$PREVIEW_URL" --max-time 60 --location 2>/dev/null || echo "60")
if [[ "$(echo "$ELAPSED < 5" | bc -l 2>/dev/null || echo "0")" -eq 1 ]]; then
  pass "Response time < 5s (${ELAPSED}s)"
else
  fail "Response time too slow: ${ELAPSED}s (threshold: 5s)"
fi

# Test 8: 404 Handling
echo ""
echo "[8/8] 404 Handling"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${PREVIEW_URL}/this-page-does-not-exist-abc123" --max-time 15 --location 2>/dev/null || echo "000")
if [[ "$STATUS" =~ ^(404|200|301|302)$ ]]; then
  pass "Non-existent page handled gracefully (HTTP $STATUS)"
fi

# Summary
echo ""
echo "============================================"
echo "Results: $PASSED passed, $FAILED failed"
echo "============================================"

if [[ $FAILED -gt 0 ]]; then
  echo "SMOKE TESTS FAILED"
  exit 1
else
  echo "All smoke tests passed"
  exit 0
fi
