from tests.support import make_runtime_test_dir, remove_runtime_test_dir

from ai_orchestrator.app import load_env_file


def test_load_env_file_populates_missing_environment_values(monkeypatch) -> None:
    runtime_dir = make_runtime_test_dir("env-file-load")
    try:
        env_path = runtime_dir / ".env.local"
        env_path.write_text(
            "\n".join(
                [
                    "# comment",
                    "TELEGRAM_BOT_TOKEN=test-token",
                    "EXTRA_VALUE='quoted'",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("EXTRA_VALUE", raising=False)

        load_env_file(env_path)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert __import__("os").environ["TELEGRAM_BOT_TOKEN"] == "test-token"
    assert __import__("os").environ["EXTRA_VALUE"] == "quoted"


def test_load_env_file_preserves_existing_environment_values(monkeypatch) -> None:
    runtime_dir = make_runtime_test_dir("env-file-prefer-env")
    try:
        env_path = runtime_dir / ".env.local"
        env_path.write_text("TELEGRAM_BOT_TOKEN=file-token", encoding="utf-8")
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "env-token")

        load_env_file(env_path)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert __import__("os").environ["TELEGRAM_BOT_TOKEN"] == "env-token"
