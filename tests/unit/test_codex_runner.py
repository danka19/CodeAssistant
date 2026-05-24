import subprocess
from pathlib import Path

import pytest

from ai_orchestrator.integrations.codex_runner import CodexRunner, CodexRunnerExecutionError


def test_codex_runner_runs_exec_prompt() -> None:
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["cwd"] = kwargs["cwd"]
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="")

    runner = CodexRunner(command="codex", subprocess_run=fake_run)  # type: ignore[arg-type]
    result = runner.run_implementation_prompt(
        prompt="implement plan", worktree_path=Path("/tmp/worktree")
    )

    assert result.exit_code == 0
    assert captured["command"] == ["codex", "exec", "implement plan"]
    assert captured["cwd"] == Path("/tmp/worktree")


def test_codex_runner_raises_on_non_zero_exit() -> None:
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="failed")

    runner = CodexRunner(command="codex", subprocess_run=fake_run)  # type: ignore[arg-type]
    with pytest.raises(CodexRunnerExecutionError, match="Codex exited with code 2"):
        runner.run_implementation_prompt(
            prompt="implement plan", worktree_path=Path("/tmp/worktree")
        )
