from aiogram.fsm.state import State, StatesGroup

class BookingStates(StatesGroup):
    choosing_date = State()
    choosing_time = State()
    input_name = State()
    input_phone = State()

class AdminStates(StatesGroup):
    adding_slot_date = State()
    adding_slot_time = State()
    closing_day = State()