from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.databases.database import Users, City_Districts
from bot.keyboards.add_ad import get_ad_type_kb
from bot.keyboards.main import *
from bot.utils.utils import get_text
from bot.states.states import *

router = Router()

@router.callback_query(lambda call: call.data in ['add_ad', 'back_to_choice_city'])
async def add_ad(call: CallbackQuery):
    cities = City_Districts.select(City_Districts.city_name).distinct()

    user = Users.get(Users.user_id == call.from_user.id)
    await call.message.delete()
    await call.message.answer(
        get_text(key='choice_city', lang=user.language),
        reply_markup=get_choice_city_kb(cities, user.language)
    )


@router.callback_query(lambda call: call.data.startswith("choice_city_") or call.data == 'back_to_ad_type_selected')
async def choice_city(call: CallbackQuery, state: FSMContext):
    """
    💾 Сохраняет - Город
    📩 Запрашивает - Тип (Аренда или продажа)
    """

    city = call.data.split('_', 2)[-1]

    user = Users.get(Users.user_id == call.from_user.id)

    await state.update_data(city=city)
    await call.message.edit_text(
        get_text("choose_ad_type", user.language),
        reply_markup=get_ad_type_kb(user.language)
    )
    await state.set_state(AddAd.ad_type)