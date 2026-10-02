from aiogram.fsm.state import State, StatesGroup


class ListingForm(StatesGroup):
    title = State()
    price = State()
    category = State()
    description = State()
    photo = State()
    city = State()
    preview = State()
