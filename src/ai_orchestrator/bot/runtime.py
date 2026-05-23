"""Runtime Telegram adapter for the current polling command set."""

from __future__ import annotations

import asyncio
from typing import Any, Callable
from collections.abc import Awaitable

from ai_orchestrator.bot.handlers import BotCommandHandler
from telegram.error import TimedOut


class TelegramPollingAdapter:
    """Bridge python-telegram-bot updates to existing command handlers."""

    def __init__(
        self,
        command_handler: BotCommandHandler,
        inline_keyboard_markup_factory: Callable[[list[list[Any]]], Any] | None = None,
        inline_keyboard_button_factory: Callable[[str, str], Any] | None = None,
        retry_attempts: int = 3,
        retry_delay_seconds: float = 1.0,
        sleep_func: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self._command_handler = command_handler
        self._inline_keyboard_markup_factory = (
            inline_keyboard_markup_factory
            if inline_keyboard_markup_factory is not None
            else (lambda keyboard: {"inline_keyboard": keyboard})
        )
        self._inline_keyboard_button_factory = (
            inline_keyboard_button_factory
            if inline_keyboard_button_factory is not None
            else (lambda text, callback_data: {"text": text, "callback_data": callback_data})
        )
        self._retry_attempts = retry_attempts
        self._retry_delay_seconds = retry_delay_seconds
        self._sleep = sleep_func if sleep_func is not None else asyncio.sleep

    async def on_task(self, update: Any, context: Any) -> None:
        if update.effective_user is None or update.effective_message is None:
            return
        command_text = update.effective_message.text or "/task"
        response = self._command_handler.handle_task_command(
            user_id=update.effective_user.id,
            command_text=command_text,
        )
        await self._call_with_retries(update.effective_message.reply_text, response)

    async def on_status(self, update: Any, context: Any) -> None:
        if update.effective_user is None or update.effective_message is None:
            return
        command_text = update.effective_message.text or "/status"
        response = self._command_handler.handle_status_command(
            user_id=update.effective_user.id,
            command_text=command_text,
        )
        await self._call_with_retries(update.effective_message.reply_text, response)

    async def on_tasks(self, update: Any, context: Any) -> None:
        if update.effective_user is None or update.effective_message is None:
            return
        response, menu_items = self._command_handler.handle_tasks_command(
            user_id=update.effective_user.id,
        )
        if not menu_items:
            await self._call_with_retries(update.effective_message.reply_text, response)
            return

        keyboard = [
            [self._inline_keyboard_button_factory(item.label, item.callback_data)]
            for item in menu_items
        ]
        reply_markup = self._inline_keyboard_markup_factory(keyboard)
        await self._call_with_retries(
            update.effective_message.reply_text,
            response,
            reply_markup=reply_markup,
        )

    async def on_help(self, update: Any, context: Any) -> None:
        if update.effective_user is None or update.effective_message is None:
            return
        response = self._command_handler.handle_help_command(
            user_id=update.effective_user.id,
        )
        await self._call_with_retries(update.effective_message.reply_text, response)

    async def on_approve(self, update: Any, context: Any) -> None:
        if update.effective_user is None or update.effective_message is None:
            return
        command_text = update.effective_message.text or "/approve"
        response = self._command_handler.handle_approve_command(
            user_id=update.effective_user.id,
            command_text=command_text,
        )
        await self._call_with_retries(update.effective_message.reply_text, response)

    async def on_reject(self, update: Any, context: Any) -> None:
        if update.effective_user is None or update.effective_message is None:
            return
        command_text = update.effective_message.text or "/reject"
        response = self._command_handler.handle_reject_command(
            user_id=update.effective_user.id,
            command_text=command_text,
        )
        await self._call_with_retries(update.effective_message.reply_text, response)

    async def on_task_status_callback(self, update: Any, context: Any) -> None:
        if update.effective_user is None or update.callback_query is None:
            return
        callback_data = update.callback_query.data or ""
        response = self._command_handler.handle_task_status_callback(
            user_id=update.effective_user.id,
            callback_data=callback_data,
        )
        await self._call_with_retries(update.callback_query.answer)
        await self._call_with_retries(update.callback_query.message.reply_text, response)

    async def _call_with_retries(
        self, operation: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any
    ) -> Any:
        """Retry transient Telegram timeout failures a small number of times."""

        for attempt in range(1, self._retry_attempts + 1):
            try:
                return await operation(*args, **kwargs)
            except TimedOut:
                if attempt >= self._retry_attempts:
                    raise
                await self._sleep(self._retry_delay_seconds)
        return None


def create_polling_application(
    *,
    bot_token: str,
    command_handler: BotCommandHandler,
    application_builder_factory: Callable[[], Any] | None = None,
    command_handler_factory: Callable[[str, Callable[..., Any]], Any] | None = None,
    callback_query_handler_factory: Callable[..., Any] | None = None,
    inline_keyboard_markup_factory: Callable[[list[list[Any]]], Any] | None = None,
    inline_keyboard_button_factory: Callable[[str, str], Any] | None = None,
) -> Any:
    """Create a polling application and register the current command handlers."""

    if (
        application_builder_factory is None
        or command_handler_factory is None
        or callback_query_handler_factory is None
        or inline_keyboard_markup_factory is None
        or inline_keyboard_button_factory is None
    ):
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CallbackQueryHandler, CommandHandler

        if application_builder_factory is None:
            application_builder_factory = Application.builder
        if command_handler_factory is None:
            command_handler_factory = CommandHandler
        if callback_query_handler_factory is None:
            callback_query_handler_factory = CallbackQueryHandler
        if inline_keyboard_markup_factory is None:
            inline_keyboard_markup_factory = InlineKeyboardMarkup
        if inline_keyboard_button_factory is None:

            def inline_keyboard_button_factory(text: str, callback_data: str) -> Any:
                return InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data,
                )

    application = application_builder_factory().token(bot_token).build()
    adapter = TelegramPollingAdapter(
        command_handler=command_handler,
        inline_keyboard_markup_factory=inline_keyboard_markup_factory,
        inline_keyboard_button_factory=inline_keyboard_button_factory,
    )
    application.add_handler(command_handler_factory("task", adapter.on_task))
    application.add_handler(command_handler_factory("tasks", adapter.on_tasks))
    application.add_handler(command_handler_factory("status", adapter.on_status))
    application.add_handler(command_handler_factory("approve", adapter.on_approve))
    application.add_handler(command_handler_factory("reject", adapter.on_reject))
    application.add_handler(command_handler_factory("help", adapter.on_help))
    application.add_handler(
        callback_query_handler_factory(
            adapter.on_task_status_callback,
            pattern="^task_status:",
        )
    )
    return application
