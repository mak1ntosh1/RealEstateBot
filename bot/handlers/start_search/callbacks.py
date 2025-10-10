from contextlib import suppress

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile

from bot.databases.database import Users, Realty, Favorites
from bot.keyboards.main import get_realty_cards_favorites_kb
from bot.keyboards.start_search import get_realty_card_kb, get_realty_card2_kb
from bot.utils.utils import get_text, search_realty, get_text_info_ad_incomplete, get_text_info_ad_full
from config import COUNT_CARDS_IN_BATCH, BOT_NAME

router = Router()


@router.callback_query(F.data.startswith("start_search"))
async def start_search(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_', 2)
    without_filters = None
    if len(data) == 3:
        without_filters = data[-1]
    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    search_results = await search_realty(user, without_filters)

    if search_results:
        result_text = f"{get_text('search_started', lang)}\n\n" \
                      f"{get_text('search_results_found', lang)} {len(search_results)}\n"

        for realty in search_results[:COUNT_CARDS_IN_BATCH]:
            text = get_text_info_ad_incomplete(realty, lang)

            await call.message.answer(text, reply_markup=get_realty_card_kb(
                realty, user.user_id, page=1, lang=lang
            ))
        if len(search_results) >= COUNT_CARDS_IN_BATCH:
            realty = search_results[COUNT_CARDS_IN_BATCH]
            text = get_text_info_ad_incomplete(realty, lang)

            await call.message.answer(text, reply_markup=get_realty_card_kb(
                realty, user.user_id, page=1, lang=lang, this_last_one=1
            ))
    else:
        result_text = f"{get_text('search_started', lang)}\n\n" \
                      f"{get_text('no_results_found', lang)}"

    await call.message.edit_text(result_text)
    await state.clear()


@router.callback_query(F.data.startswith("more_"))
async def more(call: CallbackQuery):
    realty_id = call.data.split('_', 2)[-2]
    page = int(call.data.split('_', 2)[-1])
    realty = Realty.get(Realty.id == realty_id)
    user = realty.user
    lang = user.language

    await call.message.edit_reply_markup(
        reply_markup=get_realty_card_kb(realty, user.user_id, page=page, lang=lang)
    )

    search_results = await search_realty(user)

    if search_results:
        start_idx = (page - 1) * COUNT_CARDS_IN_BATCH
        end_idx = min(page * COUNT_CARDS_IN_BATCH, len(search_results))

        result_text = f"{get_text('search_started', lang)}\n\n" \
                      f"{get_text('search_results_found', lang)} {len(search_results)}\n"

        for realty in search_results[start_idx:end_idx]:
            text = get_text_info_ad_incomplete(realty, lang)

            await call.message.answer(text, reply_markup=get_realty_card_kb(
                realty, user.user_id, page=page, lang=lang
            ))
        if len(search_results) >= end_idx:
            realty = search_results[end_idx]
            text = get_text_info_ad_incomplete(realty, lang)

            await call.message.answer(text, reply_markup=get_realty_card_kb(
                realty, user.user_id, page=page, lang=lang, this_last_one=1,
            ))
    else:
        result_text = f"{get_text('search_started', lang)}\n\n" \
                      f"{get_text('no_results_found', lang)}"

    await call.message.edit_text(result_text)



@router.callback_query(F.data.startswith("contact_"))
async def get_contact(call: CallbackQuery):
    realty_id = call.data.split('_', 3)[-3]
    this_last_one = call.data.split('_', 3)[-2]
    page = int(call.data.split('_', 3)[-1])
    realty = Realty.get(Realty.id == realty_id)
    user = realty.user
    lang = user.language
    contact = realty.contact

    result_text = get_text_info_ad_incomplete(realty, lang) + f'\n\n📞 Контактная информация: {contact}'
    keyboard = get_realty_card_kb(
        realty, user.user_id, page=page, lang=lang, this_last_one=this_last_one
    )

    with suppress(Exception):
        await call.message.edit_text(
            result_text,
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("card_in_detail_"))
async def card_in_detail(call: CallbackQuery, new_call_data=None, is_favorites=False):
    call_data = new_call_data if is_favorites else call.data
    realty_id = call_data.split('_', 5)[-3]
    page = int(call_data.split('_', 5)[-2])
    this_last_one = int(call_data.split('_', 5)[-1])

    realty = Realty.get(Realty.id == realty_id)
    user = realty.user
    lang = user.language

    photo_number = 1

    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None

    if photo:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(photo.photo_path),
                caption=get_text_info_ad_full(realty, lang)
            ),
            reply_markup=get_realty_card2_kb(
                realty, photo_number + 1, user.user_id, page=page, lang=lang, this_last_one=this_last_one, is_favorites=is_favorites
            )
        )
    else:
        await call.message.edit_text(
            text=get_text_info_ad_full(realty, lang),
            reply_markup=get_realty_card2_kb(
                realty, photo_number + 1, user.user_id, page=page, lang=lang, this_last_one=this_last_one, is_favorites=is_favorites
            )
        )
        await call.answer(get_text('no_photos', lang))


