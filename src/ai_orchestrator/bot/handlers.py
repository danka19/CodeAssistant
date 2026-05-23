"""Command handlers for the Phase 1 intake bot."""

from __future__ import annotations

from ai_orchestrator.bot import presenter
from ai_orchestrator.services.intake_service import (
    IntakeService,
    TaskNotFoundError,
    UnauthorizedUserError,
    ValidationError,
)


class BotCommandHandler:
    """Translate command text into intake service calls."""

    def __init__(self, intake_service: IntakeService) -> None:
        self._intake_service = intake_service

    def handle_task_command(self, user_id: int, command_text: str) -> str:
        """Handle `/task <text>`."""

        task_text = self._extract_argument("/task", command_text)
        try:
            task = self._intake_service.create_task(user_id=user_id, source_text=task_text)
        except UnauthorizedUserError:
            return presenter.format_unauthorized()
        except ValidationError as error:
            return presenter.format_validation_error(str(error))
        return presenter.format_task_created(task)

    def handle_status_command(self, user_id: int, command_text: str) -> str:
        """Handle `/status <task_id>`."""

        task_id = self._extract_argument("/status", command_text)
        try:
            task = self._intake_service.get_task_status(user_id=user_id, task_id=task_id)
        except UnauthorizedUserError:
            return presenter.format_unauthorized()
        except ValidationError as error:
            return presenter.format_validation_error(str(error))
        except TaskNotFoundError:
            return presenter.format_not_found(task_id)
        return presenter.format_task_status(task)

    @staticmethod
    def _extract_argument(command: str, command_text: str) -> str:
        """Extract the payload after a command prefix."""

        normalized = command_text.strip()
        if normalized.startswith(command):
            return normalized[len(command) :].strip()
        return normalized
