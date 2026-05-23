import asyncio
from dataclasses import dataclass
from pathlib import Path

import pytest
from telegram.error import TimedOut

from ai_orchestrator.app import run_telegram_polling
from ai_orchestrator.bot.handlers import BotCommandHandler
from ai_orchestrator.bot.runtime import TelegramPollingAdapter, create_polling_application
from tests.support import make_runtime_test_dir, remove_runtime_test_dir


class _FakeMessage:
    def __init__(self, text: str) -> None:
        self.text = text
        self.replies: list[str] = []
        self.reply_markups: list[object | None] = []
        self.failures_before_success = 0
        self.call_count = 0

    async def reply_text(self, text: str, reply_markup: object | None = None) -> None:
        self.call_count += 1
        if self.failures_before_success > 0:
            self.failures_before_success -= 1
            raise TimedOut("timed out")
        self.replies.append(text)
        self.reply_markups.append(reply_markup)


class _FakeUser:
    def __init__(self, user_id: int) -> None:
        self.id = user_id


class _FakeUpdate:
    def __init__(self, user_id: int, text: str) -> None:
        self.effective_user = _FakeUser(user_id)
        self.effective_message = _FakeMessage(text)
        self.callback_query = None


class _FakeCallbackQuery:
    def __init__(self, data: str) -> None:
        self.data = data
        self.message = _FakeMessage("")
        self.answered = False

    async def answer(self) -> None:
        self.answered = True


class _FakeCallbackUpdate:
    def __init__(self, user_id: int, data: str) -> None:
        self.effective_user = _FakeUser(user_id)
        self.effective_message = None
        self.callback_query = _FakeCallbackQuery(data)


class _FakeBotCommandHandler:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, str]] = []

    def handle_task_command(self, user_id: int, command_text: str) -> str:
        self.calls.append(("task", user_id, command_text))
        return "task-response"

    def handle_status_command(self, user_id: int, command_text: str) -> str:
        self.calls.append(("status", user_id, command_text))
        return "status-response"

    def handle_help_command(self, user_id: int) -> str:
        self.calls.append(("help", user_id, ""))
        return "help-response"

    def handle_tasks_command(self, user_id: int) -> tuple[str, list[object]]:
        self.calls.append(("tasks", user_id, ""))

        @dataclass
        class _MenuItem:
            label: str
            callback_data: str

        return (
            "tasks-response",
            [_MenuItem("task-1", "task_status:task-1")],
        )

    def handle_task_status_callback(self, user_id: int, callback_data: str) -> str:
        self.calls.append(("task_status_callback", user_id, callback_data))
        return "task-status-callback-response"


def test_adapter_routes_task_command_and_replies() -> None:
    handler = _FakeBotCommandHandler()
    adapter = TelegramPollingAdapter(command_handler=handler)  # type: ignore[arg-type]
    update = _FakeUpdate(1001, "/task write tests")

    asyncio.run(adapter.on_task(update, None))  # type: ignore[arg-type]

    assert handler.calls == [("task", 1001, "/task write tests")]
    assert update.effective_message.replies == ["task-response"]


def test_adapter_routes_status_command_and_replies() -> None:
    handler = _FakeBotCommandHandler()
    adapter = TelegramPollingAdapter(command_handler=handler)  # type: ignore[arg-type]
    update = _FakeUpdate(1001, "/status task-123")

    asyncio.run(adapter.on_status(update, None))  # type: ignore[arg-type]

    assert handler.calls == [("status", 1001, "/status task-123")]
    assert update.effective_message.replies == ["status-response"]


def test_adapter_routes_help_command_and_replies() -> None:
    handler = _FakeBotCommandHandler()
    adapter = TelegramPollingAdapter(command_handler=handler)  # type: ignore[arg-type]
    update = _FakeUpdate(1001, "/help")

    asyncio.run(adapter.on_help(update, None))  # type: ignore[arg-type]

    assert handler.calls == [("help", 1001, "")]
    assert update.effective_message.replies == ["help-response"]


def test_adapter_routes_tasks_command_and_replies_with_menu() -> None:
    handler = _FakeBotCommandHandler()
    adapter = TelegramPollingAdapter(command_handler=handler)  # type: ignore[arg-type]
    update = _FakeUpdate(1001, "/tasks")

    asyncio.run(adapter.on_tasks(update, None))  # type: ignore[arg-type]

    assert handler.calls == [("tasks", 1001, "")]
    assert update.effective_message.replies == ["tasks-response"]
    assert update.effective_message.reply_markups[0] is not None


