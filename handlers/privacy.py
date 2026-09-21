from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import texts.messages as texts
import texts.privacy as privacy
from analytics.storage import erase_user, give_consent
from keyboards.main_menu import main_menu_kb

router = Router(name="privacy")


@router.message(Command("privacy"))
async def cmd_privacy(message: Message) -> None:
    await message.answer(privacy.POLICY)


@router.callback_query(F.data == "consent:policy")
async def show_policy(callback: CallbackQuery) -> None:
    await callback.message.answer(privacy.POLICY)
    await callback.answer()


@router.callback_query(F.data == "consent:accept")
async def accept_consent(callback: CallbackQuery) -> None:
    give_consent(callback.from_user.id, privacy.POLICY_VERSION)
    await callback.message.edit_text(privacy.CONSENT_ACCEPTED)
    await callback.message.answer(texts.WELCOME, reply_markup=main_menu_kb())
    await callback.answer()


@router.message(Command("delete_data"))
async def cmd_delete_data(message: Message, state: FSMContext) -> None:
    await state.clear()
    erase_user(message.from_user.id)
    await message.answer(privacy.DELETED)
