"""Subprocess wrapper for Codex implementation runs."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(slots=True)
class CodexRunResult:
    """Captured result from one Codex CLI invocation."""

    command: list[str]
    exit_code: int
    stdout: str
    stderr: str


class CodexRunnerError(Exception):
    """Base Codex runner failure."""


class CodexRunnerExecutionError(CodexRunnerError):
    """Raised when Codex exits unsuccessfully."""

    def __init__(self, message: str, *, result: CodexRunResult) -> None:
        super().__init__(message)
        self.result = result


class CodexRunner:
    """Run Codex non-interactively via `codex exec`."""

    def __init__(
        self,
        *,
        command: str = "codex",
        timeout_seconds: int = 1800,
        subprocess_run: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self._command = command
        self._timeout_seconds = timeout_seconds
        self._subprocess_run = subprocess_run or subprocess.run

    def run_implementation_prompt(
        self,
        *,
        prompt: str,
        worktree_path: Path,
    ) -> CodexRunResult:
        """Run Codex implementation for one task prompt."""

        command = [self._command, "exec", prompt]
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
            raise CodexRunnerExecutionError(
                f"Codex command not found: {self._command}",
                result=CodexRunResult(
                    command=command,
                    exit_code=-1,
                    stdout="",
                    stderr=str(error),
                ),
            ) from error
        except subprocess.TimeoutExpired as error:
            raise CodexRunnerExecutionError(
                f"Codex implementation timed out after {self._timeout_seconds}s.",
                result=CodexRunResult(
                    command=command,
                    exit_code=-1,
                    stdout=error.stdout or "",
                    stderr=error.stderr or "",
                ),
            ) from error

        result = CodexRunResult(
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        if completed.returncode != 0:
            raise CodexRunnerExecutionError(
                f"Codex exited with code {completed.returncode}.",
                result=result,
            )
        return result
