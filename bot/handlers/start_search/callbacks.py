from contextlib import suppress

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
from peewee import fn

from bot.databases.database import Users, Realty, Favorites
from bot.keyboards.main import get_realty_cards_favorites_kb
from bot.keyboards.start_search import get_realty_card_kb, get_realty_card2_kb
from bot.utils.utils import get_text, search_realty, get_text_info_ad_incomplete, get_text_info_ad_full
from config import COUNT_CARDS_IN_BATCH, SEARCH

router = Router()


@router.callback_query(F.data.startswith("start_search"))
async def start_search(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_', 2)
    without_filters = None
    if len(data) == 3:
        without_filters = data[-1]

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    # Получение QuerySet и применение LIMIT/OFFSET
    search_query = await search_realty(user, without_filters)

    # Задаем LIMIT для первой страницы: на 1 больше, чтобы проверить наличие следующей
    limit = COUNT_CARDS_IN_BATCH + 1
    offset = 0  # Первая страница всегда OFFSET=0

    # Применяем лимит и загружаем данные (выполняем SQL-запрос)
    search_query = search_query.limit(limit).offset(offset)
    search_results = list(search_query)

    # Подготовка данных для отображения
    realty_to_show = search_results[:COUNT_CARDS_IN_BATCH]

    # Проверяем, есть ли следующая страница (если результатов больше, чем лимит пачки)
    has_more = len(search_results) > COUNT_CARDS_IN_BATCH

    # Выполняем быстрый запрос COUNT для получения общего числа
    total_results_count = search_query.select(fn.COUNT(Realty.id)).scalar()

    result_text = f"{get_text('search_started', lang)}\n\n"
    if realty_to_show:
        result_text += f"{get_text('search_results_found', lang)} <code>{total_results_count}</code>"
    else:
        result_text += f"{get_text('no_results_found', lang)}"

    await call.message.answer_photo(
        photo=SEARCH,
        caption=result_text
    )

    if realty_to_show:
        for idx, realty_item in enumerate(realty_to_show):
            text = get_text_info_ad_incomplete(realty_item, lang)

            # Определяем, является ли объявление последним (если есть следующая страница)
            is_last_one = has_more and idx == len(realty_to_show) - 1

            await call.message.answer(
                text,
                reply_markup=get_realty_card_kb(
                    realty_item,
                    user.user_id,
                    page=1,
                    lang=lang,
                    this_last_one=1 if is_last_one else 0
                )
            )
    await state.clear()


@router.callback_query(F.data.startswith("more_"))
async def more(call: CallbackQuery):
    # more_<realty_id>_<page>
    try:
        data_parts = call.data.split('_')
        realty_id = data_parts[-2]
        page = int(data_parts[-1])
    except (IndexError, ValueError):
        # Обработка некорректного колбэка
        await call.answer("Ошибка данных.", show_alert=True)
        return

    # Загрузка realty и user (необходимо для языка и параметров поиска)
    realty_id = int(realty_id)
    realty = Realty.get(Realty.id == realty_id)
    user = realty.user
    lang = user.language

    # Определение LIMIT и OFFSET для пагинации
    # LIMIT = Загружаем на 1 объявление больше, чтобы понять, есть ли следующая страница.
    limit = COUNT_CARDS_IN_BATCH + 1
    offset = (page - 1) * COUNT_CARDS_IN_BATCH

    # Вызов оптимизированного поиска
    search_query = await search_realty(user)

    # Применяем LIMIT/OFFSET к QuerySet
    search_query = search_query.limit(limit).offset(offset)

    # Загружаем данные из БД (выполняем запрос)
    search_results = list(search_query)

    # Обновление первого сообщения (удаление старой карточки)
    await call.message.edit_reply_markup(
        reply_markup=get_realty_card_kb(realty, user.user_id, page=page, lang=lang)
    )

    realty_to_show = search_results[:COUNT_CARDS_IN_BATCH]
    print(realty_to_show)
    has_more = len(search_results) > COUNT_CARDS_IN_BATCH
    print(has_more)
    if realty_to_show:
        result_text = f"{get_text('search_started', lang)}\n\n" \
                      f"{get_text('search_results_found', lang)} (Часть {page})"

        await call.message.edit_text(result_text)

        # Отправка объявлений
        for idx, realty_item in enumerate(realty_to_show):
            text = get_text_info_ad_incomplete(realty_item, lang)

            # Определяем, является ли объявление последним в пачке
            is_last_one = has_more and idx == len(realty_to_show) - 1

            # Отправляем карточку
            await call.message.answer(
                text,
                reply_markup=get_realty_card_kb(
                    realty_item,
                    user.user_id,
                    page=page,
                    lang=lang,
                    this_last_one=1 if is_last_one else 0
                )
            )

    else:
        # Результатов нет
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
        try:
            await call.message.edit_caption(
                caption=get_text_info_ad_full(realty, lang),
                reply_markup=get_realty_card2_kb(
                    realty, photo_number + 1, user.user_id, page=page, lang=lang, this_last_one=this_last_one, is_favorites=is_favorites
                )
            )
        except Exception as e:
            await call.message.edit_text(
                text=get_text_info_ad_full(realty, lang),
                reply_markup=get_realty_card2_kb(
                    realty, photo_number + 1, user.user_id, page=page, lang=lang, this_last_one=this_last_one,
                    is_favorites=is_favorites
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






