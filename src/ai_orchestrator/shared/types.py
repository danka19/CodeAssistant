"""Shared type aliases."""

from __future__ import annotations

from typing import Literal

TaskStatusName = Literal[
    "created",
    "queued",
    "planning",
    "waiting_plan_approval",
    "plan_rejected",
    "implementing",
    "testing",
    "creating_pr",
    "failed",
]
