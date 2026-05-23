"""Task intake application logic."""

from __future__ import annotations

from dataclasses import dataclass

from ai_orchestrator.db.models import TaskRecord
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.shared.clock import utc_now_iso
from ai_orchestrator.shared.enums import TaskStatus
from ai_orchestrator.shared.ids import generate_task_id


class IntakeServiceError(Exception):
    """Base intake service error."""


class UnauthorizedUserError(IntakeServiceError):
    """Raised when a Telegram user is not allowed."""


class ValidationError(IntakeServiceError):
    """Raised when command input is invalid."""


class TaskNotFoundError(IntakeServiceError):
    """Raised when a task id does not exist."""


@dataclass(slots=True)
class IntakeService:
    """Minimal Phase 1 task intake behavior."""

    repository: TaskRepository
    allowed_user_ids: list[int]

    def create_task(self, *, user_id: int, source_text: str) -> TaskRecord:
        """Create a queued task and record an intake event."""

        self._ensure_authorized(user_id)
        cleaned_text = source_text.strip()
        if not cleaned_text:
            raise ValidationError("`/task` requires a task description.")

        timestamp = utc_now_iso()
        task = self.repository.create_task(
            task_id=generate_task_id(),
            source_text=cleaned_text,
            status=TaskStatus.QUEUED.value,
            requested_by=user_id,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self.repository.add_event(
            task_id=task.task_id,
            event_type="task_queued",
            payload={
                "requested_by": user_id,
                "source_text": cleaned_text,
                "status": task.status,
            },
            created_at=timestamp,
        )
        return task

    def get_task_status(self, *, user_id: int, task_id: str) -> TaskRecord:
        """Return the current task state for an allowed user."""

        self._ensure_authorized(user_id)
        normalized_task_id = task_id.strip()
        if not normalized_task_id:
            raise ValidationError("`/status` requires a task id.")

        task = self.repository.get_task(normalized_task_id)
        if task is None:
            raise TaskNotFoundError(normalized_task_id)
        return task

    def _ensure_authorized(self, user_id: int) -> None:
        if user_id not in self.allowed_user_ids:
            raise UnauthorizedUserError(user_id)
