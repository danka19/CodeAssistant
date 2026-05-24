"""Composition root for local application wiring."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ai_orchestrator.bot.handlers import BotCommandHandler
from ai_orchestrator.bot.runtime import create_polling_application
from ai_orchestrator.config.loader import AppConfig, load_app_config
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.integrations.claude_runner import ClaudeRunner
from ai_orchestrator.integrations.codex_runner import CodexRunner
from ai_orchestrator.integrations.github_client import GitHubClient
from ai_orchestrator.services.implementation_service import ImplementationService
from ai_orchestrator.services.intake_service import IntakeService
from ai_orchestrator.services.planning_service import PlanningService
from ai_orchestrator.services.workspace_preparation_service import WorkspacePreparationService
from ai_orchestrator.worker.loop import WorkerLoop

DEFAULT_CONFIG_PATH = Path("config/config.example.yaml")
DEFAULT_DATABASE_PATH = Path("data/tasks.sqlite3")
DEFAULT_ENV_PATH = Path(".env.local")


@dataclass(slots=True)
class ApplicationContext:
    """Wired services for the current process."""

    config: AppConfig
    repository: TaskRepository
    intake_service: IntakeService
    bot_handler: BotCommandHandler
    github_client: GitHubClient
    worker_loop: WorkerLoop


def build_application(config_path: Path, database_path: Path) -> ApplicationContext:
    """Build the current local application graph."""

    config = load_app_config(config_path)
    repository = TaskRepository(database_path)
    repository.initialize()
    intake_service = IntakeService(
        repository=repository,
        allowed_user_ids=config.telegram.allowed_user_ids,
    )
    bot_handler = BotCommandHandler(intake_service=intake_service)
    github_client = GitHubClient(token_env=config.github.token_env)
    claude_runner = ClaudeRunner(
        command=config.agents.claude_planner.command,
        timeout_seconds=config.limits.command_timeout_seconds,
    )
    workspace_preparation_service = WorkspacePreparationService(
        repository=repository,
        config=config,
    )
    planning_service = PlanningService(
        repository=repository,
        claude_runner=claude_runner,
        runs_dir=Path(config.runtime.runs_dir),
    )
    codex_runner = CodexRunner(
        command=config.agents.codex_implementer.command,
        timeout_seconds=config.limits.command_timeout_seconds,
    )
    implementation_service = ImplementationService(
        repository=repository,
        config=config,
        codex_runner=codex_runner,
        runs_dir=Path(config.runtime.runs_dir),
    )
    worker_loop = WorkerLoop(
        repository=repository,
        workspace_preparation_service=workspace_preparation_service,
        planning_service=planning_service,
        implementation_service=implementation_service,
    )
    return ApplicationContext(
        config=config,
        repository=repository,
        intake_service=intake_service,
        bot_handler=bot_handler,
        github_client=github_client,
        worker_loop=worker_loop,
    )


def run_telegram_polling(config_path: Path, database_path: Path) -> None:
    """Start the Phase 1 Telegram intake bot in polling mode."""

    load_env_file(DEFAULT_ENV_PATH)
    context = build_application(config_path=config_path, database_path=database_path)
    token_env = context.config.telegram.bot_token_env
    bot_token = os.getenv(token_env)
    if not bot_token or bot_token == "PASTE_REAL_BOT_TOKEN_HERE":
        raise RuntimeError(
            f"Missing Telegram bot token in environment variable: {token_env}",
        )

    application = create_polling_application(
        bot_token=bot_token,
        command_handler=context.bot_handler,
    )
    application.run_polling()


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE pairs from a local env file if it exists."""

    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        normalized_key = key.strip()
        if not normalized_key:
            continue

        normalized_value = value.strip().strip('"').strip("'")
        os.environ.setdefault(normalized_key, normalized_value)


def prepare_task_workspace(
    *,
    config_path: Path,
    database_path: Path,
    task_id: str,
    repo_alias: str,
) -> None:
    """Prepare repository cache and worktree for one queued task."""

    load_env_file(DEFAULT_ENV_PATH)
    context = build_application(config_path=config_path, database_path=database_path)
    result = context.worker_loop.prepare_task_workspace(
        task_id=task_id,
        repo_alias=repo_alias,
    )
    print(
        "\n".join(
            [
                f"Task: {result.task.task_id}",
                f"Status: {result.task.status}",
                f"Repository: {repo_alias}",
                f"Branch: {result.workspace.branch_name}",
                f"Worktree: {result.workspace.worktree_path}",
            ]
        )
    )


def check_github_auth(*, config_path: Path, database_path: Path) -> None:
    """Validate GitHub CLI auth using the configured token env."""

    load_env_file(DEFAULT_ENV_PATH)
    context = build_application(config_path=config_path, database_path=database_path)
    status = context.github_client.check_auth()
    print(
        "\n".join(
            [
                f"Token env: {status.token_env}",
                "GitHub auth: ok",
                f"gh exit code: {status.exit_code}",
            ]
        )
    )


