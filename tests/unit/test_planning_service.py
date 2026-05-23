from pathlib import Path

import pytest

from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.integrations.claude_runner import ClaudeRunResult, ClaudeRunnerExecutionError
from ai_orchestrator.services.planning_service import (
    InvalidRiskLevelError,
    PlanningService,
    TaskNotPlanningError,
)
from ai_orchestrator.shared.enums import TaskStatus
from tests.support import make_runtime_test_dir, remove_runtime_test_dir


class _FakeClaudeRunner:
    def __init__(
        self, *, result: ClaudeRunResult | None = None, error: Exception | None = None
    ) -> None:
        self.result = result
        self.error = error
        self.calls: list[tuple[str, Path]] = []

    def run_planning_prompt(self, *, prompt: str, worktree_path: Path) -> ClaudeRunResult:
        self.calls.append((prompt, worktree_path))
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result


def test_plan_task_writes_plan_and_waits_for_medium_risk_approval() -> None:
    runtime_dir = make_runtime_test_dir("planning-service-medium")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-plan-1",
            source_text="Add planner bridge",
            status="planning",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        repository.assign_workspace(
            task_id=task.task_id,
            repo_alias="codeassistant",
            branch_name="agent/task-plan-1-add-planner-bridge",
            worktree_path=str(runtime_dir / "worktrees" / task.task_id),
            updated_at="2026-05-23T00:00:00Z",
        )
        (runtime_dir / "worktrees" / task.task_id).mkdir(parents=True, exist_ok=True)
        fake_runner = _FakeClaudeRunner(
            result=ClaudeRunResult(
                command=["claude", "-p", "prompt"],
                exit_code=0,
                stdout="# Plan\n\n- Step 1\n",
                stderr="",
            )
        )
        service = PlanningService(
            repository=repository,
            claude_runner=fake_runner,  # type: ignore[arg-type]
            runs_dir=runtime_dir / "runs",
        )

        result = service.plan_task(task_id=task.task_id, risk_level="medium")
        stored_task = repository.get_task(task.task_id)
        events = repository.list_events(task.task_id)
        artifact_text = result.artifact_path.read_text(encoding="utf-8")
        log_exists = result.log_path.exists()
        input_text = (runtime_dir / "runs" / task.task_id / "input.md").read_text(encoding="utf-8")
        planning_prompt = fake_runner.calls[0][0]
        planning_log = result.log_path.read_text(encoding="utf-8")
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert result.approval_required is True
    assert result.artifact_path.name == "plan.md"
    assert stored_task is not None
    assert stored_task.status == TaskStatus.WAITING_PLAN_APPROVAL.value
    assert artifact_text.startswith("# Plan")
    assert log_exists is True
    assert "## Request" in input_text
    assert "Main planner input:" in planning_prompt
    assert "Add planner bridge" not in planning_prompt
    assert "[prompt omitted]" in planning_log
    assert events[-1].event_type == "status_transition"


def test_plan_task_writes_architecture_plan_for_high_risk() -> None:
    runtime_dir = make_runtime_test_dir("planning-service-high")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-plan-2",
            source_text="Refactor the architecture",
            status="planning",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        repository.assign_workspace(
            task_id=task.task_id,
            repo_alias="codeassistant",
            branch_name="agent/task-plan-2-refactor-architecture",
            worktree_path=str(runtime_dir / "worktrees" / task.task_id),
            updated_at="2026-05-23T00:00:00Z",
        )
        (runtime_dir / "worktrees" / task.task_id).mkdir(parents=True, exist_ok=True)
        service = PlanningService(
            repository=repository,
            claude_runner=_FakeClaudeRunner(
                result=ClaudeRunResult(
                    command=["claude", "-p", "prompt"],
                    exit_code=0,
                    stdout="# Architecture plan\n",
                    stderr="",
                )
            ),  # type: ignore[arg-type]
            runs_dir=runtime_dir / "runs",
        )

        result = service.plan_task(task_id=task.task_id, risk_level="high")
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert result.artifact_path.name == "architecture_plan.md"
    assert result.approval_required is True


