import subprocess
from pathlib import Path

import pytest

from ai_orchestrator.config.loader import (
    AgentsConfig,
    AppConfig,
    ClaudePlannerConfig,
    CodexImplementerConfig,
    GitHubConfig,
    LimitsConfig,
    RepositoryConfig,
    RuntimeConfig,
    TelegramConfig,
)
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.integrations.codex_runner import CodexRunResult
from ai_orchestrator.services.implementation_service import (
    ImplementationService,
    ImplementationServiceError,
)
from tests.support import make_runtime_test_dir, remove_runtime_test_dir


class _FakeCodexRunner:
    def __init__(self, worktree_path: Path) -> None:
        self._worktree_path = worktree_path

    def run_implementation_prompt(self, *, prompt: str, worktree_path: Path) -> CodexRunResult:
        assert worktree_path == self._worktree_path
        (worktree_path / "feature.txt").write_text("implemented\n", encoding="utf-8")
        return CodexRunResult(
            command=["codex", "exec", prompt], exit_code=0, stdout="ok", stderr=""
        )


def _make_config(*, repo_path: Path, worktree_path: Path, test_commands: list[str]) -> AppConfig:
    return AppConfig(
        runtime=RuntimeConfig(
            mode="systemd",
            user="ai-orchestrator",
            root_dir=str(repo_path.parent),
            data_dir=str(repo_path.parent / "data"),
            runs_dir=str(repo_path.parent / "runs"),
            repos_dir=str(repo_path.parent / "repos"),
            worktrees_dir=str(repo_path.parent / "worktrees"),
        ),
        telegram=TelegramConfig(bot_token_env="TELEGRAM_BOT_TOKEN", allowed_user_ids=[]),
        github=GitHubConfig(token_env="GITHUB_TOKEN", default_owner="owner", pr_base_branch="main"),
        repositories={
            "codeassistant": RepositoryConfig(
                repo="owner/repo",
                default_branch="main",
                purpose="tests",
                local_path=str(repo_path),
                worktree_root=str(worktree_path.parent),
                test_commands=test_commands,
            )
        },
        agents=AgentsConfig(
            claude_planner=ClaudePlannerConfig(command="claude"),
            codex_implementer=CodexImplementerConfig(command="codex"),
        ),
        limits=LimitsConfig(command_timeout_seconds=60),
    )


def _run(command: list[str], cwd: Path) -> None:
    completed = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr


def test_implementation_service_creates_commit_after_checks_pass() -> None:
    runtime_dir = make_runtime_test_dir("implementation-service-success")
    try:
        worktree_path = runtime_dir / "worktree"
        worktree_path.mkdir(parents=True, exist_ok=True)
        _run(["git", "init"], cwd=worktree_path)
        _run(["git", "config", "user.email", "tests@example.com"], cwd=worktree_path)
        _run(["git", "config", "user.name", "Tests"], cwd=worktree_path)
        (worktree_path / "seed.txt").write_text("seed\n", encoding="utf-8")
        _run(["git", "add", "-A"], cwd=worktree_path)
        _run(["git", "commit", "-m", "seed"], cwd=worktree_path)

        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-impl-1",
            source_text="Implement feature",
            status="implementing",
            requested_by=1001,
            created_at="2026-05-24T00:00:00Z",
            updated_at="2026-05-24T00:00:00Z",
        )
        repository.assign_workspace(
            task_id=task.task_id,
            repo_alias="codeassistant",
            branch_name="agent/task-impl-1-implement-feature",
            worktree_path=str(worktree_path),
            updated_at="2026-05-24T00:00:00Z",
        )
        run_dir = runtime_dir / "runs" / task.task_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "plan.md").write_text("# plan\n", encoding="utf-8")

        config = _make_config(
            repo_path=runtime_dir / "repos" / "repo",
            worktree_path=worktree_path,
            test_commands=["python -c \"print('ok')\""],
        )
        service = ImplementationService(
            repository=repository,
            config=config,
            codex_runner=_FakeCodexRunner(worktree_path),  # type: ignore[arg-type]
            runs_dir=runtime_dir / "runs",
        )

        result = service.implement_task(task_id=task.task_id)
        stored_task = repository.get_task(task.task_id)
        events = repository.list_events(task.task_id)
        summary_text = result.summary_path.read_text(encoding="utf-8")
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert result.commit_sha
    assert result.task.status == "creating_pr"
    assert stored_task is not None
    assert stored_task.status == "creating_pr"
    assert result.implementation_log_path.name == "implementation.log"
    assert result.test_log_path.name == "test.log"
    assert result.summary_path.name == "summary.md"
    assert "feature.txt" in summary_text
    transition_events = [event for event in events if event.event_type == "status_transition"]
    assert len(transition_events) >= 2


def test_implementation_service_marks_failed_when_check_fails() -> None:
    runtime_dir = make_runtime_test_dir("implementation-service-check-fail")
    try:
        worktree_path = runtime_dir / "worktree"
        worktree_path.mkdir(parents=True, exist_ok=True)
        _run(["git", "init"], cwd=worktree_path)
        _run(["git", "config", "user.email", "tests@example.com"], cwd=worktree_path)
        _run(["git", "config", "user.name", "Tests"], cwd=worktree_path)
        (worktree_path / "seed.txt").write_text("seed\n", encoding="utf-8")
        _run(["git", "add", "-A"], cwd=worktree_path)
        _run(["git", "commit", "-m", "seed"], cwd=worktree_path)

        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        task = repository.create_task(
            task_id="task-impl-2",
            source_text="Implement feature",
            status="implementing",
            requested_by=1001,
            created_at="2026-05-24T00:00:00Z",
            updated_at="2026-05-24T00:00:00Z",
        )
        repository.assign_workspace(
            task_id=task.task_id,
            repo_alias="codeassistant",
            branch_name="agent/task-impl-2-implement-feature",
            worktree_path=str(worktree_path),
            updated_at="2026-05-24T00:00:00Z",
        )
        run_dir = runtime_dir / "runs" / task.task_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "plan.md").write_text("# plan\n", encoding="utf-8")

        config = _make_config(
            repo_path=runtime_dir / "repos" / "repo",
            worktree_path=worktree_path,
            test_commands=['python -c "import sys; sys.exit(1)"'],
        )
        service = ImplementationService(
            repository=repository,
            config=config,
            codex_runner=_FakeCodexRunner(worktree_path),  # type: ignore[arg-type]
            runs_dir=runtime_dir / "runs",
        )

        with pytest.raises(ImplementationServiceError):
            service.implement_task(task_id=task.task_id)
        failed_task = repository.get_task(task.task_id)
        events = repository.list_events(task.task_id)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert failed_task is not None
    assert failed_task.status == "failed"
    assert events[-2].event_type == "status_transition"
    assert events[-1].event_type == "worker_failed"
