from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import texts.messages as texts
from keyboards.main_menu import back_to_main_kb, main_menu_kb

router = Router(name="main_menu")


@router.callback_query(F.data == "nav:main")
async def show_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(texts.WELCOME, reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "nav:about")
async def show_about(callback: CallbackQuery) -> None:
    await callback.message.edit_text(texts.ABOUT_ME, reply_markup=back_to_main_kb())
    await callback.answer()
