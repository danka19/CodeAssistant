"""Worker-side entrypoints for phased runtime actions."""

from __future__ import annotations

from dataclasses import dataclass

from ai_orchestrator.db.models import TaskRecord
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.integrations.claude_runner import ClaudeRunnerExecutionError
from ai_orchestrator.integrations.codex_runner import CodexRunnerExecutionError
from ai_orchestrator.services.implementation_service import (
    ImplementationContextError,
    ImplementationResult,
    ImplementationService,
    PlanArtifactNotFoundError,
    RepositoryConfigNotFoundError,
    TaskNotImplementingError as ServiceTaskNotImplementingError,
)
from ai_orchestrator.services.planning_service import (
    InvalidRiskLevelError,
    PlanningContextError,
    PlanningResult,
    PlanningService,
    TaskNotPlanningError,
)
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


class InvalidWorkerRiskLevelError(WorkerLoopError):
    """Raised when the worker receives an unsupported planning risk level."""


@dataclass(slots=True)
class WorkerPreparationResult:
    """Returned after the worker prepares a task workspace."""

    task: TaskRecord
    workspace: WorkspacePreparationResult


@dataclass(slots=True)
class WorkerPlanningResult:
    """Returned after the worker completes the planning boundary."""

    task: TaskRecord
    planning: PlanningResult


@dataclass(slots=True)
class WorkerImplementationResult:
    """Returned after the worker completes Phase 4 implementation."""

    task: TaskRecord
    implementation: ImplementationResult


class WorkerLoop:
    """Phase 2 worker bridge for repository and worktree preparation."""

    VALID_RISK_LEVELS = frozenset({"low", "medium", "high"})

    def __init__(
        self,
        *,
        repository: TaskRepository,
        workspace_preparation_service: WorkspacePreparationService,
        planning_service: PlanningService,
        implementation_service: ImplementationService,
    ) -> None:
        self._repository = repository
        self._workspace_preparation_service = workspace_preparation_service
        self._planning_service = planning_service
        self._implementation_service = implementation_service

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

    def plan_task(
        self,
        *,
        task_id: str,
        risk_level: str,
    ) -> WorkerPlanningResult:
        """Run the Phase 3 Claude planner for a task already in planning."""

        if risk_level not in self.VALID_RISK_LEVELS:
            allowed = ", ".join(sorted(self.VALID_RISK_LEVELS))
            raise InvalidWorkerRiskLevelError(
                f"Invalid risk level '{risk_level}'. Expected one of: {allowed}.",
            )

        try:
            planning_result = self._planning_service.plan_task(
                task_id=task_id,
                risk_level=risk_level,
            )
        except (
            LookupError,
            TaskNotPlanningError,
            PlanningContextError,
            InvalidRiskLevelError,
            ClaudeRunnerExecutionError,
        ):
            raise
        return WorkerPlanningResult(task=planning_result.task, planning=planning_result)

    def implement_task(self, *, task_id: str) -> WorkerImplementationResult:
        """Run the Phase 4 Codex implementation boundary for one task."""

        task = self._repository.get_task(task_id)
        if task is None:
            raise LookupError(f"Unknown task id: {task_id}")
        if task.status != TaskStatus.IMPLEMENTING.value:
            raise TaskNotImplementingError(
                f"Task {task_id} must be implementing before Codex runs, got {task.status}.",
            )
        try:
            implementation_result = self._implementation_service.implement_task(task_id=task_id)
        except (
            LookupError,
            ServiceTaskNotImplementingError,
            ImplementationContextError,
            RepositoryConfigNotFoundError,
            PlanArtifactNotFoundError,
            CodexRunnerExecutionError,
        ):
            raise
        return WorkerImplementationResult(
            task=implementation_result.task,
            implementation=implementation_result,
        )


class TaskNotImplementingError(WorkerLoopError):
    """Raised when a worker action expects an implementing task."""
