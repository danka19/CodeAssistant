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


class TaskApprovalStateError(IntakeServiceError):
    """Raised when an approval action is attempted from the wrong state."""


@dataclass(slots=True)
class IntakeService:
    """Minimal Phase 1 task intake behavior."""

    repository: TaskRepository
    allowed_user_ids: list[int]

    def create_task(self, *, user_id: int, source_text: str) -> TaskRecord:
        """Create a queued task and record an intake event."""

        self.ensure_authorized(user_id=user_id)
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

        self.ensure_authorized(user_id=user_id)
        normalized_task_id = task_id.strip()
        if not normalized_task_id:
            raise ValidationError("`/status` requires a task id.")

        task = self.repository.get_task(normalized_task_id)
        if task is None:
            raise TaskNotFoundError(normalized_task_id)
        return task

    def list_tasks(self, *, user_id: int, limit: int = 10) -> list[TaskRecord]:
        """Return recent tasks for an allowed user."""

        self.ensure_authorized(user_id=user_id)
        return self.repository.list_tasks(limit=limit)

    def approve_plan(self, *, user_id: int, task_id: str) -> TaskRecord:
        """Approve a task plan that is waiting for manual approval."""

        self.ensure_authorized(user_id=user_id)
        task = self._get_task_for_approval(task_id=task_id, command_name="/approve")
        timestamp = utc_now_iso()
        updated_task = self.repository.update_task_status(
            task_id=task.task_id,
            status=TaskStatus.IMPLEMENTING.value,
            updated_at=timestamp,
        )
        self.repository.add_event(
            task_id=task.task_id,
            event_type="plan_approved",
            payload={
                "approved_by": user_id,
                "from_status": task.status,
                "to_status": updated_task.status,
            },
            created_at=timestamp,
        )
        self.repository.add_event(
            task_id=task.task_id,
            event_type="status_transition",
            payload={
                "from_status": task.status,
                "to_status": updated_task.status,
                "step": "plan_approval",
            },
            created_at=timestamp,
        )
        return updated_task

    def reject_plan(self, *, user_id: int, task_id: str, reason: str | None = None) -> TaskRecord:
        """Reject a task plan that is waiting for manual approval."""

        self.ensure_authorized(user_id=user_id)
        task = self._get_task_for_approval(task_id=task_id, command_name="/reject")
        timestamp = utc_now_iso()
        updated_task = self.repository.update_task_status(
            task_id=task.task_id,
            status=TaskStatus.PLAN_REJECTED.value,
            updated_at=timestamp,
        )
        self.repository.add_event(
            task_id=task.task_id,
            event_type="plan_rejected",
            payload={
                "rejected_by": user_id,
                "reason": (reason or "").strip(),
                "from_status": task.status,
                "to_status": updated_task.status,
            },
            created_at=timestamp,
        )
        self.repository.add_event(
            task_id=task.task_id,
            event_type="status_transition",
            payload={
                "from_status": task.status,
                "to_status": updated_task.status,
                "step": "plan_rejection",
            },
            created_at=timestamp,
        )
        return updated_task

    def ensure_authorized(self, *, user_id: int) -> None:
        """Validate that the Telegram user is allowed to use the intake bot."""

        if user_id not in self.allowed_user_ids:
            raise UnauthorizedUserError(user_id)

    def _get_task_for_approval(self, *, task_id: str, command_name: str) -> TaskRecord:
        normalized_task_id = task_id.strip()
        if not normalized_task_id:
            raise ValidationError(f"`{command_name}` requires a task id.")
        task = self.repository.get_task(normalized_task_id)
        if task is None:
            raise TaskNotFoundError(normalized_task_id)
        if task.status != TaskStatus.WAITING_PLAN_APPROVAL.value:
            raise TaskApprovalStateError(
                f"Task {normalized_task_id} is not waiting for plan approval.",
            )
        return task
