import json

import pytest

from ai_orchestrator.db.repository import TaskRepository
from ai_orchestrator.services.intake_service import IntakeService, TaskApprovalStateError
from ai_orchestrator.shared.enums import TaskStatus
from tests.support import make_runtime_test_dir, remove_runtime_test_dir


def test_approve_plan_moves_task_to_implementing() -> None:
    runtime_dir = make_runtime_test_dir("approve-plan")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        repository.create_task(
            task_id="task-approval-1",
            source_text="Approve me",
            status=TaskStatus.WAITING_PLAN_APPROVAL.value,
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        service = IntakeService(repository=repository, allowed_user_ids=[1001])

        task = service.approve_plan(user_id=1001, task_id="task-approval-1")
        events = repository.list_events(task.task_id)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert task.status == TaskStatus.IMPLEMENTING.value
    assert events[-2].event_type == "plan_approved"


def test_reject_plan_moves_task_to_plan_rejected_and_records_reason() -> None:
    runtime_dir = make_runtime_test_dir("reject-plan")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        repository.create_task(
            task_id="task-approval-2",
            source_text="Reject me",
            status=TaskStatus.WAITING_PLAN_APPROVAL.value,
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        service = IntakeService(repository=repository, allowed_user_ids=[1001])

        task = service.reject_plan(
            user_id=1001,
            task_id="task-approval-2",
            reason="scope too broad",
        )
        events = repository.list_events(task.task_id)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert task.status == TaskStatus.PLAN_REJECTED.value
    payload = json.loads(events[-2].payload_json)
    assert payload["reason"] == "scope too broad"


def test_approve_plan_requires_waiting_status() -> None:
    runtime_dir = make_runtime_test_dir("approve-plan-status")
    try:
        repository = TaskRepository(runtime_dir / "tasks.sqlite3")
        repository.initialize()
        repository.create_task(
            task_id="task-approval-3",
            source_text="Wrong status",
            status=TaskStatus.QUEUED.value,
            requested_by=1001,
            created_at="2026-05-23T00:00:00Z",
            updated_at="2026-05-23T00:00:00Z",
        )
        service = IntakeService(repository=repository, allowed_user_ids=[1001])

        with pytest.raises(TaskApprovalStateError):
            service.approve_plan(user_id=1001, task_id="task-approval-3")
    finally:
        remove_runtime_test_dir(runtime_dir)
