"""
Sentry error tracking integration for AIWA backend.
Attaches contextual metadata (task_id, project_id, agent_id) to events.
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .config import get_settings
from .context import get_current_task_context


def init_sentry() -> None:
    """Initialize Sentry with FastAPI and Redis integrations."""
    settings = get_settings()

    if not settings.sentry_dsn:
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        release="aiwa@1.0.0",
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            RedisIntegration(),
        ],
        before_send=filter_sensitive_events,
        send_default_pii=False,
        max_breadcrumbs=50,
        sample_rate=1.0,
        traces_sample_rate=0.1,
    )


def filter_sensitive_events(event: dict, hint: dict) -> dict | None:
    """Strip sensitive data before sending to Sentry."""
    # Remove Authorization headers
    if "request" in event:
        headers = event["request"].get("headers", {})
        filtered = {k: v for k, v in headers.items() if k.lower() not in ("authorization", "cookie", "x-api-key")}
        event["request"]["headers"] = filtered

    # Remove raw SQL queries that may contain secrets
    if "breadcrumbs" in event:
        for bc in event["breadcrumbs"]:
            if bc.get("category") == "db":
                bc["message"] = "<redacted>"

    return event


def attach_task_context():
    """Attach current task/project context to the Sentry scope."""
    ctx = get_current_task_context()
    if not ctx:
        return

    with sentry_sdk.configure_scope() as scope:
        if ctx.get("task_id"):
            scope.set_tag("task_id", ctx["task_id"])
        if ctx.get("project_id"):
            scope.set_tag("project_id", ctx["project_id"])
        if ctx.get("agent_id"):
            scope.set_tag("agent_id", ctx["agent_id"])


def record_agent_failure(error: Exception, agent_id: str, task_id: str | None = None, task_type: str | None = None):
    """Explicitly capture an agent failure with full context."""
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("agent_id", agent_id)
        if task_id:
            scope.set_tag("task_id", task_id)
        if task_type:
            scope.set_tag("task_type", task_type)
        scope.set_level("error")
        sentry_sdk.capture_exception(error)
