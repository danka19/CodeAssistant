from pathlib import Path

from ai_orchestrator.config.loader import load_app_config


def test_loads_example_config() -> None:
    config = load_app_config(Path("config/config.example.yaml"))

    assert config.runtime.mode == "systemd"
    assert config.telegram.allowed_user_ids == []
    assert "codeassistant" in config.repositories
