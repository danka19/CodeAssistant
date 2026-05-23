"""Plain-text response formatting for Telegram commands."""

from __future__ import annotations

from ai_orchestrator.db.models import TaskRecord


def format_task_created(task: TaskRecord) -> str:
    """Render a short response for a newly accepted task."""

    return f"Task {task.task_id} accepted. Status: {task.status}."


def format_task_status(task: TaskRecord) -> str:
    """Render a short status response."""

    return f"{task.task_id}: {task.status}."


def format_validation_error(message: str) -> str:
    """Render a user-facing validation error."""

    return f"Validation error: {message}"


def format_not_found(task_id: str) -> str:
    """Render a task-not-found response."""

    return f"Task {task_id} not found."


def format_unauthorized() -> str:
    """Render a short unauthorized response."""

    return "Unauthorized user."
