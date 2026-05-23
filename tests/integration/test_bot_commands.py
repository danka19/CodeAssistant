from ai_orchestrator.bot.handlers import BotCommandHandler
from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.services.intake_service import IntakeService
from tests.support import make_runtime_test_dir, remove_runtime_test_dir


def build_handler(runtime_dir) -> BotCommandHandler:
    repository = TaskRepository(runtime_dir / "tasks.sqlite3")
    repository.initialize()
    service = IntakeService(repository=repository, allowed_user_ids=[1001])
    return BotCommandHandler(service)


def test_task_command_creates_task_and_status_command_reads_it() -> None:
    runtime_dir = make_runtime_test_dir("bot-commands")
    try:
        handler = build_handler(runtime_dir)

        task_response = handler.handle_task_command(1001, "/task Prepare initial intake worker")
        task_id = task_response.split()[1]
        status_response = handler.handle_status_command(1001, f"/status {task_id}")
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert "accepted" in task_response
    assert task_id in status_response
    assert "queued" in status_response


def test_status_command_returns_not_found_for_unknown_task() -> None:
    runtime_dir = make_runtime_test_dir("bot-status-missing")
    try:
        handler = build_handler(runtime_dir)

        response = handler.handle_status_command(1001, "/status task-missing")
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert response == "Task task-missing not found."


def test_help_command_returns_phase_1_command_summary() -> None:
    runtime_dir = make_runtime_test_dir("bot-help")
    try:
        handler = build_handler(runtime_dir)

        response = handler.handle_help_command(1001)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert "/task <description>" in response
    assert "/tasks" in response
    assert "/status <task_id>" in response
    assert "/help" in response


def test_tasks_command_returns_menu_and_callback_opens_status() -> None:
    runtime_dir = make_runtime_test_dir("bot-tasks-menu")
    try:
        handler = build_handler(runtime_dir)
        first_response = handler.handle_task_command(1001, "/task First task title")
        second_response = handler.handle_task_command(1001, "/task Second task title")

        menu_text, menu_items = handler.handle_tasks_command(1001)
        callback_response = handler.handle_task_status_callback(
            1001,
            menu_items[0].callback_data,
        )
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert "accepted" in first_response
    assert "accepted" in second_response
    assert menu_text == "Select a task to open status:"
    assert len(menu_items) == 2
    assert menu_items[0].callback_data.startswith("task_status:")
    assert ": queued." in callback_response


def test_help_command_rejects_unauthorized_user() -> None:
    runtime_dir = make_runtime_test_dir("bot-help-unauthorized")
    try:
        handler = build_handler(runtime_dir)

        response = handler.handle_help_command(2002)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert response == "Unauthorized user."