def test_adapter_routes_task_status_callback_and_replies() -> None:
    handler = _FakeBotCommandHandler()
    adapter = TelegramPollingAdapter(command_handler=handler)  # type: ignore[arg-type]
    update = _FakeCallbackUpdate(1001, "task_status:task-1")

    asyncio.run(adapter.on_task_status_callback(update, None))  # type: ignore[arg-type]

    assert handler.calls == [("task_status_callback", 1001, "task_status:task-1")]
    assert update.callback_query.answered is True
    assert update.callback_query.message.replies == ["task-status-callback-response"]


def test_adapter_retries_transient_reply_timeout_and_succeeds() -> None:
    handler = _FakeBotCommandHandler()
    sleep_calls: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    adapter = TelegramPollingAdapter(
        command_handler=handler,  # type: ignore[arg-type]
        retry_attempts=3,
        retry_delay_seconds=0.25,
        sleep_func=fake_sleep,
    )
    update = _FakeUpdate(1001, "/status task-123")
    update.effective_message.failures_before_success = 1

    asyncio.run(adapter.on_status(update, None))  # type: ignore[arg-type]

    assert handler.calls == [("status", 1001, "/status task-123")]
    assert update.effective_message.call_count == 2
    assert update.effective_message.replies == ["status-response"]
    assert sleep_calls == [0.25]


def test_adapter_raises_after_exhausting_reply_retries() -> None:
    handler = _FakeBotCommandHandler()

    async def fake_sleep(delay: float) -> None:
        return None

    adapter = TelegramPollingAdapter(
        command_handler=handler,  # type: ignore[arg-type]
        retry_attempts=2,
        retry_delay_seconds=0.1,
        sleep_func=fake_sleep,
    )
    update = _FakeUpdate(1001, "/help")
    update.effective_message.failures_before_success = 2

    with pytest.raises(TimedOut):
        asyncio.run(adapter.on_help(update, None))  # type: ignore[arg-type]

    assert update.effective_message.call_count == 2


def test_create_polling_application_registers_phase_1_commands() -> None:
    captured_handlers: list[object] = []
    captured_callback_handlers: list[object] = []

    class _FakeApplication:
        def __init__(self) -> None:
            self.handlers: list[object] = []

        def add_handler(self, handler: object) -> None:
            self.handlers.append(handler)

    class _FakeBuilder:
        def __init__(self) -> None:
            self.token_value = ""

        def token(self, value: str) -> "_FakeBuilder":
            self.token_value = value
            return self

        def build(self) -> _FakeApplication:
            return _FakeApplication()

    class _FakeCommandHandler:
        def __init__(self, command: str, callback: object) -> None:
            self.commands = [command]
            self.callback = callback
            captured_handlers.append(self)

    class _FakeCallbackQueryHandler:
        def __init__(self, callback: object, pattern: str) -> None:
            self.callback = callback
            self.pattern = pattern
            captured_callback_handlers.append(self)

    app = create_polling_application(
        bot_token="test-token",
        command_handler=_FakeBotCommandHandler(),  # type: ignore[arg-type]
        application_builder_factory=_FakeBuilder,
        command_handler_factory=_FakeCommandHandler,
        callback_query_handler_factory=_FakeCallbackQueryHandler,
    )

    assert [handler.commands for handler in captured_handlers] == [
        ["task"],
        ["tasks"],
        ["status"],
        ["help"],
    ]
    assert len(captured_handlers) == 4
    assert len(app.handlers) == 5
    assert len(captured_callback_handlers) == 1
    assert captured_callback_handlers[0].pattern == "^task_status:"


