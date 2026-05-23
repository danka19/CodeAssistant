from pathlib import Path
from subprocess import CompletedProcess

import pytest

from ai_orchestrator.config.loader import (
    AppConfig,
    GitHubConfig,
    RepositoryConfig,
    RuntimeConfig,
    TelegramConfig,
)
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.services.workspace_preparation_service import (
    PathSafetyError,
    RepositoryStateError,
    WorkspacePreparationService,
    build_task_branch_name,
)
from tests.support import make_runtime_test_dir, remove_runtime_test_dir


def test_build_task_branch_name_slugifies_and_trims() -> None:
    branch_name = build_task_branch_name(
        "task-1234",
        "Implement GitHub/Repo manager!!! with a very long title that keeps going",
    )

    assert branch_name == "agent/task-1234-implement-github-repo-manager-with-a-very-long-t"


def test_prepare_workspace_clones_fetches_and_assigns_worktree(monkeypatch) -> None:
    runtime_dir = make_runtime_test_dir("workspace-prepare")
    try:
        remote_path = runtime_dir / "remote-source"
        remote_path.mkdir(parents=True, exist_ok=True)
        app_config = _build_config(runtime_dir=runtime_dir, remote_path=remote_path)
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        created_task = repository.create_task(
            task_id="task-123abc",
            source_text="Prepare repo manager workspace",
            status="queued",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        repo_cache = Path(app_config.repositories["sandbox"].local_path)
        worktree_path = (
            Path(app_config.repositories["sandbox"].worktree_root) / created_task.task_id
        )
        executed_commands: list[tuple[str, ...]] = []

        def fake_run(command, cwd=None, capture_output=True, text=True, check=False):
            del capture_output, text, check
            args = tuple(command)
            executed_commands.append(args)
            if args[:2] == ("git", "clone"):
                repo_cache.mkdir(parents=True, exist_ok=True)
                (repo_cache / ".git").mkdir()
                return CompletedProcess(command, 0, stdout="cloned\n", stderr="")
            if args[:3] == ("git", "fetch", "origin"):
                return CompletedProcess(command, 0, stdout="fetched\n", stderr="")
            if args[:3] == ("git", "show-ref", "--verify"):
                return CompletedProcess(command, 1, stdout="", stderr="")
            if args[:3] == ("git", "worktree", "add"):
                worktree_path.mkdir(parents=True, exist_ok=True)
                return CompletedProcess(command, 0, stdout="prepared\n", stderr="")
            raise AssertionError(f"Unexpected command: {args} cwd={cwd}")

        monkeypatch.setattr(
            "ai_orchestrator.services.workspace_preparation_service.subprocess.run",
            fake_run,
        )

        service = WorkspacePreparationService(repository=repository, config=app_config)
        result = service.prepare_workspace(
            task_id=created_task.task_id,
            repo_alias="sandbox",
        )
        stored_task = repository.get_task(created_task.task_id)
        events = repository.list_events(created_task.task_id)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert result.branch_name == "agent/task-123abc-prepare-repo-manager-workspace"
    assert result.repo_path == repo_cache.resolve()
    assert result.worktree_path == worktree_path.resolve()
    assert stored_task is not None
    assert stored_task.repo_alias == "sandbox"
    assert stored_task.branch_name == result.branch_name
    assert stored_task.worktree_path == str(result.worktree_path)
    assert executed_commands == [
        ("git", "clone", remote_path.resolve().as_uri(), str(repo_cache.resolve())),
        ("git", "fetch", "origin"),
        ("git", "show-ref", "--verify", f"refs/heads/{result.branch_name}"),
        (
            "git",
            "worktree",
            "add",
            "-b",
            result.branch_name,
            str(worktree_path.resolve()),
            "origin/main",
        ),
    ]
    assert [event.event_type for event in events].count("git_command") == 4
    assert events[-1].event_type == "workspace_prepared"


def test_prepare_workspace_rejects_paths_outside_managed_roots() -> None:
    runtime_dir = make_runtime_test_dir("workspace-path-safety")
    try:
        remote_path = runtime_dir / "remote-source"
        remote_path.mkdir(parents=True, exist_ok=True)
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        repository.create_task(
            task_id="task-unsafe",
            source_text="Unsafe workspace root",
            status="queued",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        app_config = _build_config(
            runtime_dir=runtime_dir,
            remote_path=remote_path,
            local_path=runtime_dir.parent / "outside-repo-cache",
        )

        service = WorkspacePreparationService(repository=repository, config=app_config)
        with pytest.raises(PathSafetyError):
            service.prepare_workspace(task_id="task-unsafe", repo_alias="sandbox")
    finally:
        remove_runtime_test_dir(runtime_dir)


def test_prepare_workspace_rejects_dirty_repository_cache(monkeypatch) -> None:
    runtime_dir = make_runtime_test_dir("workspace-dirty-cache")
    try:
        remote_path = runtime_dir / "remote-source"
        remote_path.mkdir(parents=True, exist_ok=True)
        app_config = _build_config(runtime_dir=runtime_dir, remote_path=remote_path)
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        repository.create_task(
            task_id="task-dirty",
            source_text="Dirty cache repo",
            status="queued",
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        repo_cache = Path(app_config.repositories["sandbox"].local_path)
        repo_cache.mkdir(parents=True, exist_ok=True)
        (repo_cache / ".git").mkdir()

        def fake_run(command, cwd=None, capture_output=True, text=True, check=False):
            del cwd, capture_output, text, check
            args = tuple(command)
            if args == ("git", "remote", "get-url", "origin"):
                return CompletedProcess(
                    command, 0, stdout=f"{remote_path.resolve().as_uri()}\n", stderr=""
                )
            if args == ("git", "status", "--porcelain"):
                return CompletedProcess(command, 0, stdout=" M README.md\n", stderr="")
            raise AssertionError(f"Unexpected command: {args}")

        monkeypatch.setattr(
            "ai_orchestrator.services.workspace_preparation_service.subprocess.run",
            fake_run,
        )

        service = WorkspacePreparationService(repository=repository, config=app_config)
        with pytest.raises(RepositoryStateError):
            service.prepare_workspace(task_id="task-dirty", repo_alias="sandbox")
    finally:
        remove_runtime_test_dir(runtime_dir)


def _build_config(
    *,
    runtime_dir: Path,
    remote_path: Path,
    local_path: Path | None = None,
) -> AppConfig:
    repos_root = runtime_dir / "repos"
    worktrees_root = runtime_dir / "worktrees"
    return AppConfig(
        runtime=RuntimeConfig(
            mode="systemd",
            user="ai-orchestrator",
            root_dir=str(runtime_dir),
            data_dir=str(runtime_dir / "data"),
            runs_dir=str(runtime_dir / "runs"),
            repos_dir=str(repos_root),
            worktrees_dir=str(worktrees_root),
        ),
        telegram=TelegramConfig(
            bot_token_env="TELEGRAM_BOT_TOKEN",
            allowed_user_ids=[1001],
        ),
        github=GitHubConfig(
            token_env="GITHUB_TOKEN",
            default_owner="danka19",
            pr_base_branch="main",
        ),
        repositories={
            "sandbox": RepositoryConfig(
                repo=str(remote_path.resolve()),
                default_branch="main",
                purpose="test",
                local_path=str((local_path or (repos_root / "sandbox")).resolve()),
                worktree_root=str((worktrees_root / "sandbox").resolve()),
                test_commands=["python -m pytest -q"],
            )
        },
    )