def plan_task(
    *,
    config_path: Path,
    database_path: Path,
    task_id: str,
    risk_level: str,
) -> None:
    """Run the manual Phase 3 Claude planning bridge for one task."""

    load_env_file(DEFAULT_ENV_PATH)
    context = build_application(config_path=config_path, database_path=database_path)
    result = context.worker_loop.plan_task(
        task_id=task_id,
        risk_level=risk_level,
    )
    print(
        "\n".join(
            [
                f"Task: {result.task.task_id}",
                f"Status: {result.task.status}",
                f"Risk: {result.planning.risk_level}",
                f"Approval required: {'yes' if result.planning.approval_required else 'no'}",
                f"Plan artifact: {result.planning.artifact_path}",
                f"Planning log: {result.planning.log_path}",
            ]
        )
    )


def implement_task(
    *,
    config_path: Path,
    database_path: Path,
    task_id: str,
) -> None:
    """Run the manual Phase 4 Codex implementation bridge for one task."""

    load_env_file(DEFAULT_ENV_PATH)
    context = build_application(config_path=config_path, database_path=database_path)
    result = context.worker_loop.implement_task(task_id=task_id)
    print(
        "\n".join(
            [
                f"Task: {result.task.task_id}",
                f"Status: {result.task.status}",
                f"Commit: {result.implementation.commit_sha}",
                f"Implementation log: {result.implementation.implementation_log_path}",
                f"Test log: {result.implementation.test_log_path}",
                f"Summary: {result.implementation.summary_path}",
            ]
        )
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the current local runtime entrypoints."""

    normalized_argv = list(argv) if argv is not None else sys.argv[1:]
    if not normalized_argv or normalized_argv[0].startswith("-"):
        normalized_argv = ["run-bot", *normalized_argv]

    parser = argparse.ArgumentParser(description="Run the local AI orchestrator entrypoints.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_bot_parser = subparsers.add_parser(
        "run-bot",
        help="Run the Telegram polling intake bot.",
    )
    _add_common_path_arguments(run_bot_parser)

    prepare_workspace_parser = subparsers.add_parser(
        "prepare-workspace",
        help="Prepare repository cache and worktree for one queued task.",
    )
    _add_common_path_arguments(prepare_workspace_parser)
    prepare_workspace_parser.add_argument(
        "--task-id",
        required=True,
        help="Queued task id to prepare.",
    )
    prepare_workspace_parser.add_argument(
        "--repo-alias",
        required=True,
        help="Configured repository alias to use for the task.",
    )

    check_github_auth_parser = subparsers.add_parser(
        "check-github-auth",
        help="Validate GitHub CLI auth using the configured token env.",
    )
    _add_common_path_arguments(check_github_auth_parser)

    plan_task_parser = subparsers.add_parser(
        "plan-task",
        help="Run Claude planning for one task already in the planning state.",
    )
    _add_common_path_arguments(plan_task_parser)
    plan_task_parser.add_argument(
        "--task-id",
        required=True,
        help="Planning task id to run through Claude.",
    )
    plan_task_parser.add_argument(
        "--risk",
        required=True,
        choices=("low", "medium", "high"),
        help="Risk level used to choose approval behavior and artifact type.",
    )

    implement_task_parser = subparsers.add_parser(
        "implement-task",
        help="Run Codex implementation for one task already in the implementing state.",
    )
    _add_common_path_arguments(implement_task_parser)
    implement_task_parser.add_argument(
        "--task-id",
        required=True,
        help="Implementing task id to run through Codex.",
    )

    return parser.parse_args(normalized_argv)


def _add_common_path_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the YAML config file.",
    )
    parser.add_argument(
        "--database-path",
        type=Path,
        default=DEFAULT_DATABASE_PATH,
        help="Path to the SQLite database file.",
    )


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for the local runtime commands."""

    args = parse_args(argv)
    if args.command == "run-bot":
        run_telegram_polling(config_path=args.config, database_path=args.database_path)
        return 0
    if args.command == "prepare-workspace":
        prepare_task_workspace(
            config_path=args.config,
            database_path=args.database_path,
            task_id=args.task_id,
            repo_alias=args.repo_alias,
        )
        return 0
    if args.command == "check-github-auth":
        check_github_auth(
            config_path=args.config,
            database_path=args.database_path,
        )
        return 0
    if args.command == "plan-task":
        plan_task(
            config_path=args.config,
            database_path=args.database_path,
            task_id=args.task_id,
            risk_level=args.risk,
        )
        return 0
    if args.command == "implement-task":
        implement_task(
            config_path=args.config,
            database_path=args.database_path,
            task_id=args.task_id,
        )
        return 0
    raise RuntimeError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
