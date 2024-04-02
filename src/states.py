from aiogram.fsm.state import State, StatesGroup


# Состояние
class UserInfo(StatesGroup):
    name = State()
    phone_number = State()
    comment = State()
