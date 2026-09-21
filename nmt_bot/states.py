from aiogram.fsm.state import State, StatesGroup


class Practice(StatesGroup):
    choosing_letters = State()
    testing = State()
