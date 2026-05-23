"""Database record models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TaskRecord:
    """Stored task row."""

    task_id: str
    source_text: str
    status: str
    requested_by: int
    created_at: str
    updated_at: str
    repo_alias: str | None = None
    branch_name: str | None = None
    worktree_path: str | None = None


@dataclass(slots=True)
class EventRecord:
    """Stored event row."""

    id: int
    task_id: str
    event_type: str
    payload_json: str
    created_at: str