def test_create_polling_application_uses_named_callback_data_for_real_buttons(monkeypatch) -> None:
    captured_button_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    class _FakeApplication:
        def __init__(self) -> None:
            self.handlers: list[object] = []

        def add_handler(self, handler: object) -> None:
            self.handlers.append(handler)

    class _FakeBuilder:
        def token(self, value: str) -> "_FakeBuilder":
            return self

        def build(self) -> _FakeApplication:
            return _FakeApplication()

    class _FakeCommandHandler:
        def __init__(self, command: str, callback: object) -> None:
            self.commands = [command]
            self.callback = callback

    class _FakeCallbackQueryHandler:
        def __init__(self, callback: object, pattern: str) -> None:
            self.callback = callback
            self.pattern = pattern

    class _FakeInlineKeyboardButton:
        def __init__(self, *args, **kwargs) -> None:
            captured_button_calls.append((args, kwargs))

    class _FakeInlineKeyboardMarkup:
        def __init__(self, keyboard: object) -> None:
            self.keyboard = keyboard

    monkeypatch.setitem(
        __import__("sys").modules,
        "telegram",
        type(
            "TelegramModule",
            (),
            {
                "InlineKeyboardButton": _FakeInlineKeyboardButton,
                "InlineKeyboardMarkup": _FakeInlineKeyboardMarkup,
            },
        )(),
    )
    monkeypatch.setitem(
        __import__("sys").modules,
        "telegram.ext",
        type(
            "TelegramExtModule",
            (),
            {
                "Application": type("Application", (), {"builder": _FakeBuilder}),
                "CallbackQueryHandler": _FakeCallbackQueryHandler,
                "CommandHandler": _FakeCommandHandler,
            },
        )(),
    )

    app = create_polling_application(
        bot_token="test-token",
        command_handler=_FakeBotCommandHandler(),  # type: ignore[arg-type]
        application_builder_factory=None,
        command_handler_factory=None,
        callback_query_handler_factory=None,
        inline_keyboard_markup_factory=None,
        inline_keyboard_button_factory=None,
    )

    adapter = app.handlers[1].callback
    update = _FakeUpdate(1001, "/tasks")
    asyncio.run(adapter(update, None))

    assert captured_button_calls
    args, kwargs = captured_button_calls[0]
    assert args == ()
    assert kwargs["text"] == "task-1"
    assert kwargs["callback_data"] == "task_status:task-1"


def test_run_telegram_polling_requires_token_env(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime_dir = make_runtime_test_dir("runtime-adapter-missing-token")
    try:
        config_path = _write_min_config(runtime_dir / "config.yaml")
        database_path = runtime_dir / "tasks.sqlite3"
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.setattr("ai_orchestrator.app.DEFAULT_ENV_PATH", runtime_dir / "missing.env")

        with pytest.raises(RuntimeError, match="Missing Telegram bot token"):
            run_telegram_polling(config_path=config_path, database_path=database_path)
    finally:
        remove_runtime_test_dir(runtime_dir)


def test_run_telegram_polling_builds_and_runs_application(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime_dir = make_runtime_test_dir("runtime-adapter-run")
    config_path = _write_min_config(runtime_dir / "config.yaml")
    database_path = runtime_dir / "tasks.sqlite3"

    captured: dict[str, object] = {}

    class _FakeApplication:
        def run_polling(self) -> None:
            captured["ran"] = True

    def _fake_create_polling_application(
        *,
        bot_token: str,
        command_handler: BotCommandHandler,
    ) -> _FakeApplication:
        captured["token"] = bot_token
        captured["handler_type"] = type(command_handler).__name__
        return _FakeApplication()

    monkeypatch.setattr(
        "ai_orchestrator.app.create_polling_application",
        _fake_create_polling_application,
    )
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token-value")

    try:
        run_telegram_polling(config_path=config_path, database_path=database_path)
    finally:
        remove_runtime_test_dir(runtime_dir)

    assert captured["token"] == "token-value"
    assert captured["handler_type"] == "BotCommandHandler"
    assert captured["ran"] is True


def _write_min_config(path: Path) -> Path:
    path.write_text(
        "\n".join(
            [
                "runtime:",
                "  mode: test",
                "  user: test-user",
                "  root_dir: /tmp/root",
                "  data_dir: /tmp/data",
                "  runs_dir: /tmp/runs",
                "  repos_dir: /tmp/repos",
                "  worktrees_dir: /tmp/worktrees",
                "telegram:",
                "  bot_token_env: TELEGRAM_BOT_TOKEN",
                "  allowed_user_ids: [1001]",
                "github:",
                "  token_env: GITHUB_TOKEN",
                "  default_owner: test-owner",
                "  pr_base_branch: main",
                "repositories: {}",
            ]
        ),
        encoding="utf-8",
    )
    return path
