from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.loader import Case


def case_card_kb(case: Case) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if case.review:
        builder.button(text="💬 Отзыв", callback_data=f"case:review:{case.id}")
    if case.detailed_case:
        builder.button(text="📖 Подробнее", callback_data=f"case:detail:{case.id}")
    for label, url in case.links.items():
        builder.button(text=f"🔗 {label}", url=url)
    builder.button(text="⬅️ К списку кейсов", callback_data="nav:cases")
    builder.button(text="⬅️ В главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def back_to_card_kb(case_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ К кейсу", callback_data=f"case:open:{case_id}")
    builder.button(text="⬅️ В главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()
