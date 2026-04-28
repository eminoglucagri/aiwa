"""
Thread-local context for request-scoped data (task_id, project_id, agent_id).
Used by logging, Sentry, and metrics to enrich every log entry/event.
"""

import contextvars
from typing import Optional

_task_context: contextvars.ContextVar[dict] = contextvars.ContextVar("task_context", default={})


def set_task_context(task_id: str | None = None, project_id: str | None = None, agent_id: str | None = None) -> None:
    """Set context variables for the current async task."""
    _task_context.set({
        "task_id": task_id,
        "project_id": project_id,
        "agent_id": agent_id,
    })


def get_current_task_context() -> dict:
    """Return the current task context dict (may be empty)."""
    return _task_context.get()


def clear_task_context() -> None:
    """Clear context when task ends."""
    _task_context.set({})


class TaskContext:
    """Async context manager to scope task context to a block."""

    def __init__(self, task_id: str | None = None, project_id: str | None = None, agent_id: str | None = None):
        self.task_id = task_id
        self.project_id = project_id
        self.agent_id = agent_id
        self._token: contextvars.Token | None = None

    def __enter__(self):
        self._token = _task_context.set({
            "task_id": self.task_id,
            "project_id": self.project_id,
            "agent_id": self.agent_id,
        })
        return self

    def __exit__(self, *args):
        _task_context.reset(self._token)
