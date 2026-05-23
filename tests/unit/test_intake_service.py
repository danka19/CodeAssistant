from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.services.intake_service import (
    IntakeService,
    TaskNotFoundError,
    UnauthorizedUserError,
    ValidationError,
)
from tests.support import make_runtime_test_dir, remove_runtime_test_dir


def build_service(runtime_dir) -> IntakeService:
    repository = TaskRepository(runtime_dir / "tasks.sqlite3")
    repository.initialize()
    return IntakeService(repository=repository, allowed_user_ids=[1001])


def test_task_creation_persists_task_and_event() -> None:
    runtime_dir = make_runtime_test_dir("task-create")
    try:
        service = build_service(runtime_dir)

        task = service.create_task(user_id=1001, source_text="Investigate intake flow")
        events = service.repository.list_events(task.task_id)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert task.task_id.startswith("task-")
    assert task.status == "queued"
    assert len(events) == 1
    assert events[0].event_type == "task_queued"


def test_status_lookup_returns_existing_task() -> None:
    runtime_dir = make_runtime_test_dir("status-existing")
    try:
        service = build_service(runtime_dir)
        created = service.create_task(user_id=1001, source_text="Check current status")

        fetched = service.get_task_status(user_id=1001, task_id=created.task_id)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert fetched.task_id == created.task_id
    assert fetched.status == "queued"


def test_unknown_task_id_raises_not_found() -> None:
    runtime_dir = make_runtime_test_dir("status-missing")
    try:
        service = build_service(runtime_dir)

        try:
            service.get_task_status(user_id=1001, task_id="task-missing")
        except TaskNotFoundError:
            return
    finally:
        remove_runtime_test_dir(runtime_dir)

    raise AssertionError("Expected TaskNotFoundError for unknown task id.")


def test_unauthorized_user_cannot_create_task() -> None:
    runtime_dir = make_runtime_test_dir("unauthorized")
    try:
        service = build_service(runtime_dir)

        try:
            service.create_task(user_id=2002, source_text="Blocked request")
        except UnauthorizedUserError:
            return
    finally:
        remove_runtime_test_dir(runtime_dir)

    raise AssertionError("Expected UnauthorizedUserError for blocked user.")


def test_empty_task_payload_is_rejected() -> None:
    runtime_dir = make_runtime_test_dir("empty-task")
    try:
        service = build_service(runtime_dir)

        try:
            service.create_task(user_id=1001, source_text="   ")
        except ValidationError:
            return
    finally:
        remove_runtime_test_dir(runtime_dir)

    raise AssertionError("Expected ValidationError for empty task text.")
