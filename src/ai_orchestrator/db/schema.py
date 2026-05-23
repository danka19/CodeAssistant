"""SQLite schema management."""

from __future__ import annotations

import sqlite3

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY,
        source_text TEXT NOT NULL,
        status TEXT NOT NULL,
        requested_by INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES tasks(task_id)
    )
    """,
)

TASK_COLUMN_MIGRATIONS = {
    "repo_alias": "TEXT",
    "branch_name": "TEXT",
    "worktree_path": "TEXT",
}


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the current schema and backfill additive columns."""

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    _apply_task_column_migrations(connection)
    connection.commit()


def _apply_task_column_migrations(connection: sqlite3.Connection) -> None:
    existing_columns = {row[1] for row in connection.execute("PRAGMA table_info(tasks)").fetchall()}
    for column_name, column_type in TASK_COLUMN_MIGRATIONS.items():
        if column_name in existing_columns:
            continue
        connection.execute(
            f"ALTER TABLE tasks ADD COLUMN {column_name} {column_type}",
        )
