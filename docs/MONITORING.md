# Monitoring & Alerting — AIWA Platform

**Issue:** AIWA-32
**Status:** Implemented
**Updated:** 2026-04-28

---

## Overview

The AIWA platform uses open-source observability tooling: Prometheus for metrics, Grafana for dashboards, Sentry for error tracking, and Prometheus Alertmanager for alerting. Structured JSON logging is available via `structlog`.

---

## Stack

| Component | Image | Port | Purpose |
|---|---|---|---|
| Prometheus | `prom/prometheus:v2.52.0` | 9090 | Metrics collection + alerting rules |
| Alertmanager | `prom/alertmanager:v0.27.1` | 9093 | Alert routing to Slack/email |
| Grafana | `grafana/grafana:11.2.0` | 3000 | Dashboards |
| Blackbox Exporter | `prom/blackbox-exporter:v0.25.0` | 9115 | Uptime monitoring of generated apps |
| Node Exporter | `prom/node-exporter:v1.8.0` | 9100 | Host-level metrics |

---

## Quick Start

### Start the monitoring stack

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

### Verify all services are up

```bash
# Prometheus
curl -s http://localhost:9090/-/healthy

# Grafana
curl -s http://localhost:3000/api/health

# Blackbox exporter
curl -s http://localhost:9115/probe?target=https://example.com&module=http_2xx
```

### Access dashboards

- **Grafana:** http://localhost:3000 (admin / admin)
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093

The **Generation Pipeline Health** dashboard loads automatically — import it from `grafana/dashboards/pipeline-health.json` if auto-provisioning is disabled.

---

## 1. Structured Logging

### Python Integration

```python
from backend.logging import setup_logging, get_logger

setup_logging()  # Call once at app startup
log = get_logger("aiwa.api")

log.info("task_submitted", task_id="abc123", project_id="proj1")
log.error("task_failed", task_id="abc123", error="timeout")
```

### Output Format

JSON to stdout, collected by Loki or written to log files:

```json
{
  "timestamp": "2026-04-28T10:00:00.000Z",
  "level": "info",
  "logger": "aiwa.api",
  "message": "task_submitted",
  "task_id": "abc123",
  "project_id": "proj1",
  "agent_id": "worker-1",
  "caller": "/src/backend/api.py:42"
}
```

### Configuration (`.env`)

```
LOG_LEVEL=INFO
LOG_FORMAT=json          # or "console" for human-readable
```

### Search

In Grafana Loki or stdout:
- `level=error` — all errors
- `task_id=abc123` — all logs for a specific task
- `agent_id=worker-1` — all logs for a worker

---

## 2. Metrics (Prometheus)

Metrics are exposed at `GET /metrics` on the FastAPI backend.

### Backend Setup

```python
from backend.metrics import metrics_router, init_platform_info
from backend.logging import setup_logging

setup_logging()
init_platform_info()

app.include_router(metrics_router)
```

### Key Metrics

| Metric | Type | Labels | Description |
|---|---|---|---|
| `aiwa_agent_task_duration_seconds` | Histogram | agent_id, task_type, status | Agent task execution time |
| `aiwa_agent_task_total` | Counter | agent_id, task_type, status | Total agent tasks |
| `aiwa_agent_cost_usd` | Counter | agent_id, task_type | API cost in USD |
| `aiwa_agent_token_usage_total` | Counter | agent_id, token_type | Token consumption |
| `aiwa_queue_depth` | Gauge | queue_name | Pending tasks per queue |
| `aiwa_http_requests_total` | Counter | method, path, status_code | HTTP request count |
| `aiwa_http_request_duration_seconds` | Histogram | method, path | HTTP request latency |
| `aiwa_deployment_total` | Counter | project_id, status, branch | Deployment attempts |
| `probe_success{job="generated-apps"}` | Gauge | instance | Uptime of generated apps |

### Instrumenting Agent Tasks

```python
from backend.metrics import record_cost, update_queue_depth

# Track cost after a task completes
record_cost(
    agent_id="worker-1",
    task_type="generate",
    cost_usd=2.50,
    tokens={"input": 50000, "output": 12000},
)

# Update queue depth
update_queue_depth("default", depth=42)
```

### Deployment Tracking

```python
from backend.metrics import track_deployment

with track_deployment(project_id="proj123", branch="main"):
    # ... deployment code ...
    pass
```

---

## 3. Error Tracking (Sentry)

### Setup

```python
from backend.error_tracking import init_sentry, attach_task_context

init_sentry()  # Call once at startup (reads SENTRY_DSN from env)
```

### Context

Attach task/project context so every Sentry event is tagged:

```python
from backend.context import TaskContext

with TaskContext(task_id="abc123", project_id="proj1", agent_id="worker-1"):
    # All logs and Sentry events within this block get task_id/proj1/worker-1
    run_agent_task()
```

### Recording Failures

```python
from backend.error_tracking import record_agent_failure

try:
    await agent.run()
except Exception as e:
    record_agent_failure(e, agent_id="worker-1", task_id="abc123", task_type="generate")
    raise
```

### Configuration

```
SENTRY_DSN=https://key@sentry.io/project
ENVIRONMENT=production  # Sets Sentry environment
```

Sentry automatically strips `Authorization`, `Cookie`, and `X-Api-Key` headers before sending.

---

## 4. Uptime Monitoring

Generated Vercel app endpoints are monitored via the Blackbox Exporter.

### Adding a Generated App

Update `prometheus/prometheus.yml` under the `generated-apps` job:

