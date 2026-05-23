import sqlite3

from ai_orchestrator.db.repository import TaskRepository
from tests.support import make_runtime_test_dir, remove_runtime_test_dir


def test_initialize_is_idempotent() -> None:
    runtime_dir = make_runtime_test_dir("db-schema")
    try:
        database_path = runtime_dir / "tasks.sqlite3"
        repository = TaskRepository(database_path)

        repository.initialize()
        repository.initialize()

        with sqlite3.connect(database_path) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert "tasks" in tables
    assert "events" in tables
