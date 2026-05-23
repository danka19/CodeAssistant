"""Load tracked config templates and deployment config files."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

import yaml


@dataclass(slots=True)
class RuntimeConfig:
    mode: str
    user: str
    root_dir: str
    data_dir: str
    runs_dir: str
    repos_dir: str
    worktrees_dir: str


@dataclass(slots=True)
class TelegramConfig:
    bot_token_env: str
    allowed_user_ids: list[int]
    allowed_user_ids_env: str | None = None


@dataclass(slots=True)
class GitHubConfig:
    token_env: str | None
    default_owner: str
    pr_base_branch: str


@dataclass(slots=True)
class ClaudePlannerConfig:
    command: str


@dataclass(slots=True)
class AgentsConfig:
    claude_planner: ClaudePlannerConfig = field(
        default_factory=lambda: ClaudePlannerConfig(command="claude")
    )


@dataclass(slots=True)
class LimitsConfig:
    command_timeout_seconds: int = 1800


@dataclass(slots=True)
class RepositoryConfig:
    repo: str
    default_branch: str
    purpose: str
    local_path: str
    worktree_root: str
    test_commands: list[str]


@dataclass(slots=True)
class AppConfig:
    runtime: RuntimeConfig
    telegram: TelegramConfig
    github: GitHubConfig
    repositories: dict[str, RepositoryConfig]
    agents: AgentsConfig = field(default_factory=AgentsConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)


def load_app_config(path: Path) -> AppConfig:
    """Load YAML configuration into typed dataclasses."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    telegram_config = TelegramConfig(**raw["telegram"])
    if telegram_config.allowed_user_ids_env:
        env_value = os.getenv(telegram_config.allowed_user_ids_env, "").strip()
        if env_value:
            telegram_config.allowed_user_ids = _parse_allowed_user_ids(env_value)
    repositories = {
        alias: RepositoryConfig(**repo_data)
        for alias, repo_data in raw.get("repositories", {}).items()
    }
    agents_raw = raw.get("agents", {})
    limits_raw = raw.get("limits", {})
    return AppConfig(
        runtime=RuntimeConfig(**raw["runtime"]),
        telegram=telegram_config,
        github=GitHubConfig(**raw["github"]),
        agents=AgentsConfig(
            claude_planner=ClaudePlannerConfig(
                command=agents_raw.get("claude_planner", {}).get("command", "claude"),
            )
        ),
        limits=LimitsConfig(
            command_timeout_seconds=int(limits_raw.get("command_timeout_seconds", 1800)),
        ),
        repositories=repositories,
    )


def _parse_allowed_user_ids(raw_value: str) -> list[int]:
    """Parse comma-separated Telegram user ids from environment config."""

    stripped_value = raw_value.strip()
    if stripped_value.startswith("[") and stripped_value.endswith("]"):
        stripped_value = stripped_value[1:-1]

    values: list[int] = []
    for token in stripped_value.split(","):
        normalized = token.strip()
        if not normalized:
            continue
        values.append(int(normalized))
    return values
