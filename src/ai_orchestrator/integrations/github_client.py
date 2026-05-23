"""GitHub auth and CLI boundary for phased runtime actions."""

from __future__ import annotations

from dataclasses import dataclass
import os
import subprocess


class GitHubClientError(Exception):
    """Base GitHub integration error."""


class MissingGitHubTokenError(GitHubClientError):
    """Raised when the configured token environment variable is missing."""


class GitHubCliUnavailableError(GitHubClientError):
    """Raised when the GitHub CLI is not installed."""


class GitHubAuthError(GitHubClientError):
    """Raised when GitHub CLI auth validation fails."""

    def __init__(self, status: "GitHubAuthStatus") -> None:
        super().__init__(f"GitHub auth check failed with exit code {status.exit_code}.")
        self.status = status


@dataclass(slots=True)
class GitHubAuthStatus:
    """Secret-free result for one GitHub auth check."""

    token_env: str
    exit_code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


@dataclass(slots=True)
class GitHubClient:
    """Phase 2 GitHub auth boundary around the GitHub CLI."""

    token_env: str | None

    def require_token(self) -> str:
        """Return the configured GitHub token from the environment."""

        if not self.token_env:
            raise MissingGitHubTokenError("GitHub token env is not configured.")

        token = os.getenv(self.token_env, "").strip()
        if not token or token == "PASTE_REAL_GITHUB_TOKEN_HERE":
            raise MissingGitHubTokenError(
                f"Missing GitHub token in environment variable: {self.token_env}",
            )
        return token

    def check_auth(self) -> GitHubAuthStatus:
        """Validate that the GitHub CLI can use the configured token."""

        token = self.require_token()
        env = os.environ.copy()
        env.setdefault("GH_TOKEN", token)
        env.setdefault("GITHUB_TOKEN", token)
        try:
            completed = subprocess.run(
                ["gh", "auth", "status", "--hostname", "github.com"],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
        except FileNotFoundError as error:
            raise GitHubCliUnavailableError("GitHub CLI `gh` is not installed.") from error

        status = GitHubAuthStatus(
            token_env=self.token_env or "",
            exit_code=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )
        if not status.ok:
            raise GitHubAuthError(status)
        return status
