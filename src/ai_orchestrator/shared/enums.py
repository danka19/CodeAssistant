"""Shared enums."""

from __future__ import annotations

from enum import Enum


class TaskStatus(str, Enum):
    """Task states currently recognized by the local implementation."""

    CREATED = "created"
    QUEUED = "queued"
    PLANNING = "planning"
    WAITING_PLAN_APPROVAL = "waiting_plan_approval"
    PLAN_REJECTED = "plan_rejected"
    IMPLEMENTING = "implementing"
    FAILED = "failed"
