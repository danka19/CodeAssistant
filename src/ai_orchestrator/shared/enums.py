"""Shared enums."""

from __future__ import annotations

from enum import Enum


class TaskStatus(str, Enum):
    """Task states currently recognized by the local implementation."""

    CREATED = "created"
    QUEUED = "queued"
    PLANNING = "planning"
    FAILED = "failed"