@router.callback_query(F.data.startswith("card_hide_"))
async def card_hide(call: CallbackQuery):
    realty_id = call.data.split('_', 4)[-3]
    page = int(call.data.split('_', 4)[-2])
    this_last_one = int(call.data.split('_', 4)[-1])

    realty = Realty.get(Realty.id == realty_id)
    user = realty.user
    lang = user.language

    try:
        await call.message.edit_text(
            text=get_text_info_ad_incomplete(realty, lang),
            reply_markup=get_realty_card_kb(
                realty, user.user_id, page=page, lang=lang, this_last_one=this_last_one
            )
        )
    except Exception as e:
        print(e)
        await call.message.delete()
        await call.message.answer(
            text=get_text_info_ad_incomplete(realty, lang),
            reply_markup=get_realty_card_kb(
                realty, user.user_id, page=page, lang=lang, this_last_one=this_last_one
            )
        )


@router.callback_query(F.data.startswith("card_next_photo_"))
async def card_next_photo(call: CallbackQuery):
    realty_id = call.data.split('_', 6)[-4]
    photo_number = int(call.data.split('_', 6)[-3])
    page = int(call.data.split('_', 6)[-2])
    this_last_one = int(call.data.split('_', 6)[-1])

    realty = Realty.get(Realty.id == realty_id)
    user = realty.user
    lang = user.language

    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None

    if photo:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(photo.photo_path),
                caption=get_text_info_ad_full(realty, lang)
            ),
            reply_markup=get_realty_card2_kb(
                realty, photo_number + 1, user.user_id, page=page, lang=lang, this_last_one=this_last_one
            )
        )
    else:
        await call.answer(get_text('no_photos', lang))


@router.callback_query(F.data.startswith("toggle_favorite_"))
async def toggle_favorite(call: CallbackQuery):
    realty_id = call.data.split('_', 8)[-7]
    method = call.data.split('_', 8)[-6]
    page = int(call.data.split('_', 8)[-5])
    this_last_one = int(call.data.split('_', 8)[-4])
    type_card = call.data.split('_', 8)[-3]
    photo_number = int(call.data.split('_', 8)[-2])
    is_favorites = int(call.data.split('_', 8)[-1])

    user = Users.get(Users.user_id == call.from_user.id)
    realty = Realty.get(Realty.id == realty_id)

    lang = user.language

    if method == 'add':
        Favorites.create(
            user=user,
            realty=realty
        )
    else:
        favorite = Favorites.get((Favorites.user == user) & (Favorites.realty == realty))
        favorite.delete_instance()

    if is_favorites:
        user = Users.get(Users.user_id == call.from_user.id)
        lang = user.language
        favorites = Favorites.select().where(Favorites.user == user)
        await call.message.delete()

        if favorites:
            keyboard = await get_realty_cards_favorites_kb(favorites, page, call, lang)

            with suppress(Exception):
                await call.message.delete()
            await call.message.answer(
                text=get_text('your_list_favorites', lang),
                reply_markup=keyboard
            )
        else:
            await call.answer('no_favorites')
    else:
        await call.message.edit_reply_markup(
            reply_markup=get_realty_card_kb(
                realty, user.user_id, page=page, lang=lang, this_last_one=this_last_one
            ) if type_card == 'full' else get_realty_card2_kb(
                realty, photo_number, user.user_id, page=page, lang=lang, this_last_one=this_last_one, is_favorites=is_favorites
            )
        )






