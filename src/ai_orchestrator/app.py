"""Composition root for local application wiring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_orchestrator.bot.handlers import BotCommandHandler
from ai_orchestrator.config.loader import AppConfig, load_app_config
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.services.intake_service import IntakeService


@dataclass(slots=True)
class ApplicationContext:
    """Wired services for the current process."""

    config: AppConfig
    repository: TaskRepository
    intake_service: IntakeService
    bot_handler: BotCommandHandler


def build_application(config_path: Path, database_path: Path) -> ApplicationContext:
    """Build the minimum Phase 1 application graph."""

    config = load_app_config(config_path)
    repository = TaskRepository(database_path)
    repository.initialize()
    intake_service = IntakeService(
        repository=repository,
        allowed_user_ids=config.telegram.allowed_user_ids,
    )
    bot_handler = BotCommandHandler(intake_service=intake_service)
    return ApplicationContext(
        config=config,
        repository=repository,
        intake_service=intake_service,
        bot_handler=bot_handler,
    )
