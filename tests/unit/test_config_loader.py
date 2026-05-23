from pathlib import Path

from ai_orchestrator.config.loader import load_app_config


def test_loads_example_config(monkeypatch) -> None:
    monkeypatch.delenv("TELEGRAM_ALLOWED_USER_IDS", raising=False)

    config = load_app_config(Path("config/config.example.yaml"))

    assert config.runtime.mode == "systemd"
    assert config.telegram.allowed_user_ids == []
    assert config.telegram.allowed_user_ids_env == "TELEGRAM_ALLOWED_USER_IDS"
    assert config.agents.claude_planner.command == "claude"
    assert config.limits.command_timeout_seconds == 1800
    assert "codeassistant" in config.repositories


def test_allowed_user_ids_can_be_overridden_by_environment(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "1001, 2002")

    config = load_app_config(Path("config/config.example.yaml"))

    assert config.telegram.allowed_user_ids == [1001, 2002]


def test_allowed_user_ids_env_accepts_bracketed_list(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "[1001, 2002]")

    config = load_app_config(Path("config/config.example.yaml"))

    assert config.telegram.allowed_user_ids == [1001, 2002]
