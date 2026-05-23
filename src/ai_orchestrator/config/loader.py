"""Load tracked config templates and deployment config files."""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(slots=True)
class GitHubConfig:
    token_env: str | None
    default_owner: str
    pr_base_branch: str


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


def load_app_config(path: Path) -> AppConfig:
    """Load YAML configuration into typed dataclasses."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    repositories = {
        alias: RepositoryConfig(**repo_data)
        for alias, repo_data in raw.get("repositories", {}).items()
    }
    return AppConfig(
        runtime=RuntimeConfig(**raw["runtime"]),
        telegram=TelegramConfig(**raw["telegram"]),
        github=GitHubConfig(**raw["github"]),
        repositories=repositories,
    )
