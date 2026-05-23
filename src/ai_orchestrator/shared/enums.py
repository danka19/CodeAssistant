"""Shared enums."""

from __future__ import annotations

from enum import Enum


class TaskStatus(str, Enum):
    """Currently implemented task states for Phase 1."""

    CREATED = "created"
    QUEUED = "queued"
    FAILED = "failed"
