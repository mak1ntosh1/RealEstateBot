from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


class CustomFilter(Filter):
    def __init__(self, state_class, back_to_where, filter_expression: bool):
        self.state_class = state_class
        self.filter_expression = filter_expression
        self.back_to_where = back_to_where

    async def __call__(self, call: CallbackQuery, state: FSMContext) -> bool:
        current_state = await state.get_state()
        return (current_state == self.state_class and self.filter_expression) or call.data == self.back_to_where
















