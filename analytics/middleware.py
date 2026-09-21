from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from analytics.export import schedule_export
from analytics.storage import record_event


class VisitTrackingMiddleware(BaseMiddleware):
    """Пишет в локальную базу факт визита без сбора персональных данных
    (см. analytics/storage.py) и планирует обновление Excel-отчёта."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if user is not None:
            action = _describe(event)
            record_event(user.id, action)
            schedule_export()
        return await handler(event, data)


def _describe(event: TelegramObject) -> str:
    if isinstance(event, Message):
        # Не сохраняем произвольный текст, который может ввести пользователь
        # (потенциально персональные данные) — только имя команды, если это команда.
        text = event.text or ""
        if text.startswith("/"):
            return text.split()[0]
        return "<текстовое сообщение>"
    if isinstance(event, CallbackQuery):
        return event.data or "<callback без данных>"
    return type(event).__name__
