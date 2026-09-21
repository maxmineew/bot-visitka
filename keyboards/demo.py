from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config


def demo_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🧠 Психолог", callback_data="demo:open:psy")
    builder.button(text="🥗 Нутрициолог", callback_data="demo:open:nutri")
    builder.button(text="🔢 Нумеролог", callback_data="demo:open:numero")
    builder.button(text="🤖 AI-агент", callback_data="demo:open:agent")
    builder.button(text="⬅️ В главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Отмена", callback_data="nav:demo")
    return builder.as_markup()


def psy_format_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💻 Онлайн", callback_data="demo:psy:format:online")
    builder.button(text="🏢 Очно", callback_data="demo:psy:format:offline")
    builder.adjust(2)
    return builder.as_markup()


def nutri_question_kb(step: int, options: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for letter, label in options:
        builder.button(text=label, callback_data=f"demo:nutri:q{step}:{letter}")
    builder.adjust(1)
    return builder.as_markup()


def result_kb() -> InlineKeyboardMarkup:
    contact_url = f"https://t.me/{config.CONTACT_USERNAME}"
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Заказать такого бота", url=contact_url)
    builder.button(text="🎮 Другие демо", callback_data="nav:demo")
    builder.button(text="⬅️ В главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()
