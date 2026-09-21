from aiogram.fsm.state import State, StatesGroup


class DemoStates(StatesGroup):
    psy_pain = State()
    psy_contact = State()
    nutri_quiz = State()
    numero_date = State()
    agent_chat = State()
