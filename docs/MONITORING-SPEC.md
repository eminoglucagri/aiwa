# Monitoring & Alerting Infrastructure — AIWA-32

**Issue:** AIWA-32
**Status:** In progress
**Updated:** 2026-04-28

## Deliverables

- [x] `SPEC.md` — this document
- [ ] `src/backend/logging.py` — structured JSON logging with levels
- [ ] `src/backend/metrics.py` — Prometheus metrics instrumentation
- [ ] `src/backend/error_tracking.py` — Sentry integration
- [ ] `prometheus/` — Prometheus config + scrape targets
- [ ] `grafana/` — Grafana dashboard JSON for pipeline health
- [ ] `docker-compose.monitoring.yml` — Prometheus + Grafana + Alertmanager stack
- [ ] `scripts/monitoring/` — alerting rules and alert scripts
- [ ] `docs/MONITORING.md` — deployment and usage documentation

## 1. Overview

Observability stack for the AIWA platform using open-source tooling:

| Component | Tool | Purpose |
|---|---|---|
| Structured Logging | Python `structlog` | JSON logs with levels, search via Grafana Loki or plain text |
| Error Tracking | Sentry | Stack traces, error rates, alerting |
| Metrics | Prometheus + `prometheus-fastapi-instrumentator` | Agent execution, task duration, success rate, cost |
| Dashboards | Grafana | Generation pipeline health, system overview |
| Alerting | Prometheus Alertmanager | Alert routing to Slack/email/webhook |
| Uptime Monitoring | Blackbox Exporter | Synthetic checks on generated app endpoints |

## 2. Structured Logging

- Format: JSON (machine-parseable)
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Fields: `timestamp`, `level`, `logger`, `message`, `task_id`, `project_id`, `agent_id`, `duration_ms`
- Output: stdout (container-native) → picked up by Prometheus Loki or stdout logs

## 3. Metrics (Prometheus)

### 3.1 Agent Execution Metrics

```
aiwa_agent_task_duration_seconds{agent_id, task_type, status}
aiwa_agent_task_total{agent_id, task_type, status}
aiwa_agent_cost_usd{agent_id, task_type}
aiwa_agent_token_usage_total{agent_id, token_type}
```

### 3.2 Task Queue Metrics

```
aiwa_queue_depth{queue_name}
aiwa_queue_tasks_total{queue_name, status}
aiwa_queue_latency_seconds{queue_name}
```

### 3.3 API Metrics

```
aiwa_http_requests_total{method, path, status_code}
aiwa_http_request_duration_seconds{method, path}
aiwa_db_query_duration_seconds{operation}
aiwa_redis_operation_duration_seconds{operation}
```

### 3.4 Deployment Metrics

```
aiwa_deployment_total{project_id, status, branch}
aiwa_deployment_duration_seconds{project_id}
```

## 4. Error Tracking (Sentry)

- SDK: `sentry-sdk[fastapi]` in the backend
- Captures: unhandled exceptions, FastAPI route errors, agent failures
- Context: `task_id`, `project_id`, `agent_id` attached to events
- Alert triggers: error rate threshold, new issue creation

## 5. Uptime Monitoring

- Tool: Prometheus `blackbox_exporter`
- Checks: HTTP endpoints for generated Vercel deployments
- Frequency: every 60s per endpoint
- Alert on: HTTP 5xx, timeout > 10s, SSL cert expiry < 7 days

## 6. Dashboards (Grafana)

### 6.1 Generation Pipeline Health Dashboard

Panels:
1. **Task throughput** — tasks completed/hour over time
2. **Success rate** — % of tasks with status=success vs failed
3. **Agent duration distribution** — histogram of task duration
4. **Error rate** — errors captured by Sentry per hour
5. **Queue depth** — current pending tasks per queue
6. **Cost tracking** — estimated API cost per day/week
7. **Uptime summary** — % of generated apps reachable
8. **API latency** — p50, p95, p99 HTTP request duration

## 7. Alerting Rules

| Alert | Expr | Severity | Action |
|---|---|---|---|
| `AgentTaskFailureRateHigh` | `rate(aiwa_agent_task_total{status="failed"}[5m]) > 0.1` | critical | Slack + PagerDuty |
| `AgentTaskTimeout` | `aiwa_agent_task_duration_seconds > 600` | warning | Slack |
| `HighQueueDepth` | `aiwa_queue_depth > 100` | warning | Slack |
| `DeploymentFailureRateHigh` | `rate(aiwa_deployment_total{status="failed"}[5m]) > 0.05` | critical | Slack + webhook |
| `GeneratedAppDown` | `probe_success{job="generated-apps"} == 0` | critical | Slack |
| `HighAPILatency` | `histogram_quantile(0.95, aiwa_http_request_duration_seconds) > 2` | warning | Slack |

## 8. Docker Compose Stack

Services:
- `prometheus` — metrics collection + alerting
- `alertmanager` — alert routing
- `grafana` — dashboards
- `loki` (optional) — log aggregation
- `blackbox-exporter` — uptime probing

## 9. File Structure

```
.
├── src/
│   └── backend/
│       ├── logging.py          # structlog setup
│       ├── metrics.py           # Prometheus metrics + instrumentation
│       └── error_tracking.py    # Sentry integration
├── prometheus/
│   ├── prometheus.yml           # Main scrape config
│   ├── targets.yml              # Scrape target definitions
│   └── rules/
│       └── agent_alerts.yml     # Prometheus alerting rules
├── grafana/
│   └── dashboards/
│       └── pipeline-health.json # Grafana dashboard JSON
├── docker-compose.monitoring.yml # Monitoring stack
├── scripts/
│   └── monitoring/
│       └── setup-alerts.sh     # Alert routing setup
└── docs/
    └── MONITORING.md            # Operations guide
```
