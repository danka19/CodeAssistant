from subprocess import CompletedProcess

import pytest

from ai_orchestrator.integrations.github_client import (
    GitHubAuthError,
    GitHubCliUnavailableError,
    GitHubClient,
    MissingGitHubTokenError,
)


def test_require_token_reads_configured_env(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")

    client = GitHubClient(token_env="GITHUB_TOKEN")

    assert client.require_token() == "test-token"


def test_require_token_rejects_missing_env(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    client = GitHubClient(token_env="GITHUB_TOKEN")

    with pytest.raises(MissingGitHubTokenError):
        client.require_token()


def test_check_auth_runs_gh_status(monkeypatch) -> None:
    captured_env: dict[str, str] = {}

    def fake_run(command, capture_output=True, text=True, check=False, env=None):
        del capture_output, text, check
        assert command == ["gh", "auth", "status", "--hostname", "github.com"]
        assert env is not None
        captured_env.update(
            {
                "GH_TOKEN": env["GH_TOKEN"],
                "GITHUB_TOKEN": env["GITHUB_TOKEN"],
            }
        )
        return CompletedProcess(command, 0, stdout="logged in\n", stderr="")

    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(
        "ai_orchestrator.integrations.github_client.subprocess.run",
        fake_run,
    )

    client = GitHubClient(token_env="GITHUB_TOKEN")
    status = client.check_auth()

    assert status.ok is True
    assert status.token_env == "GITHUB_TOKEN"
    assert captured_env == {
        "GH_TOKEN": "test-token",
        "GITHUB_TOKEN": "test-token",
    }


def test_check_auth_raises_for_failed_gh_status(monkeypatch) -> None:
    def fake_run(command, capture_output=True, text=True, check=False, env=None):
        del capture_output, text, check, env
        return CompletedProcess(command, 1, stdout="", stderr="auth failed\n")

    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(
        "ai_orchestrator.integrations.github_client.subprocess.run",
        fake_run,
    )

    client = GitHubClient(token_env="GITHUB_TOKEN")
    with pytest.raises(GitHubAuthError) as error:
        client.check_auth()

    assert error.value.status.exit_code == 1


def test_check_auth_raises_when_gh_is_missing(monkeypatch) -> None:
    def fake_run(command, capture_output=True, text=True, check=False, env=None):
        del command, capture_output, text, check, env
        raise FileNotFoundError

    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(
        "ai_orchestrator.integrations.github_client.subprocess.run",
        fake_run,
    )

    client = GitHubClient(token_env="GITHUB_TOKEN")
    with pytest.raises(GitHubCliUnavailableError):
        client.check_auth()
