from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

import texts.privacy as privacy
from analytics.storage import has_consent
from keyboards.consent import consent_kb

_ALLOWED_COMMANDS = ("/start", "/privacy", "/delete_data")
_ALLOWED_CALLBACKS = ("consent:accept", "consent:policy")


class ConsentGateMiddleware(BaseMiddleware):
    """Пока пользователь не дал согласие на обработку данных, бот показывает
    только экран согласия, политику и команду удаления данных."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if user is None or has_consent(user.id):
            return await handler(event, data)

        if isinstance(event, Message):
            if (event.text or "").startswith(_ALLOWED_COMMANDS):
                return await handler(event, data)
            await event.answer(privacy.CONSENT_PROMPT, reply_markup=consent_kb())
            return None

        if isinstance(event, CallbackQuery):
            if event.data in _ALLOWED_CALLBACKS:
                return await handler(event, data)
            await event.message.answer(privacy.CONSENT_PROMPT, reply_markup=consent_kb())
            await event.answer()
            return None

        return await handler(event, data)
