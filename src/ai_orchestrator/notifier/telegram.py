"""Telegram notification stubs for the intake phase."""

from __future__ import annotations

from ai_orchestrator.bot.presenter import format_task_created, format_task_status
from ai_orchestrator.db.models import TaskRecord


class TelegramNotifier:
    """Thin wrapper around current text presenters."""

    def task_accepted_text(self, task: TaskRecord) -> str:
        return format_task_created(task)

    def task_status_text(self, task: TaskRecord) -> str:
        return format_task_status(task)