def test_plan_task_moves_low_risk_task_to_implementing() -> None:
    runtime_dir = make_runtime_test_dir("planning-service-low")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-plan-3",
            source_text="Fix typo",
            status="planning",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        repository.assign_workspace(
            task_id=task.task_id,
            repo_alias="codeassistant",
            branch_name="agent/task-plan-3-fix-typo",
            worktree_path=str(runtime_dir / "worktrees" / task.task_id),
            updated_at="2026-05-23T00:00:00Z",
        )
        (runtime_dir / "worktrees" / task.task_id).mkdir(parents=True, exist_ok=True)
        service = PlanningService(
            repository=repository,
            claude_runner=_FakeClaudeRunner(
                result=ClaudeRunResult(
                    command=["claude", "-p", "prompt"],
                    exit_code=0,
                    stdout="# Plan\n\n- Fix typo\n",
                    stderr="",
                )
            ),  # type: ignore[arg-type]
            runs_dir=runtime_dir / "runs",
        )

        result = service.plan_task(task_id=task.task_id, risk_level="low")
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert result.task.status == TaskStatus.IMPLEMENTING.value
    assert result.approval_required is False


def test_plan_task_requires_planning_state() -> None:
    runtime_dir = make_runtime_test_dir("planning-service-status")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-plan-4",
            source_text="Already queued",
            status="queued",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        service = PlanningService(
            repository=repository,
            claude_runner=_FakeClaudeRunner(
                result=ClaudeRunResult(
                    command=["claude", "-p", "prompt"],
                    exit_code=0,
                    stdout="# Plan\n",
                    stderr="",
                )
            ),  # type: ignore[arg-type]
            runs_dir=runtime_dir / "runs",
        )

        with pytest.raises(TaskNotPlanningError):
            service.plan_task(task_id=task.task_id, risk_level="medium")
    finally:
        remove_runtime_test_dir(runtime_dir)


def test_plan_task_marks_task_failed_when_runner_fails() -> None:
    runtime_dir = make_runtime_test_dir("planning-service-failure")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-plan-5",
            source_text="Fail planning",
            status="planning",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        repository.assign_workspace(
            task_id=task.task_id,
            repo_alias="codeassistant",
            branch_name="agent/task-plan-5-fail-planning",
            worktree_path=str(runtime_dir / "worktrees" / task.task_id),
            updated_at="2026-05-23T00:00:00Z",
        )
        (runtime_dir / "worktrees" / task.task_id).mkdir(parents=True, exist_ok=True)
        runner_error = ClaudeRunnerExecutionError(
            "Claude exited with code 1.",
            result=ClaudeRunResult(
                command=["claude", "-p", "prompt"],
                exit_code=1,
                stdout="",
                stderr="boom",
            ),
        )
        service = PlanningService(
            repository=repository,
            claude_runner=_FakeClaudeRunner(error=runner_error),  # type: ignore[arg-type]
            runs_dir=runtime_dir / "runs",
        )

        with pytest.raises(ClaudeRunnerExecutionError):
            service.plan_task(task_id=task.task_id, risk_level="medium")
        stored_task = repository.get_task(task.task_id)
        events = repository.list_events(task.task_id)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert stored_task is not None
    assert stored_task.status == TaskStatus.FAILED.value
    assert events[-1].event_type == "worker_failed"


def test_plan_task_rejects_invalid_risk_level() -> None:
    runtime_dir = make_runtime_test_dir("planning-service-invalid-risk")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-plan-6",
            source_text="Invalid risk check",
            status="planning",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        repository.assign_workspace(
            task_id=task.task_id,
            repo_alias="codeassistant",
            branch_name="agent/task-plan-6-invalid-risk",
            worktree_path=str(runtime_dir / "worktrees" / task.task_id),
            updated_at="2026-05-23T00:00:00Z",
        )
        (runtime_dir / "worktrees" / task.task_id).mkdir(parents=True, exist_ok=True)
        service = PlanningService(
            repository=repository,
            claude_runner=_FakeClaudeRunner(
                result=ClaudeRunResult(
                    command=["claude", "-p", "prompt"],
                    exit_code=0,
                    stdout="# Plan\n",
                    stderr="",
                )
            ),  # type: ignore[arg-type]
            runs_dir=runtime_dir / "runs",
        )

        with pytest.raises(InvalidRiskLevelError, match="Invalid risk level"):
            service.plan_task(task_id=task.task_id, risk_level="urgent")
    finally:
        remove_runtime_test_dir(runtime_dir)
