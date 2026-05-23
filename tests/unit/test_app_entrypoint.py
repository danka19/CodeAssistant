from tests.support import make_runtime_test_dir, remove_runtime_test_dir

from ai_orchestrator.app import load_env_file, main, parse_args


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


def test_parse_args_defaults_to_run_bot_for_legacy_invocation() -> None:
    args = parse_args(["--config", "config/custom.yaml"])

    assert args.command == "run-bot"
    assert str(args.config).endswith("config\\custom.yaml")


def test_parse_args_supports_prepare_workspace_command() -> None:
    args = parse_args(
        [
            "prepare-workspace",
            "--task-id",
            "task-123",
            "--repo-alias",
            "codeassistant",
        ]
    )

    assert args.command == "prepare-workspace"
    assert args.task_id == "task-123"
    assert args.repo_alias == "codeassistant"


def test_main_routes_prepare_workspace_command(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_prepare_task_workspace(**kwargs) -> None:
        captured.update(kwargs)

    monkeypatch.setattr("ai_orchestrator.app.prepare_task_workspace", fake_prepare_task_workspace)

    exit_code = main(
        [
            "prepare-workspace",
            "--task-id",
            "task-123",
            "--repo-alias",
            "codeassistant",
        ]
    )

    assert exit_code == 0
    assert captured["task_id"] == "task-123"
    assert captured["repo_alias"] == "codeassistant"


def test_main_routes_run_bot_command(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run_telegram_polling(*, config_path, database_path) -> None:
        captured["config_path"] = config_path
        captured["database_path"] = database_path

    monkeypatch.setattr("ai_orchestrator.app.run_telegram_polling", fake_run_telegram_polling)

    exit_code = main(["run-bot"])

    assert exit_code == 0
    assert "config_path" in captured
