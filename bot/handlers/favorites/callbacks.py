from contextlib import suppress

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile

from bot.databases.database import Users, Realty, Favorites
from bot.handlers.start_search.callbacks import card_in_detail
from bot.keyboards.main import *
from bot.utils.utils import get_text
from config import FAVORITES_ADS

router = Router()


@router.callback_query(F.data.startswith("favorites_"))
async def favorites_(call: CallbackQuery):
    page = int(call.data.split('_', 1)[-1])

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language
    favorites = Favorites.select().where(Favorites.user == user)


    if favorites:
        keyboard = await get_realty_cards_favorites_kb(favorites, page, call, lang)

        with suppress(Exception):
            await call.message.delete()
        await call.message.answer_photo(
            photo=FAVORITES_ADS,
            caption=get_text('your_list_favorites', lang),
            reply_markup=keyboard
        )
    else:
        await call.answer(get_text('no_favorites', lang))


@router.callback_query(F.data.startswith("favorite_"))
async def favorite(call: CallbackQuery):
    realty_id = int(call.data.split('_', 2)[-2])
    page = int(call.data.split('_', 2)[-1])

    realty = Realty.get_or_none((Realty.id == realty_id))

    new_call_data = f'card_in_detail_{realty.id}_{page}_0'
    await card_in_detail(call, new_call_data, is_favorites=1)