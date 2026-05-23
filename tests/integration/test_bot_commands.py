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
