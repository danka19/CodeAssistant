"""Command handlers for the Phase 1 intake bot."""

from __future__ import annotations

from ai_orchestrator.bot import presenter
from ai_orchestrator.services.intake_service import (
    IntakeService,
    TaskApprovalStateError,
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

    def handle_tasks_command(self, user_id: int) -> tuple[str, list[presenter.TaskMenuItem]]:
        """Handle `/tasks`."""

        try:
            tasks = self._intake_service.list_tasks(user_id=user_id)
        except UnauthorizedUserError:
            return presenter.format_unauthorized(), []
        return presenter.format_tasks_menu(tasks)

    def handle_task_status_callback(self, user_id: int, callback_data: str) -> str:
        """Handle inline callback payload to open task status."""

        task_id = presenter.parse_task_status_callback_data(callback_data)
        if task_id is None:
            return presenter.format_validation_error("Invalid task selection.")
        try:
            task = self._intake_service.get_task_status(user_id=user_id, task_id=task_id)
        except UnauthorizedUserError:
            return presenter.format_unauthorized()
        except ValidationError as error:
            return presenter.format_validation_error(str(error))
        except TaskNotFoundError:
            return presenter.format_not_found(task_id)
        return presenter.format_task_status(task)

    def handle_help_command(self, user_id: int) -> str:
        """Handle `/help`."""

        try:
            self._intake_service.ensure_authorized(user_id=user_id)
        except UnauthorizedUserError:
            return presenter.format_unauthorized()
        return presenter.format_help()

    def handle_approve_command(self, user_id: int, command_text: str) -> str:
        """Handle `/approve <task_id>`."""

        task_id = self._extract_argument("/approve", command_text)
        try:
            task = self._intake_service.approve_plan(user_id=user_id, task_id=task_id)
        except UnauthorizedUserError:
            return presenter.format_unauthorized()
        except ValidationError as error:
            return presenter.format_validation_error(str(error))
        except TaskApprovalStateError as error:
            return presenter.format_validation_error(str(error))
        except TaskNotFoundError:
            return presenter.format_not_found(task_id)
        return presenter.format_plan_approved(task)

    def handle_reject_command(self, user_id: int, command_text: str) -> str:
        """Handle `/reject <task_id> [reason]`."""

        task_id, reason = self._extract_reject_arguments(command_text)
        try:
            task = self._intake_service.reject_plan(
                user_id=user_id,
                task_id=task_id,
                reason=reason,
            )
        except UnauthorizedUserError:
            return presenter.format_unauthorized()
        except ValidationError as error:
            return presenter.format_validation_error(str(error))
        except TaskApprovalStateError as error:
            return presenter.format_validation_error(str(error))
        except TaskNotFoundError:
            return presenter.format_not_found(task_id)
        return presenter.format_plan_rejected(task)

    @staticmethod
    def _extract_argument(command: str, command_text: str) -> str:
        """Extract the payload after a command prefix."""

        normalized = command_text.strip()
        if normalized.startswith(command):
            return normalized[len(command) :].strip()
        return normalized

    @classmethod
    def _extract_reject_arguments(cls, command_text: str) -> tuple[str, str]:
        normalized = cls._extract_argument("/reject", command_text)
        if not normalized:
            return "", ""
        task_id, _, reason = normalized.partition(" ")
        return task_id.strip(), reason.strip()