```yaml
- job_name: "generated-apps"
  static_configs:
    - targets:
        - "https://proj1.vercel.app"
        - "https://proj2.vercel.app"
```

Or use file-based service discovery for dynamic targets.

### Alert

- **5m downtime** → `GeneratedAppDown` alert fires → Slack notification

---

## 5. Alerting

### Alert Routing

Alerts route through Alertmanager to Slack (configurable):

| Alert | Severity | Condition |
|---|---|---|
| `AgentTaskFailureRateHigh` | critical | >10% task failure rate over 5m |
| `AgentTaskTimeout` | warning | Task runs >10 minutes |
| `HighQueueDepth` | warning | >100 pending tasks for 10m |
| `NoAgentTasksCompleted` | warning | No completions in 30m |
| `HighAgentCost` | warning | >$100/hour |
| `DeploymentFailureRateHigh` | critical | >5% deployment failure rate |
| `HighAPILatency` | warning | p95 latency >2s for 5m |
| `APIServerDown` | critical | API not responding for 2m |
| `GeneratedAppDown` | critical | Generated app unreachable for 5m |

### Configuring Alert Destinations

Set environment variables before starting Alertmanager:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxx/yyy/zzz"
export SLACK_CHANNEL="#aiwa-alerts"
export SMTP_PASSWORD="mail-password"
```

### Muting Alerts

In Alertmanager, use inhibition rules to prevent warning-level alerts from firing when a critical alert is already active (same alertname/instance).

---

## 6. Dashboards

### Generation Pipeline Health Dashboard

Located at: `grafana/dashboards/pipeline-health.json`

**Panels:**

| Panel | Metric | Description |
|---|---|---|
| Task Success Rate (1h) | `aiwa_agent_task_total` ratio | % of successful tasks |
| Queue Depth | `aiwa_queue_depth` | Total pending tasks |
| Generated Apps Up | `probe_success` | Count of reachable apps |
| API Cost (24h) | `aiwa_agent_cost_usd` increase | Daily cost |
| Task Throughput | `aiwa_agent_task_total` rate | Tasks/min by type |
| Task Duration | `aiwa_agent_task_duration_seconds` | p50/p95/p99 histogram |
| API Cost by Type | `aiwa_agent_cost_usd` increase | Cost breakdown by task type |
| Queue Depth Over Time | `aiwa_queue_depth` | Per-queue trend |
| Token Usage (1h) | `aiwa_agent_token_usage_total` | Input/output tokens |
| HTTP Request Rate | `aiwa_http_requests_total` | Requests/sec by path |
| API Latency | `aiwa_http_request_duration_seconds` | p50/p95/p99 |
| Deployment Rate | `aiwa_deployment_total` | Deployments/hour by status |
| Generated App Uptime | `probe_success` | Uptime % per app |

### Importing the Dashboard

1. Open Grafana → Dashboards → Import
2. Upload `grafana/dashboards/pipeline-health.json`
3. Select the Prometheus datasource
4. Click Import

---

## 7. Project Structure

```
.
├── src/backend/
│   ├── logging.py           # structlog setup + get_logger()
│   ├── metrics.py           # Prometheus metrics + /metrics endpoint
│   ├── error_tracking.py   # Sentry integration
│   ├── context.py          # Thread-local task context
│   └── config.py           # Settings (reads from .env)
├── prometheus/
│   ├── prometheus.yml       # Scrape config (API, worker, blackbox, node)
│   └── rules/
│       └── agent_alerts.yml # Prometheus alerting rules (6 alert groups)
├── grafana/
│   ├── dashboards/
│   │   └── pipeline-health.json  # Generation pipeline health dashboard
│   └── provisioning/
│       ├── datasources/datasources.yml
│       └── dashboards/dashboards.yml
├── alertmanager/config/
│   └── alertmanager.yml    # Slack + email routing, inhibition rules
├── blackbox/config/
│   └── blackbox.yml        # HTTP 2xx prober config
├── docker-compose.monitoring.yml  # Full stack (Prometheus, Grafana, Alertmanager, etc.)
├── scripts/monitoring/
│   └── setup-alerts.sh      # Alert routing setup script
└── docs/
    ├── MONITORING.md       # This document
    └── MONITORING-SPEC.md   # Specification
```

---

## 8. Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Log verbosity |
| `LOG_FORMAT` | `json` | `json` or `console` |
| `SENTRY_DSN` | _(empty)_ | Sentry project DSN |
| `ENVIRONMENT` | `development` | Sentry environment |
| `SLACK_WEBHOOK_URL` | _(empty)_ | Slack webhook for alerts |
| `SLACK_CHANNEL` | `#aiwa-alerts` | Slack channel for routing |
| `SMTP_PASSWORD` | _(empty)_ | SMTP auth for email alerts |
| `GRAFANA_ADMIN_USER` | `admin` | Grafana admin username |
| `GRAFANA_ADMIN_PASSWORD` | `admin` | Grafana admin password |

---

## 9. Next Steps

1. **Add `structlog` and `prometheus-client` to requirements** when backend dependencies are defined
2. **Instrument the FastAPI app** with `metrics_router` and `init_sentry()` in the app entry point
3. **Configure SENTRY_DSN** in Vercel environment variables
4. **Set up Slack webhook** for `#aiwa-alerts`
5. **Import the Grafana dashboard** and configure datasource
6. **Wire up agent workers** to expose `/metrics` and call `record_cost()` on task completion
7. **Add dynamic target discovery** for generated apps (currently placeholder) using a file_sd JSON file updated by the Control Plane
8. **Set up Grafana SSO** (OIDC) when platform auth is in place
