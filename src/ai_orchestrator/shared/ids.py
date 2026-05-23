"""Identifier helpers."""

from __future__ import annotations

from uuid import uuid4


def generate_task_id() -> str:
    """Generate a short task id for intake records."""

    return f"task-{uuid4().hex[:8]}"
