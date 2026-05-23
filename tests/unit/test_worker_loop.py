from dataclasses import dataclass

import pytest

from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.services.workspace_preparation_service import (
    RepositoryAliasNotFoundError,
    WorkspacePreparationResult,
)
from ai_orchestrator.worker.loop import TaskNotQueuedError, WorkerLoop
from tests.support import make_runtime_test_dir, remove_runtime_test_dir


@dataclass(slots=True)
class _FakeWorkspacePreparationService:
    result: WorkspacePreparationResult | None = None
    error: Exception | None = None
    calls: list[tuple[str, str]] | None = None

    def prepare_workspace(self, *, task_id: str, repo_alias: str) -> WorkspacePreparationResult:
        if self.calls is not None:
            self.calls.append((task_id, repo_alias))
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result


def test_prepare_task_workspace_transitions_task_to_planning() -> None:
    runtime_dir = make_runtime_test_dir("worker-prepare-success")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-worker-1",
            source_text="Prepare worker bridge",
            status="queued",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        workspace_result = WorkspacePreparationResult(
            task=task,
            repo_path=runtime_dir / "repos" / "sandbox",
            worktree_path=runtime_dir / "worktrees" / "sandbox" / task.task_id,
            branch_name="agent/task-worker-1-prepare-worker-bridge",
        )
        fake_service = _FakeWorkspacePreparationService(
            result=workspace_result,
            calls=[],
        )

        worker = WorkerLoop(
            repository=repository,
            workspace_preparation_service=fake_service,  # type: ignore[arg-type]
        )
        result = worker.prepare_task_workspace(
            task_id=task.task_id,
            repo_alias="sandbox",
        )
        stored_task = repository.get_task(task.task_id)
        events = repository.list_events(task.task_id)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert result.task.status == "planning"
    assert stored_task is not None
    assert stored_task.status == "planning"
    assert fake_service.calls == [("task-worker-1", "sandbox")]
    assert events[-1].event_type == "status_transition"


def test_prepare_task_workspace_marks_task_failed_when_workspace_preparation_fails() -> None:
    runtime_dir = make_runtime_test_dir("worker-prepare-failure")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-worker-2",
            source_text="Fail worker bridge",
            status="queued",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        fake_service = _FakeWorkspacePreparationService(
            error=RepositoryAliasNotFoundError("missing-repo"),
        )

        worker = WorkerLoop(
            repository=repository,
            workspace_preparation_service=fake_service,  # type: ignore[arg-type]
        )
        with pytest.raises(RepositoryAliasNotFoundError):
            worker.prepare_task_workspace(
                task_id=task.task_id,
                repo_alias="missing-repo",
            )
        stored_task = repository.get_task(task.task_id)
        events = repository.list_events(task.task_id)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert stored_task is not None
    assert stored_task.status == "failed"
    assert events[-1].event_type == "worker_failed"


def test_prepare_task_workspace_rejects_non_queued_task() -> None:
    runtime_dir = make_runtime_test_dir("worker-prepare-not-queued")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-worker-3",
            source_text="Already planning",
            status="planning",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        fake_service = _FakeWorkspacePreparationService(
            calls=[],
        )

        worker = WorkerLoop(
            repository=repository,
            workspace_preparation_service=fake_service,  # type: ignore[arg-type]
        )
        with pytest.raises(TaskNotQueuedError):
            worker.prepare_task_workspace(
                task_id=task.task_id,
                repo_alias="sandbox",
            )
    finally:
        remove_runtime_test_dir(runtime_dir)
