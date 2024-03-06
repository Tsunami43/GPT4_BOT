from aiogram.dispatcher.filters.state import StatesGroup, State


class GenerateText(StatesGroup):
    S1 = State()


class GenerateImage(StatesGroup):
    Image_512 = State()

class PaymentsState(StatesGroup):
    EnterEmail = State()

class GPT4PaymentsState(StatesGroup):
    EnterEmail = State()