from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import texts.messages as texts
import texts.privacy as privacy
from analytics.storage import has_consent
from keyboards.consent import consent_kb
from keyboards.main_menu import main_menu_kb

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not has_consent(message.from_user.id):
        await message.answer(privacy.CONSENT_PROMPT, reply_markup=consent_kb())
        return
    await message.answer(texts.WELCOME, reply_markup=main_menu_kb())
