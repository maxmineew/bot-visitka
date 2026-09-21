from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import Case


def cases_list_kb(cases: list[Case]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for case in cases:
        builder.button(text=case.title, callback_data=f"case:open:{case.id}")
    builder.button(text="📁 Ещё кейсы", callback_data="case:more")
    builder.button(text="⬅️ В главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def other_cases_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ К основным кейсам", callback_data="nav:cases")
    builder.button(text="⬅️ В главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()
