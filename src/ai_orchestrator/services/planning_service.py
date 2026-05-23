"""Phase 3 planning workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_orchestrator.db.models import TaskRecord
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.integrations.claude_runner import (
    ClaudeRunResult,
    ClaudeRunner,
    ClaudeRunnerExecutionError,
)
from ai_orchestrator.shared.clock import utc_now_iso
from ai_orchestrator.shared.enums import TaskStatus


class PlanningServiceError(Exception):
    """Base planning service error."""


class TaskNotPlanningError(PlanningServiceError):
    """Raised when planning is attempted from the wrong task state."""


class PlanningContextError(PlanningServiceError):
    """Raised when the task is missing worktree metadata needed for planning."""


class InvalidRiskLevelError(PlanningServiceError):
    """Raised when planning receives an unsupported risk level."""


@dataclass(slots=True)
class PlanningResult:
    """Result of one planning run."""

    task: TaskRecord
    risk_level: str
    artifact_path: Path
    log_path: Path
    approval_required: bool


class PlanningService:
    """Create plan artifacts and move tasks through the Phase 3 planner gate."""

    VALID_RISK_LEVELS = frozenset({"low", "medium", "high"})

    def __init__(
        self,
        *,
        repository: TaskRepository,
        claude_runner: ClaudeRunner,
        runs_dir: Path,
    ) -> None:
        self._repository = repository
        self._claude_runner = claude_runner
        self._runs_dir = runs_dir

    def plan_task(
        self,
        *,
        task_id: str,
        risk_level: str,
    ) -> PlanningResult:
        """Run Claude planning for one task that is ready for the planning boundary."""

        task = self._repository.get_task(task_id)
        if task is None:
            raise LookupError(f"Unknown task id: {task_id}")
        if risk_level not in self.VALID_RISK_LEVELS:
            allowed = ", ".join(sorted(self.VALID_RISK_LEVELS))
            raise InvalidRiskLevelError(
                f"Invalid risk level '{risk_level}'. Expected one of: {allowed}.",
            )
        if task.status != TaskStatus.PLANNING.value:
            raise TaskNotPlanningError(
                f"Task {task_id} must be planning before Claude runs, got {task.status}.",
            )
        if not task.repo_alias or not task.branch_name or not task.worktree_path:
            raise PlanningContextError(
                f"Task {task_id} is missing repository/worktree metadata required for planning.",
            )

        run_dir = self._runs_dir / task.task_id
        run_dir.mkdir(parents=True, exist_ok=True)
        input_path = run_dir / "input.md"
        input_path.write_text(
            self._render_input_document(task=task, risk_level=risk_level), encoding="utf-8"
        )

        artifact_path = run_dir / self._artifact_name_for_risk(risk_level)
        log_path = run_dir / "planning.log"

        started_at = utc_now_iso()
        self._repository.add_event(
            task_id=task.task_id,
            event_type="planning_started",
            payload={
                "status": task.status,
                "risk_level": risk_level,
                "input_path": str(input_path),
                "artifact_path": str(artifact_path),
            },
            created_at=started_at,
        )

        try:
            result = self._claude_runner.run_planning_prompt(
                prompt=self._build_planning_prompt(
                    task=task,
                    risk_level=risk_level,
                    input_path=input_path,
                ),
                worktree_path=Path(task.worktree_path),
            )
        except ClaudeRunnerExecutionError as error:
            self._write_planning_log(log_path=log_path, result=error.result)
            failed_task = self._repository.update_task_status(
                task_id=task.task_id,
                status=TaskStatus.FAILED.value,
                updated_at=utc_now_iso(),
            )
            self._repository.add_event(
                task_id=task.task_id,
                event_type="worker_failed",
                payload={
                    "step": "planning",
                    "error_type": error.__class__.__name__,
                    "message": str(error),
                    "status": failed_task.status,
                    "log_path": str(log_path),
                },
                created_at=utc_now_iso(),
            )
            raise

        artifact_path.write_text(result.stdout.strip() + "\n", encoding="utf-8")
        self._write_planning_log(log_path=log_path, result=result)

        approval_required = risk_level in {"medium", "high"}
        next_status = (
            TaskStatus.WAITING_PLAN_APPROVAL.value
            if approval_required
            else TaskStatus.IMPLEMENTING.value
        )
        updated_task = self._repository.update_task_status(
            task_id=task.task_id,
            status=next_status,
            updated_at=utc_now_iso(),
        )
        self._repository.add_event(
            task_id=task.task_id,
            event_type="planning_completed",
            payload={
                "risk_level": risk_level,
                "approval_required": approval_required,
                "artifact_path": str(artifact_path),
                "log_path": str(log_path),
            },
            created_at=utc_now_iso(),
        )
        self._repository.add_event(
            task_id=task.task_id,
            event_type="status_transition",
            payload={
                "from_status": task.status,
                "to_status": updated_task.status,
                "step": "planning",
            },
            created_at=utc_now_iso(),
        )
        return PlanningResult(
            task=updated_task,
            risk_level=risk_level,
            artifact_path=artifact_path,
            log_path=log_path,
            approval_required=approval_required,
        )

    @staticmethod
    def _artifact_name_for_risk(risk_level: str) -> str:
        return "architecture_plan.md" if risk_level == "high" else "plan.md"

    @staticmethod
    def _render_input_document(*, task: TaskRecord, risk_level: str) -> str:
        return "\n".join(
            [
                f"# Task {task.task_id}",
                "",
                f"- Requested by: {task.requested_by}",
                f"- Risk level: {risk_level}",
                f"- Repository alias: {task.repo_alias}",
                f"- Branch: {task.branch_name}",
                f"- Worktree: {task.worktree_path}",
                "",
                "## Request",
                "",
                task.source_text.strip(),
                "",
            ]
        )

    @staticmethod
    def _build_planning_prompt(*, task: TaskRecord, risk_level: str, input_path: Path) -> str:
        output_artifact = "architecture_plan.md" if risk_level == "high" else "plan.md"
        approval_required = "yes" if risk_level in {"medium", "high"} else "no"
        return "\n".join(
            [
                "You are the Claude Planner for the AI Dev Orchestrator MVP.",
                f"Task id: {task.task_id}",
                f"Main planner input: {input_path}",
                "",
                "Read the full task brief from the input file above and treat it as the main input.",
                "",
                f"Write the contents for `{output_artifact}` as Markdown.",
                "Include:",
                "- scope",
                "- not in scope",
                "- proposed changed files",
                "- verification commands",
                "- risks",
                f"- approval required: {approval_required}",
                "",
                "Do not implement code. Do not describe actions outside the task worktree.",
            ]
        )

    @staticmethod
    def _write_planning_log(*, log_path: Path, result: ClaudeRunResult) -> None:
        log_path.write_text(
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
