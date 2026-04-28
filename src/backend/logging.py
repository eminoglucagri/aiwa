#!/usr/bin/env python3
"""
Structured logging setup for AIWA backend.
Uses structlog for JSON-formatted, contextual logging.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from .config import get_settings


def add_task_context(Logger, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Attach any active task/project context to every log entry."""
    from .context import get_current_task_context
    ctx = get_current_task_context()
    if ctx:
        event_dict["task_id"] = ctx.get("task_id")
        event_dict["project_id"] = ctx.get("project_id")
        event_dict["agent_id"] = ctx.get("agent_id")
    return event_dict


def add_caller_info(Logger, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add caller filename and line number for traceability."""
    frame = sys._getframe(3)
    event_dict["caller"] = f"{frame.f_code.co_filename}:{frame.f_lineno}"
    return event_dict


def setup_logging(log_level: str | None = None) -> None:
    """
    Configure structlog for JSON output with the following shape:
    {
        "timestamp": "...",
        "level": "...",
        "logger": "...",
        "message": "...",
        "task_id": "...",
        "project_id": "...",
        "agent_id": "...",
        "caller": "..."
    }
    """
    settings = get_settings()
    level = log_level or settings.log_level or "INFO"

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PosteriorReaderLoggerFactory(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        add_task_context,
        add_caller_info,
    ]

    structlog.configure(
        processors=[*shared_processors, structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer()],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "aiwa") -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger for the given name."""
    return structlog.get_logger(name)
