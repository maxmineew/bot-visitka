from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

import texts.messages as texts
from content.loader import Case, featured_cases, get_case, other_cases
from keyboards.case_card import back_to_card_kb, case_card_kb
from keyboards.cases_menu import cases_list_kb, other_cases_kb

router = Router(name="cases")

TELEGRAM_MESSAGE_LIMIT = 4096
ASSETS_DIR = Path(__file__).parent.parent / "assets" / "cases"


def format_case_card(case: Case) -> str:
    lines = [f"<b>{case.title}</b>", ""]
    if case.client:
        lines.append(f"👤 <b>Клиент:</b> {case.client}")
    if case.product:
        lines.append(f"🧩 <b>Продукт:</b> {case.product}")
    if case.tasks:
        lines.append("")
        lines.append("✅ <b>Задачи бота:</b>")
        lines.extend(f"— {task}" for task in case.tasks)
    if case.result:
        lines.append("")
        lines.append(f"📈 <b>Результат:</b> {case.result}")
    return "\n".join(lines)


async def _send_long_text(callback: CallbackQuery, text: str, reply_markup=None) -> None:
    if len(text) <= TELEGRAM_MESSAGE_LIMIT:
        await callback.message.answer(text, reply_markup=reply_markup)
        return
    chunks = [text[i:i + TELEGRAM_MESSAGE_LIMIT] for i in range(0, len(text), TELEGRAM_MESSAGE_LIMIT)]
    for chunk in chunks[:-1]:
        await callback.message.answer(chunk)
    await callback.message.answer(chunks[-1], reply_markup=reply_markup)


@router.callback_query(F.data == "nav:cases")
async def show_cases_list(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(texts.CASES_LIST_HEADER, reply_markup=cases_list_kb(featured_cases()))
    await callback.answer()


@router.callback_query(F.data == "case:more")
async def show_other_cases(callback: CallbackQuery) -> None:
    lines = [texts.OTHER_CASES_HEADER]
    for case in other_cases():
        lines.append(f"▫️ <b>{case.title}</b> — {case.product}")
    await callback.message.answer("\n".join(lines), reply_markup=other_cases_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("case:open:"))
async def open_case(callback: CallbackQuery) -> None:
    case_id = callback.data.removeprefix("case:open:")
    case = get_case(case_id)
    if case is None:
        await callback.answer(texts.CASE_NOT_FOUND, show_alert=True)
        return

    if case.images:
        image_path = ASSETS_DIR / case.id / case.images[0]
        if image_path.exists():
            await callback.message.answer_photo(FSInputFile(image_path))

    await _send_long_text(callback, format_case_card(case), reply_markup=case_card_kb(case))
    await callback.answer()


@router.callback_query(F.data.startswith("case:review:"))
async def show_review(callback: CallbackQuery) -> None:
    case_id = callback.data.removeprefix("case:review:")
    case = get_case(case_id)
    if case is None or not case.review:
        await callback.answer(texts.CASE_NOT_FOUND, show_alert=True)
        return
    await _send_long_text(callback, f"💬 <b>Отзыв клиента</b>\n\n{case.review}", reply_markup=back_to_card_kb(case.id))
    await callback.answer()


@router.callback_query(F.data.startswith("case:detail:"))
async def show_detail(callback: CallbackQuery) -> None:
    case_id = callback.data.removeprefix("case:detail:")
    case = get_case(case_id)
    if case is None or not case.detailed_case:
        await callback.answer(texts.CASE_NOT_FOUND, show_alert=True)
        return
    await _send_long_text(callback, case.detailed_case, reply_markup=back_to_card_kb(case.id))
    await callback.answer()


@router.callback_query()
async def unknown_callback(callback: CallbackQuery) -> None:
    await callback.answer(texts.UNKNOWN_ACTION, show_alert=True)
