"""Subprocess wrapper for Claude planning and review steps."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(slots=True)
class ClaudeRunResult:
    """Captured result from one Claude CLI invocation."""

    command: list[str]
    exit_code: int
    stdout: str
    stderr: str


class ClaudeRunnerError(Exception):
    """Base Claude runner failure."""


class ClaudeRunnerExecutionError(ClaudeRunnerError):
    """Raised when Claude exits unsuccessfully or produces no plan."""

    def __init__(self, message: str, *, result: ClaudeRunResult) -> None:
        super().__init__(message)
        self.result = result


class ClaudeRunner:
    """Run Claude Code in non-interactive print mode."""

    def __init__(
        self,
        *,
        command: str = "claude",
        timeout_seconds: int = 1800,
        subprocess_run: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self._command = command
        self._timeout_seconds = timeout_seconds
        self._subprocess_run = subprocess_run or subprocess.run

    def run_planning_prompt(
        self,
        *,
        prompt: str,
        worktree_path: Path,
    ) -> ClaudeRunResult:
        """Run the configured Claude planner and return captured output."""

        command = [self._command, "-p", prompt]
        try:
            completed = self._subprocess_run(
                command,
                cwd=worktree_path,
                capture_output=True,
                text=True,
                check=False,
                timeout=self._timeout_seconds,
            )
        except FileNotFoundError as error:
            raise ClaudeRunnerExecutionError(
                f"Claude command not found: {self._command}",
                result=ClaudeRunResult(
                    command=command,
                    exit_code=-1,
                    stdout="",
                    stderr=str(error),
                ),
            ) from error
        except subprocess.TimeoutExpired as error:
            raise ClaudeRunnerExecutionError(
                f"Claude planning timed out after {self._timeout_seconds}s.",
                result=ClaudeRunResult(
                    command=command,
                    exit_code=-1,
                    stdout=error.stdout or "",
                    stderr=error.stderr or "",
                ),
            ) from error
        result = ClaudeRunResult(
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        if completed.returncode != 0:
            raise ClaudeRunnerExecutionError(
                f"Claude exited with code {completed.returncode}.",
                result=result,
            )
        if not completed.stdout.strip():
            raise ClaudeRunnerExecutionError(
                "Claude returned an empty planning response.",
                result=result,
            )
        return result
