"""Phase 4 implementation workflow."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ai_orchestrator.config.loader import AppConfig
from ai_orchestrator.db.models import TaskRecord
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.integrations.codex_runner import (
    CodexRunResult,
    CodexRunner,
    CodexRunnerExecutionError,
)
from ai_orchestrator.shared.clock import utc_now_iso
from ai_orchestrator.shared.enums import TaskStatus


class ImplementationServiceError(Exception):
    """Base implementation service error."""


class TaskNotImplementingError(ImplementationServiceError):
    """Raised when implementation is attempted from the wrong task state."""


class ImplementationContextError(ImplementationServiceError):
    """Raised when task metadata is insufficient for implementation."""


class RepositoryConfigNotFoundError(ImplementationServiceError):
    """Raised when task repo alias is missing from config."""


class PlanArtifactNotFoundError(ImplementationServiceError):
    """Raised when neither approved planning artifact exists."""


@dataclass(slots=True)
class CheckResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str


@dataclass(slots=True)
class ImplementationResult:
    task: TaskRecord
    implementation_log_path: Path
    test_log_path: Path
    summary_path: Path
    commit_sha: str
    checks_run: list[str]


@dataclass(slots=True)
class ImplementationService:
    repository: TaskRepository
    config: AppConfig
    codex_runner: CodexRunner
    runs_dir: Path

    def implement_task(self, *, task_id: str) -> ImplementationResult:
        task = self.repository.get_task(task_id)
        if task is None:
            raise LookupError(f"Unknown task id: {task_id}")
        if task.status != TaskStatus.IMPLEMENTING.value:
            raise TaskNotImplementingError(
                f"Task {task_id} must be implementing before Codex runs, got {task.status}.",
            )
        if not task.repo_alias or not task.branch_name or not task.worktree_path:
            raise ImplementationContextError(
                f"Task {task_id} is missing repository/worktree metadata required for implementation.",
            )
        repo_config = self.config.repositories.get(task.repo_alias)
        if repo_config is None:
            raise RepositoryConfigNotFoundError(task.repo_alias)

        worktree_path = Path(task.worktree_path)
        run_dir = self.runs_dir / task.task_id
        run_dir.mkdir(parents=True, exist_ok=True)
        plan_path = self._resolve_plan_artifact(run_dir=run_dir)
        implementation_log_path = run_dir / "implementation.log"
        test_log_path = run_dir / "test.log"
        summary_path = run_dir / "summary.md"

        self.repository.add_event(
            task_id=task.task_id,
            event_type="implementation_started",
            payload={
                "status": task.status,
                "plan_path": str(plan_path),
                "worktree_path": str(worktree_path),
            },
            created_at=utc_now_iso(),
        )
        current_status = task.status
        try:
            codex_result = self.codex_runner.run_implementation_prompt(
                prompt=self._build_implementation_prompt(task=task, plan_path=plan_path),
                worktree_path=worktree_path,
            )
            self._write_implementation_log(
                implementation_log_path=implementation_log_path, result=codex_result
            )
            git_status = self._run_command(
                command=("git", "status", "--short"),
                cwd=worktree_path,
            )
            if not git_status.stdout.strip():
                raise ImplementationServiceError("Codex produced no working tree changes.")

            testing_task = self.repository.update_task_status(
                task_id=task.task_id,
                status=TaskStatus.TESTING.value,
                updated_at=utc_now_iso(),
            )
            self.repository.add_event(
                task_id=task.task_id,
                event_type="status_transition",
                payload={
                    "from_status": task.status,
                    "to_status": testing_task.status,
                    "step": "implementation_checks",
                },
                created_at=utc_now_iso(),
            )
            current_status = testing_task.status
            check_results = self._run_checks(
                commands=repo_config.test_commands,
                cwd=worktree_path,
            )
            self._write_test_log(test_log_path=test_log_path, checks=check_results)
            failing_check = next((item for item in check_results if item.exit_code != 0), None)
            if failing_check is not None:
                raise ImplementationServiceError(
                    f"Check failed: {failing_check.command} (exit {failing_check.exit_code}).",
                )

            self._run_command(command=("git", "add", "-A"), cwd=worktree_path)
            git_diff_stat = self._run_command(
                command=("git", "diff", "--cached", "--stat"),
                cwd=worktree_path,
            )
            self._run_command(
                command=("git", "commit", "-m", f"task({task.task_id}): implement approved plan"),
                cwd=worktree_path,
            )
            commit_sha = self._run_command(
                command=("git", "rev-parse", "HEAD"),
                cwd=worktree_path,
            ).stdout.strip()
            creating_pr_task = self.repository.update_task_status(
                task_id=task.task_id,
                status=TaskStatus.CREATING_PR.value,
                updated_at=utc_now_iso(),
            )
            self.repository.add_event(
                task_id=task.task_id,
                event_type="status_transition",
                payload={
                    "from_status": testing_task.status,
                    "to_status": creating_pr_task.status,
                    "step": "implementation_handoff",
                },
                created_at=utc_now_iso(),
            )
            current_status = creating_pr_task.status
            self._write_summary(
                summary_path=summary_path,
                task=task,
                plan_path=plan_path,
                git_status=git_status.stdout,
                git_diff_stat=git_diff_stat.stdout,
                checks=check_results,
                commit_sha=commit_sha,
            )
            self.repository.add_event(
                task_id=task.task_id,
                event_type="implementation_completed",
                payload={
                    "status": creating_pr_task.status,
                    "implementation_log_path": str(implementation_log_path),
                    "test_log_path": str(test_log_path),
                    "summary_path": str(summary_path),
                    "commit_sha": commit_sha,
                },
                created_at=utc_now_iso(),
            )
            return ImplementationResult(
                task=creating_pr_task,
                implementation_log_path=implementation_log_path,
                test_log_path=test_log_path,
                summary_path=summary_path,
                commit_sha=commit_sha,
                checks_run=[entry.command for entry in check_results],
            )
        except (
            CodexRunnerExecutionError,
            ImplementationServiceError,
            subprocess.SubprocessError,
        ) as error:
            failed_task = self.repository.update_task_status(
                task_id=task.task_id,
                status=TaskStatus.FAILED.value,
                updated_at=utc_now_iso(),
            )
            self.repository.add_event(
                task_id=task.task_id,
                event_type="worker_failed",
                payload={
                    "step": "implementation",
                    "error_type": error.__class__.__name__,
                    "message": str(error),
                    "previous_status": current_status,
                    "status": failed_task.status,
                    "implementation_log_path": str(implementation_log_path),
                    "test_log_path": str(test_log_path),
                },
                created_at=utc_now_iso(),
            )
            raise

    @staticmethod
    def _resolve_plan_artifact(*, run_dir: Path) -> Path:
        plan_path = run_dir / "plan.md"
        architecture_plan_path = run_dir / "architecture_plan.md"
        if plan_path.exists():
            return plan_path
        if architecture_plan_path.exists():
            return architecture_plan_path
        raise PlanArtifactNotFoundError(
            f"Missing approved plan artifact in {run_dir}: expected plan.md or architecture_plan.md.",
        )

    @staticmethod
    def _build_implementation_prompt(*, task: TaskRecord, plan_path: Path) -> str:
        return "\n".join(
            [
                "You are Codex Implementer for the AI Dev Orchestrator MVP.",
                f"Task id: {task.task_id}",
                f"Approved plan: {plan_path}",
                "",
                "Read the plan file and implement exactly that scope in this worktree.",
                "Update or add tests for changed behavior.",
                "Avoid unrelated edits.",
                "Do not push and do not create a PR.",
                "After editing, provide a concise implementation summary.",
            ]
        )

    @staticmethod
    def _write_implementation_log(*, implementation_log_path: Path, result: CodexRunResult) -> None:
        implementation_log_path.write_text(
            "\n".join(
                [
                    f"command: {' '.join(result.command[:2])} [prompt omitted]",
                    f"exit_code: {result.exit_code}",
                    "",
                    "[stdout]",
                    result.stdout.rstrip(),
                    "",
                    "[stderr]",
                    result.stderr.rstrip(),
                    "",
                ]
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _run_command(
        *,
        command: Sequence[str] | str,
        cwd: Path,
        shell: bool = False,
    ) -> CheckResult:
        completed = subprocess.run(
            command if isinstance(command, str) else list(command),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
            shell=shell,
        )
        return CheckResult(
            command=command if isinstance(command, str) else " ".join(command),
            exit_code=completed.returncode,
            stdout=completed.stdout.rstrip(),
            stderr=completed.stderr.rstrip(),
        )

    def _run_checks(self, *, commands: list[str], cwd: Path) -> list[CheckResult]:
        results: list[CheckResult] = []
        for command in commands:
            results.append(self._run_command(command=command, cwd=cwd, shell=True))
        return results

    @staticmethod
    def _write_test_log(*, test_log_path: Path, checks: list[CheckResult]) -> None:
        lines: list[str] = []
        for check in checks:
            lines.extend(
                [
                    f"command: {check.command}",
                    f"exit_code: {check.exit_code}",
                    "[stdout]",
                    check.stdout,
                    "[stderr]",
                    check.stderr,
                    "",
                ]
            )
        test_log_path.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _write_summary(
        *,
        summary_path: Path,
        task: TaskRecord,
        plan_path: Path,
        git_status: str,
        git_diff_stat: str,
        checks: list[CheckResult],
        commit_sha: str,
    ) -> None:
        summary_path.write_text(
            "\n".join(
                [
                    f"# Task {task.task_id} Implementation Summary",
                    "",
                    f"- Plan artifact: {plan_path.name}",
                    f"- Branch: {task.branch_name}",
                    f"- Worktree: {task.worktree_path}",
                    f"- Commit: {commit_sha}",
                    "",
                    "## Git Status (--short)",
                    "",
                    "```text",
                    git_status.strip(),
                    "```",
                    "",
                    "## Git Diff (--stat)",
                    "",
                    "```text",
                    git_diff_stat.strip(),
                    "```",
                    "",
                    "## Checks",
                    "",
                    *[
                        f"- {'PASS' if check.exit_code == 0 else 'FAIL'}: {check.command} (exit {check.exit_code})"
                        for check in checks
                    ],
                    "",
                ]
            ),
            encoding="utf-8",
        )
