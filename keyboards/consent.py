from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def consent_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Согласен", callback_data="consent:accept")
    builder.button(text="📄 Политика конфиденциальности", callback_data="consent:policy")
    builder.adjust(1)
    return builder.as_markup()
