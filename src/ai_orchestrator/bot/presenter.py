"""Plain-text response formatting for Telegram commands."""

from __future__ import annotations

from dataclasses import dataclass

from ai_orchestrator.db.models import TaskRecord


CALLBACK_PREFIX_TASK_STATUS = "task_status:"


@dataclass(slots=True)
class TaskMenuItem:
    label: str
    callback_data: str


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


def format_help() -> str:
    """Render the current command help."""

    return (
        "Available commands:\n"
        "/task <description> - create a queued task.\n"
        "/tasks - browse recent tasks.\n"
        "/status <task_id> - show current task status.\n"
        "/approve <task_id> - approve a waiting plan.\n"
        "/reject <task_id> [reason] - reject a waiting plan.\n"
        "/help - show this command summary."
    )


def format_plan_approved(task: TaskRecord) -> str:
    """Render a plan approval response."""

    return f"{task.task_id} approved. Status: {task.status}."


def format_plan_rejected(task: TaskRecord) -> str:
    """Render a plan rejection response."""

    return f"{task.task_id} rejected. Status: {task.status}."


def format_tasks_menu(tasks: list[TaskRecord]) -> tuple[str, list[TaskMenuItem]]:
    """Render text and callback menu items for recent tasks."""

    if not tasks:
        return ("No tasks found.", [])

    items = [
        TaskMenuItem(
            label=_task_button_label(task),
            callback_data=f"{CALLBACK_PREFIX_TASK_STATUS}{task.task_id}",
        )
        for task in tasks
    ]
    return ("Select a task to open status:", items)


def parse_task_status_callback_data(callback_data: str) -> str | None:
    """Extract task id from callback payload."""

    if not callback_data.startswith(CALLBACK_PREFIX_TASK_STATUS):
        return None
    task_id = callback_data[len(CALLBACK_PREFIX_TASK_STATUS) :].strip()
    if not task_id:
        return None
    return task_id


def _task_button_label(task: TaskRecord) -> str:
    """Create a compact button label for one task."""

    max_title_length = 40
    title = task.source_text.strip()
    if len(title) > max_title_length:
        title = f"{title[: max_title_length - 3]}..."
    return f"{task.task_id} - {title}"
