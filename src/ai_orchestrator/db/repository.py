"""SQLite repository for tasks and events."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from ai_orchestrator.db.models import EventRecord, TaskRecord
from ai_orchestrator.db.schema import initialize_schema


class TaskRepository:
    """Persist and retrieve tasks plus their event history."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def initialize(self) -> None:
        """Ensure parent directories and tables exist."""

        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            initialize_schema(connection)

    def create_task(
        self,
        *,
        task_id: str,
        source_text: str,
        status: str,
        requested_by: int,
        created_at: str,
        updated_at: str,
    ) -> TaskRecord:
        """Insert a task row."""

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO tasks (
                    task_id,
                    source_text,
                    status,
                    requested_by,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (task_id, source_text, status, requested_by, created_at, updated_at),
            )
            connection.commit()
        return TaskRecord(
            task_id=task_id,
            source_text=source_text,
            status=status,
            requested_by=requested_by,
            created_at=created_at,
            updated_at=updated_at,
            repo_alias=None,
            branch_name=None,
            worktree_path=None,
        )

    def assign_workspace(
        self,
        *,
        task_id: str,
        repo_alias: str,
        branch_name: str,
        worktree_path: str,
        updated_at: str,
    ) -> TaskRecord:
        """Persist repository preparation metadata for a task."""

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET repo_alias = ?, branch_name = ?, worktree_path = ?, updated_at = ?
                WHERE task_id = ?
                """,
                (repo_alias, branch_name, worktree_path, updated_at, task_id),
            )
            connection.commit()
        task = self.get_task(task_id)
        if task is None:
            raise LookupError(f"Unknown task id: {task_id}")
        return task

    def update_task_status(
        self,
        *,
        task_id: str,
        status: str,
        updated_at: str,
    ) -> TaskRecord:
        """Persist a task status transition."""

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET status = ?, updated_at = ?
                WHERE task_id = ?
                """,
                (status, updated_at, task_id),
            )
            connection.commit()
        task = self.get_task(task_id)
        if task is None:
            raise LookupError(f"Unknown task id: {task_id}")
        return task

    def add_event(
        self,
        *,
        task_id: str,
        event_type: str,
        payload: dict[str, Any],
        created_at: str,
    ) -> EventRecord:
        """Insert an event row for a task."""

        payload_json = json.dumps(payload, sort_keys=True)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO events (task_id, event_type, payload_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (task_id, event_type, payload_json, created_at),
            )
            connection.commit()
        return EventRecord(
            id=int(cursor.lastrowid),
            task_id=task_id,
            event_type=event_type,
            payload_json=payload_json,
            created_at=created_at,
        )

    def get_task(self, task_id: str) -> TaskRecord | None:
        """Fetch one task row by id."""

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    task_id,
                    source_text,
                    status,
                    requested_by,
                    created_at,
                    updated_at,
                    repo_alias,
                    branch_name,
                    worktree_path
                FROM tasks
                WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
        if row is None:
            return None
        return TaskRecord(**dict(row))

    def list_events(self, task_id: str) -> list[EventRecord]:
        """List events for a task."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, task_id, event_type, payload_json, created_at
                FROM events
                WHERE task_id = ?
                ORDER BY id ASC
                """,
                (task_id,),
            ).fetchall()
        return [EventRecord(**dict(row)) for row in rows]

    def list_tasks(self, *, limit: int = 10) -> list[TaskRecord]:
        """List most recent tasks first."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    task_id,
                    source_text,
                    status,
                    requested_by,
                    created_at,
                    updated_at,
                    repo_alias,
                    branch_name,
                    worktree_path
                FROM tasks
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [TaskRecord(**dict(row)) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
