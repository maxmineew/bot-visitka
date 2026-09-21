from collections import Counter
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import texts.demo as texts
from handlers.demo_states import DemoStates
from keyboards.demo import (
    cancel_kb,
    demo_menu_kb,
    nutri_question_kb,
    psy_format_kb,
    result_kb,
)

router = Router(name="demo")


def _life_path_number(date_str: str) -> int:
    digits_sum = sum(int(ch) for ch in date_str if ch.isdigit())
    while digits_sum > 9 and digits_sum not in (11, 22):
        digits_sum = sum(int(ch) for ch in str(digits_sum))
    return digits_sum


@router.callback_query(F.data == "nav:demo")
async def show_demo_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(texts.DEMO_MENU_HEADER, reply_markup=demo_menu_kb())
    await callback.answer()


# --- Психолог -----------------------------------------------------------

@router.callback_query(F.data == "demo:open:psy")
async def psy_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DemoStates.psy_pain)
    await callback.message.answer(texts.PSY_INTRO, reply_markup=cancel_kb())
    await callback.answer()


@router.message(DemoStates.psy_pain)
async def psy_pain_received(message: Message, state: FSMContext) -> None:
    await message.answer(texts.PSY_ASK_FORMAT, reply_markup=psy_format_kb())


@router.callback_query(DemoStates.psy_pain, F.data.startswith("demo:psy:format:"))
async def psy_format_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DemoStates.psy_contact)
    await callback.message.answer(texts.PSY_OFFER, reply_markup=cancel_kb())
    await callback.answer()


@router.message(DemoStates.psy_contact)
async def psy_contact_received(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.PSY_RESULT, reply_markup=result_kb())


# --- Нутрициолог ----------------------------------------------------------

async def _ask_nutri_question(message: Message, step: int) -> None:
    question = texts.NUTRI_QUESTIONS[step - 1]
    await message.answer(question["text"], reply_markup=nutri_question_kb(step, question["options"]))


@router.callback_query(F.data == "demo:open:nutri")
async def nutri_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DemoStates.nutri_quiz)
    await state.update_data(q1=None, q2=None, q3=None)
    await callback.message.answer(texts.NUTRI_INTRO)
    await _ask_nutri_question(callback.message, 1)
    await callback.answer()


@router.callback_query(DemoStates.nutri_quiz, F.data.startswith("demo:nutri:q"))
async def nutri_answer_received(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, question_part, letter = callback.data.split(":")
    step = int(question_part.removeprefix("q"))
    await state.update_data({f"q{step}": letter})

    if step < len(texts.NUTRI_QUESTIONS):
        await _ask_nutri_question(callback.message, step + 1)
        await callback.answer()
        return

    data = await state.get_data()
    await state.clear()
    answers = [data["q1"], data["q2"], data["q3"]]
    majority_letter = Counter(answers).most_common(1)[0][0]
    await callback.message.answer(texts.NUTRI_RESULTS[majority_letter], reply_markup=result_kb())
    await callback.answer()


# --- Нумеролог --------------------------------------------------------

@router.callback_query(F.data == "demo:open:numero")
async def numero_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DemoStates.numero_date)
    await callback.message.answer(texts.NUMERO_INTRO, reply_markup=cancel_kb())
    await callback.answer()


@router.message(DemoStates.numero_date)
async def numero_date_received(message: Message, state: FSMContext) -> None:
    try:
        datetime.strptime((message.text or "").strip(), "%d.%m.%Y")
    except ValueError:
        await message.answer(texts.NUMERO_INVALID_DATE, reply_markup=cancel_kb())
        return

    await state.clear()
    number = _life_path_number(message.text.strip())
    header = texts.NUMERO_RESULT_HEADER.format(number=number)
    interpretation = texts.NUMERO_INTERPRETATIONS[number]
    await message.answer(header + interpretation, reply_markup=result_kb())


# --- AI-агент -------------------------------------------------------------

@router.callback_query(F.data == "demo:open:agent")
async def agent_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DemoStates.agent_chat)
    await state.update_data(turn=0)
    await callback.message.answer(texts.AGENT_INTRO)
    await callback.message.answer(texts.AGENT_TURN_1, reply_markup=cancel_kb())
    await callback.answer()


@router.message(DemoStates.agent_chat)
async def agent_message_received(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    turn = data.get("turn", 0) + 1

    if turn == 1:
        await state.update_data(turn=turn)
        await message.answer(texts.AGENT_TURN_2, reply_markup=cancel_kb())
        return
    if turn == 2:
        await state.update_data(turn=turn)
        await message.answer(texts.AGENT_TURN_3, reply_markup=cancel_kb())
        return

    await state.clear()
    await message.answer(texts.AGENT_RESULT, reply_markup=result_kb())
