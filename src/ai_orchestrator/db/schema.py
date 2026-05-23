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


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the minimum Phase 1 schema."""

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    connection.commit()
