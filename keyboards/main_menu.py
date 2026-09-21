from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config


def main_menu_kb() -> InlineKeyboardMarkup:
    contact_url = f"https://t.me/{config.CONTACT_USERNAME}"
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Живые демо", callback_data="nav:demo")
    builder.button(text="👉 Посмотреть кейсы", callback_data="nav:cases")
    builder.button(text="🚀 Заказать разработку", url=contact_url)
    builder.button(text="🙋‍♂️ Обо мне", callback_data="nav:about")
    builder.button(text="💻 Портфолио на GitHub", url=config.GITHUB_URL)
    builder.button(text="📩 Связаться со мной", url=contact_url)
    builder.adjust(1)
    return builder.as_markup()


def back_to_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:main"))
    return builder.as_markup()
