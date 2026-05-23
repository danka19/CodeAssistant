"""Worker-side entrypoints for phased runtime actions."""

from __future__ import annotations

from dataclasses import dataclass

from ai_orchestrator.db.models import TaskRecord
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.services.workspace_preparation_service import (
    RepositoryAliasNotFoundError,
    TaskLookupError,
    WorkspacePreparationError,
    WorkspacePreparationResult,
    WorkspacePreparationService,
)
from ai_orchestrator.shared.clock import utc_now_iso
from ai_orchestrator.shared.enums import TaskStatus


class WorkerLoopError(Exception):
    """Base worker-loop error."""


class TaskNotQueuedError(WorkerLoopError):
    """Raised when a worker action expects a queued task."""


@dataclass(slots=True)
class WorkerPreparationResult:
    """Returned after the worker prepares a task workspace."""

    task: TaskRecord
    workspace: WorkspacePreparationResult


class WorkerLoop:
    """Phase 2 worker bridge for repository and worktree preparation."""

    def __init__(
        self,
        *,
        repository: TaskRepository,
        workspace_preparation_service: WorkspacePreparationService,
    ) -> None:
        self._repository = repository
        self._workspace_preparation_service = workspace_preparation_service

    def prepare_task_workspace(
        self,
        *,
        task_id: str,
        repo_alias: str,
    ) -> WorkerPreparationResult:
        """Prepare a queued task for the next planning-phase boundary."""

        task = self._repository.get_task(task_id)
        if task is None:
            raise TaskLookupError(task_id)
        if task.status != TaskStatus.QUEUED.value:
            raise TaskNotQueuedError(
                f"Task {task_id} must be queued before workspace preparation, got {task.status}.",
            )

        try:
            workspace_result = self._workspace_preparation_service.prepare_workspace(
                task_id=task_id,
                repo_alias=repo_alias,
            )
        except TaskLookupError:
            raise
        except (RepositoryAliasNotFoundError, WorkspacePreparationError) as error:
            failed_task = self._repository.update_task_status(
                task_id=task_id,
                status=TaskStatus.FAILED.value,
                updated_at=utc_now_iso(),
            )
            self._repository.add_event(
                task_id=task_id,
                event_type="worker_failed",
                payload={
                    "step": "workspace_preparation",
                    "error_type": error.__class__.__name__,
                    "message": str(error),
                    "previous_status": task.status,
                    "status": failed_task.status,
                },
                created_at=utc_now_iso(),
            )
            raise

        updated_task = self._repository.update_task_status(
            task_id=task_id,
            status=TaskStatus.PLANNING.value,
            updated_at=utc_now_iso(),
        )
        self._repository.add_event(
            task_id=task_id,
            event_type="status_transition",
            payload={
                "from_status": task.status,
                "to_status": updated_task.status,
                "step": "workspace_preparation",
            },
            created_at=utc_now_iso(),
        )
        return WorkerPreparationResult(task=updated_task, workspace=workspace_result)
