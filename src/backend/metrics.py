"""
Prometheus metrics instrumentation for AIWA backend.
Exposes agent execution, task queue, API, and deployment metrics.
"""

from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from time import perf_counter

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, Info, generate_latest

from .config import get_settings

# ── Agent Execution Metrics ──────────────────────────────────────────────────

AGENT_TASK_DURATION = Histogram(
    "aiwa_agent_task_duration_seconds",
    "Time spent executing an agent task",
    labelnames=["agent_id", "task_type", "status"],
    buckets=(10, 30, 60, 120, 300, 600, 1800, 3600),
)

AGENT_TASK_TOTAL = Counter(
    "aiwa_agent_task_total",
    "Total number of agent tasks",
    labelnames=["agent_id", "task_type", "status"],
)

AGENT_COST_USD = Counter(
    "aiwa_agent_cost_usd",
    "Estimated API cost in USD",
    labelnames=["agent_id", "task_type"],
)

AGENT_TOKEN_USAGE = Counter(
    "aiwa_agent_token_usage_total",
    "Total tokens consumed by agent tasks",
    labelnames=["agent_id", "token_type"],
)

# ── Task Queue Metrics ───────────────────────────────────────────────────────

QUEUE_DEPTH = Gauge(
    "aiwa_queue_depth",
    "Number of pending tasks in a queue",
    labelnames=["queue_name"],
)

QUEUE_TASKS_TOTAL = Counter(
    "aiwa_queue_tasks_total",
    "Total tasks submitted to a queue",
    labelnames=["queue_name", "status"],
)

QUEUE_LATENCY = Histogram(
    "aiwa_queue_latency_seconds",
    "Time from task enqueue to worker pick-up",
    labelnames=["queue_name"],
    buckets=(0.5, 1, 2, 5, 10, 30, 60),
)

# ── API Metrics ───────────────────────────────────────────────────────────────

HTTP_REQUESTS_TOTAL = Counter(
    "aiwa_http_requests_total",
    "Total HTTP requests to the API",
    labelnames=["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION = Histogram(
    "aiwa_http_request_duration_seconds",
    "HTTP request duration in seconds",
    labelnames=["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

DB_QUERY_DURATION = Histogram(
    "aiwa_db_query_duration_seconds",
    "Database query duration",
    labelnames=["operation"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1),
)

REDIS_OPERATION_DURATION = Histogram(
    "aiwa_redis_operation_duration_seconds",
    "Redis operation duration",
    labelnames=["operation"],
    buckets=(0.0005, 0.001, 0.005, 0.01, 0.05),
)

# ── Deployment Metrics ────────────────────────────────────────────────────────

DEPLOYMENT_TOTAL = Counter(
    "aiwa_deployment_total",
    "Total deployment attempts",
    labelnames=["project_id", "status", "branch"],
)

DEPLOYMENT_DURATION = Histogram(
    "aiwa_deployment_duration_seconds",
    "Time from deployment trigger to ready",
    labelnames=["project_id"],
    buckets=(10, 30, 60, 120, 300, 600),
)

# ── Info ──────────────────────────────────────────────────────────────────────

PLATFORM_INFO = Info(
    "aiwa_platform",
    "AIWA platform version and environment",
)

# ── Utilities ─────────────────────────────────────────────────────────────────


def track_task(agent_id: str, task_type: str):
    """Decorator to automatically track agent task metrics."""
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = perf_counter()
            status = "success"
            try:
                result = fn(*args, **kwargs)
                return result
            except Exception:
                status = "failed"
                raise
            finally:
                duration = perf_counter() - start
                AGENT_TASK_DURATION.labels(agent_id=agent_id, task_type=task_type, status=status).observe(duration)
                AGENT_TASK_TOTAL.labels(agent_id=agent_id, task_type=task_type, status=status).inc()
        return wrapper
    return decorator


@contextmanager
def track_deployment(project_id: str, branch: str):
    """Context manager for deployment metrics."""
    start = perf_counter()
    status = "success"
    try:
        yield
    except Exception:
        status = "failed"
        raise
    finally:
        duration = perf_counter() - start
        DEPLOYMENT_TOTAL.labels(project_id=project_id, status=status, branch=branch).inc()
        if status == "success":
            DEPLOYMENT_DURATION.labels(project_id=project_id).observe(duration)


def record_cost(agent_id: str, task_type: str, cost_usd: float, tokens: dict[str, int]):
    """Record API cost and token usage for a task."""
    AGENT_COST_USD.labels(agent_id=agent_id, task_type=task_type).inc(cost_usd)
    for token_type, count in tokens.items():
        AGENT_TOKEN_USAGE.labels(agent_id=agent_id, token_type=token_type).inc(count)


def update_queue_depth(queue_name: str, depth: int):
    QUEUE_DEPTH.labels(queue_name=queue_name).set(depth)


def record_db_query(operation: str, duration: float):
    DB_QUERY_DURATION.labels(operation=operation).observe(duration)


# ── FastAPI Router for /metrics endpoint ─────────────────────────────────────

metrics_router = APIRouter()


@metrics_router.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def init_platform_info():
    settings = get_settings()
    PLATFORM_INFO.info({
        "version": "1.0.0",
        "environment": settings.environment,
    })
