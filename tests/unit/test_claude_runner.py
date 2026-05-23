import subprocess
from pathlib import Path

import pytest

from ai_orchestrator.integrations.claude_runner import (
    ClaudeRunner,
    ClaudeRunnerExecutionError,
)


def test_run_planning_prompt_uses_print_mode() -> None:
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["cwd"] = kwargs["cwd"]
        captured["timeout"] = kwargs["timeout"]
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="# plan\n",
            stderr="",
        )

    runner = ClaudeRunner(
        command="claude",
        timeout_seconds=90,
        subprocess_run=fake_run,
    )
    result = runner.run_planning_prompt(
        prompt="write a plan",
        worktree_path=Path("/tmp/worktree"),
    )

    assert captured["command"] == ["claude", "-p", "write a plan"]
    assert captured["cwd"] == Path("/tmp/worktree")
    assert captured["timeout"] == 90
    assert result.stdout == "# plan\n"


def test_run_planning_prompt_rejects_empty_output() -> None:
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="   \n",
            stderr="",
        )

    runner = ClaudeRunner(subprocess_run=fake_run)

    with pytest.raises(ClaudeRunnerExecutionError, match="empty planning response"):
        runner.run_planning_prompt(
            prompt="write a plan",
            worktree_path=Path("/tmp/worktree"),
        )


def test_run_planning_prompt_raises_on_nonzero_exit() -> None:
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            args=command,
            returncode=2,
            stdout="",
            stderr="boom",
        )

    runner = ClaudeRunner(subprocess_run=fake_run)

    with pytest.raises(ClaudeRunnerExecutionError, match="exited with code 2"):
        runner.run_planning_prompt(
            prompt="write a plan",
            worktree_path=Path("/tmp/worktree"),
        )


def test_run_planning_prompt_wraps_missing_command() -> None:
    def fake_run(command, **kwargs):
        raise FileNotFoundError("not found")

    runner = ClaudeRunner(command="missing-claude", subprocess_run=fake_run)

    with pytest.raises(ClaudeRunnerExecutionError, match="command not found"):
        runner.run_planning_prompt(
            prompt="write a plan",
            worktree_path=Path("/tmp/worktree"),
        )


def test_run_planning_prompt_wraps_timeout() -> None:
    def fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(cmd=command, timeout=5, output="", stderr="timeout")

    runner = ClaudeRunner(timeout_seconds=5, subprocess_run=fake_run)

    with pytest.raises(ClaudeRunnerExecutionError, match="timed out after 5s"):
        runner.run_planning_prompt(
            prompt="write a plan",
            worktree_path=Path("/tmp/worktree"),
        )
