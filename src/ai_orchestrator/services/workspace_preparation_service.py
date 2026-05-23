"""Prepare repository caches and task worktrees for Phase 2."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ai_orchestrator.config.loader import AppConfig, RepositoryConfig
from ai_orchestrator.db.models import TaskRecord
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.shared.clock import utc_now_iso


class WorkspacePreparationError(Exception):
    """Base error for Phase 2 workspace preparation."""


class RepositoryAliasNotFoundError(WorkspacePreparationError):
    """Raised when the requested repository alias does not exist."""


class TaskLookupError(WorkspacePreparationError):
    """Raised when the requested task record does not exist."""


class PathSafetyError(WorkspacePreparationError):
    """Raised when repository paths escape configured roots."""


class RepositoryStateError(WorkspacePreparationError):
    """Raised when the cached repository is not safe to reuse."""


class WorkspaceConflictError(WorkspacePreparationError):
    """Raised when the target branch or worktree already exists."""


class GitCommandError(WorkspacePreparationError):
    """Raised when a git command exits with a non-zero code."""

    def __init__(self, result: "GitCommandResult") -> None:
        super().__init__(
            f"Git command failed with exit code {result.exit_code}: {' '.join(result.command)}",
        )
        self.result = result


@dataclass(slots=True)
class GitCommandResult:
    """Captured result for one git invocation."""

    command: tuple[str, ...]
    cwd: str | None
    exit_code: int
    stdout: str
    stderr: str


@dataclass(slots=True)
class WorkspacePreparationResult:
    """Summary of repository/worktree preparation for a task."""

    task: TaskRecord
    repo_path: Path
    worktree_path: Path
    branch_name: str


@dataclass(slots=True)
class WorkspacePreparationService:
    """Phase 2 service that prepares the repo cache and task worktree."""

    repository: TaskRepository
    config: AppConfig

    def prepare_workspace(self, *, task_id: str, repo_alias: str) -> WorkspacePreparationResult:
        """Clone or refresh the repository cache and create the task worktree."""

        task = self.repository.get_task(task_id)
        if task is None:
            raise TaskLookupError(task_id)

        repo_config = self._get_repository_config(repo_alias)
        repo_path = self._resolve_managed_path(
            root_path=Path(self.config.runtime.repos_dir),
            configured_path=Path(repo_config.local_path),
        )
        worktree_root = self._resolve_managed_path(
            root_path=Path(self.config.runtime.worktrees_dir),
            configured_path=Path(repo_config.worktree_root),
        )
        branch_name = build_task_branch_name(task.task_id, task.source_text)
        worktree_path = self._resolve_managed_path(
            root_path=worktree_root,
            configured_path=worktree_root / task.task_id,
        )
        clone_source = resolve_clone_source(repo_config.repo)

        if repo_path.exists():
            self._validate_existing_repository(
                task_id=task.task_id,
                repo_path=repo_path,
                clone_source=clone_source,
            )
        else:
            repo_path.parent.mkdir(parents=True, exist_ok=True)
            self._run_git_command(
                task_id=task.task_id,
                command=("git", "clone", clone_source, str(repo_path)),
                cwd=None,
            )

        self._run_git_command(
            task_id=task.task_id,
            command=("git", "fetch", "origin"),
            cwd=repo_path,
        )
        self._ensure_branch_available(
            task_id=task.task_id, repo_path=repo_path, branch_name=branch_name
        )

        worktree_root.mkdir(parents=True, exist_ok=True)
        if worktree_path.exists():
            raise WorkspaceConflictError(f"Worktree path already exists: {worktree_path}")

        self._run_git_command(
            task_id=task.task_id,
            command=(
                "git",
                "worktree",
                "add",
                "-b",
                branch_name,
                str(worktree_path),
                f"origin/{repo_config.default_branch}",
            ),
            cwd=repo_path,
        )

        timestamp = utc_now_iso()
        updated_task = self.repository.assign_workspace(
            task_id=task.task_id,
            repo_alias=repo_alias,
            branch_name=branch_name,
            worktree_path=str(worktree_path),
            updated_at=timestamp,
        )
        self.repository.add_event(
            task_id=task.task_id,
            event_type="workspace_prepared",
            payload={
                "repo_alias": repo_alias,
                "repo_path": str(repo_path),
                "branch_name": branch_name,
                "worktree_path": str(worktree_path),
            },
            created_at=timestamp,
        )
        return WorkspacePreparationResult(
            task=updated_task,
            repo_path=repo_path,
            worktree_path=worktree_path,
            branch_name=branch_name,
        )

    def _get_repository_config(self, repo_alias: str) -> RepositoryConfig:
        repo_config = self.config.repositories.get(repo_alias)
        if repo_config is None:
            raise RepositoryAliasNotFoundError(repo_alias)
        return repo_config

    def _validate_existing_repository(
        self,
        *,
        task_id: str,
        repo_path: Path,
        clone_source: str,
    ) -> None:
        if not (repo_path / ".git").exists():
            raise RepositoryStateError(f"Repository cache is not a git checkout: {repo_path}")

        remote_result = self._run_git_command(
            task_id=task_id,
            command=("git", "remote", "get-url", "origin"),
            cwd=repo_path,
        )
        remote_url = remote_result.stdout.strip()
        if not remote_url:
            raise RepositoryStateError(f"Repository cache has no origin remote: {repo_path}")
        if not remote_sources_match(expected=clone_source, actual=remote_url):
            raise RepositoryStateError(
                f"Repository cache origin mismatch: expected {clone_source}, got {remote_url}",
            )

        status_result = self._run_git_command(
            task_id=task_id,
            command=("git", "status", "--porcelain"),
            cwd=repo_path,
        )
        if status_result.stdout.strip():
            raise RepositoryStateError(f"Repository cache is dirty: {repo_path}")

    def _ensure_branch_available(self, *, task_id: str, repo_path: Path, branch_name: str) -> None:
        result = self._run_git_command(
            task_id=task_id,
            command=("git", "show-ref", "--verify", f"refs/heads/{branch_name}"),
            cwd=repo_path,
            allow_exit_codes={0, 1, 128},
        )
        if result.exit_code == 0:
            raise WorkspaceConflictError(f"Branch already exists: {branch_name}")

    def _run_git_command(
        self,
        *,
        task_id: str,
        command: Sequence[str],
        cwd: Path | None,
        allow_exit_codes: set[int] | None = None,
    ) -> GitCommandResult:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            text=True,
            check=False,
        )
        result = GitCommandResult(
            command=tuple(command),
            cwd=str(cwd) if cwd is not None else None,
            exit_code=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )
        self.repository.add_event(
            task_id=task_id,
            event_type="git_command",
            payload={
                "command": list(result.command),
                "cwd": result.cwd,
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            created_at=utc_now_iso(),
        )
        accepted_exit_codes = allow_exit_codes or {0}
        if result.exit_code not in accepted_exit_codes:
            raise GitCommandError(result)
        return result

    @staticmethod
    def _resolve_managed_path(*, root_path: Path, configured_path: Path) -> Path:
        resolved_root = root_path.resolve()
        resolved_path = configured_path.resolve()
        if not resolved_path.is_relative_to(resolved_root):
            raise PathSafetyError(
                f"Configured path escapes managed root: {configured_path} not under {root_path}",
            )
        return resolved_path


def build_task_branch_name(task_id: str, source_text: str) -> str:
    """Build the Phase 2 branch name from the task id and description."""

    normalized_slug = re.sub(r"[^a-z0-9]+", "-", source_text.lower()).strip("-")
    trimmed_slug = normalized_slug[:48].strip("-") or "task"
    return f"agent/{task_id}-{trimmed_slug}"


def resolve_clone_source(repository: str) -> str:
    """Resolve a configured repository value into a git clone source."""

    candidate = repository.strip()
    if "://" in candidate or candidate.startswith("git@"):
        return candidate

    candidate_path = Path(candidate)
    if candidate_path.is_absolute() or candidate.startswith(".") or candidate_path.exists():
        return candidate_path.resolve().as_uri()

    return f"https://github.com/{candidate}.git"


def remote_sources_match(*, expected: str, actual: str) -> bool:
    """Compare clone sources while tolerating local-path normalization."""

    if _looks_like_local_path(expected) and _looks_like_local_path(actual):
        return Path(expected).resolve() == Path(actual).resolve()
    return expected.strip() == actual.strip()


def _looks_like_local_path(value: str) -> bool:
    return "://" not in value and not value.startswith("git@")
