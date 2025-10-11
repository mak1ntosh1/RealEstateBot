from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state

from bot.databases.database import Users
from bot.keyboards.setting_search import *
from bot.keyboards.start_search import get_realty_card_kb
from bot.utils.utils import search_realty, get_text_info_ad_incomplete
from bot.states.states import SearchSettings
from config import settings

router = Router()


# Запуск настройки поиска
@router.callback_query(F.data == "set_up_search", any_state)
async def start_configure_search(call: CallbackQuery, state: FSMContext):
    user = Users.get_or_none(user_id=call.from_user.id)
    ad_type = user.ad_type
    await state.update_data(ad_type=ad_type)

    lang = user.language if user and user.language else 'ru'
    await state.set_state(SearchSettings.ad_type)
    await call.message.delete()
    await call.message.answer_photo(
        photo=settings.ImageIDs.SETTINGS_SEARCH,
        caption=get_text('select_ad_type', lang),
        reply_markup=get_ad_type_kb(user.ad_type, lang)
    )
    await call.answer()


# Выбор типа недвижимости (Аренда/Покупка)
@router.callback_query(SearchSettings.ad_type, F.data.startswith("ad_type_"))
async def select_ad_type(call: CallbackQuery, state: FSMContext):
    ad_type = call.data.split("_")[-1]  # rent или buy
    await state.update_data(ad_type=ad_type)

    user = Users.get(Users.user_id == call.from_user.id)
    user.ad_type = ad_type
    user.save()

    lang = user.language if user.language else 'ru'

    next_state = SearchSettings.rent_select_city if user.ad_type == "rent" else SearchSettings.buy_select_city
    await state.set_state(next_state)
    await call.message.edit_caption(caption=get_text('select_city', lang), reply_markup=get_city_kb(user.city, lang=lang))
    await call.answer()


# Выбор города
@router.callback_query(F.data.startswith("city_"))
async def select_city(call: CallbackQuery, state: FSMContext):
    city = call.data.split("_", 1)[-1]

    await state.update_data(city=city)

    user = Users.get(Users.user_id == call.from_user.id)
    user.city = city
    user.save()

    lang = user.language if user.language else 'ru'
    current_state = await state.get_state()
    next_state = {
        SearchSettings.rent_select_city: SearchSettings.rent_select_apartment_params,
        SearchSettings.buy_select_city: SearchSettings.buy_select_property_type2
    }.get(current_state)
    await state.set_state(next_state)
    if user.ad_type == 'rent':
        active_params = Apartment_Parameters.select().where(
            (Apartment_Parameters.user == user) &
            (Apartment_Parameters.parameter == True)
        )
        filtered_params = [
            param.title_parameter for param in active_params
            if param.title_parameter in settings.SearchConstants.PARAMS_SEARCH
        ]

        await call.message.edit_caption(caption=get_text('select_apartment_params', lang),
                                     reply_markup=get_apartment_params_kb(filtered_params, lang=lang))
    else:
        await call.message.edit_caption(caption=get_text('select_property_type', lang),
                                     reply_markup=get_property_type_kb2(user.type_property, lang=lang))
    await call.answer()


# Выбор типа недвижимости (для покупки: Жилая недвижимость/Коммерческая недвижимость)
@router.callback_query(SearchSettings.buy_select_property_type2, F.data.startswith("property_type_"))
async def select_property_type2(call: CallbackQuery, state: FSMContext):
    type_object = call.data.split("_", maxsplit=2)[-1]
    await state.update_data(buy_select_property_type2=type_object)

    user = Users.get(Users.user_id == call.from_user.id)
    user.type_object = type_object
    user.save()

    lang = user.language if user.language else 'ru'

    active_params = Apartment_Parameters.select().where(
        (Apartment_Parameters.user == user) &
        (Apartment_Parameters.parameter == True)
    )
    filtered_params = [
        param.title_parameter for param in active_params
        if param.title_parameter in settings.SearchConstants.PARAMS_SEARCH
    ]

    if type_object == 'land':
        await state.set_state(SearchSettings.buy_select_apartment_params)
        await call.message.edit_caption(caption=get_text('select_apartment_params', lang),
                                     reply_markup=get_apartment_params_kb(filtered_params, lang=lang))
    else:
        await state.set_state(SearchSettings.buy_select_property_type)
        await call.message.edit_caption(caption=get_text('choose_residential_type', lang),
                                     reply_markup=get_property_type_kb(user.type_property, lang=lang))
    await call.answer()


# Выбор вида недвижимости (для покупки: Новостройки/Вторичное)
@router.callback_query(SearchSettings.buy_select_property_type, F.data.startswith("property_type_"))
async def select_property_type(call: CallbackQuery, state: FSMContext):
    property_type = call.data.split("_", maxsplit=2)[-1]
    await state.update_data(buy_select_property_type=property_type)

    user = Users.get(Users.user_id == call.from_user.id)
    user.type_property = property_type
    user.save()

    lang = user.language if user.language else 'ru'

    active_params = Apartment_Parameters.select().where(
        (Apartment_Parameters.user == user) &
        (Apartment_Parameters.parameter == True)
    )
    filtered_params = [
        param.title_parameter for param in active_params
        if param.title_parameter in settings.SearchConstants.PARAMS_SEARCH
    ]

    await state.set_state(SearchSettings.buy_select_apartment_params)
    await call.message.edit_caption(caption=get_text('select_apartment_params', lang),
                                 reply_markup=get_apartment_params_kb(filtered_params, lang=lang))
    await call.answer()


# Выбор параметров квартиры
@router.callback_query(F.data.startswith("param_"))
async def select_apartment_params(call: CallbackQuery, state: FSMContext):
    param = call.data.split("_", 1)[-1]
    user = Users.get(Users.user_id == call.from_user.id)

    selected_params = [
        param.title_parameter for param in user.parameters
        if param.title_parameter in settings.SearchConstants.PARAMS_SEARCH
    ]

    if param in selected_params:
        user_param = Apartment_Parameters.get(
            (Apartment_Parameters.user == user) &
            (Apartment_Parameters.title_parameter == param)
        )
        user_param.delete_instance()
        selected_params.remove(param)
    else:
        Apartment_Parameters.create(user=user, title_parameter=param, parameter=True)
        selected_params.append(param)


    await call.message.edit_reply_markup(reply_markup=get_apartment_params_kb(selected_params, lang=user.language))
    await call.answer()


# Выбор цены (аренда)
@router.callback_query(SearchSettings.rent_select_price, F.data.startswith("rent_price_"))
async def select_rent_price(call: CallbackQuery, state: FSMContext):
    price_key = call.data.split("_", 2)[-1]
    price_text = get_text(price_key, 'ru')  # Для сохранения текста в state

    await state.update_data(price=price_text)

    user = Users.get(Users.user_id == call.from_user.id)
    user.price = int(price_text.replace("до ", "").replace("€", "").replace(" ", ""))
    user.save()

    lang = user.language if user.language else 'ru'
    await state.set_state(SearchSettings.rent_select_area)
    await call.message.edit_caption(caption=get_text('select_area', lang), reply_markup=get_area_kb(user.total_area, lang=lang))
    await call.answer()


# Выбор цены (покупка)
@router.callback_query(SearchSettings.buy_select_price, F.data.startswith("buy_price_"))
async def select_buy_price(call: CallbackQuery, state: FSMContext):
    price_key = call.data.split("_", 2)[-1]
    price_text = get_text(price_key, 'ru')  # Для сохранения текста в state
    await state.update_data(price=price_text)

    user = Users.get(Users.user_id == call.from_user.id)
    user.price = int(price_text.replace("до ", "").replace("€", "").replace(" ", ""))
    user.save()

    lang = user.language if user.language else 'ru'
    await state.set_state(SearchSettings.buy_select_area)
    await call.message.edit_caption(caption=get_text('select_area', lang), reply_markup=get_area_kb(user.total_area, lang=lang))
    await call.answer()


# Выбор площади
@router.callback_query(F.data.startswith("area_"))
async def select_area(call: CallbackQuery, state: FSMContext):
    area_key = call.data.split("_", 1)[-1]
    area_text = get_text(area_key, 'ru')  # Для сохранения текста в state

    await state.update_data(area=area_text)

    user = Users.get(Users.user_id == call.from_user.id)
    user.total_area = int(area_text.replace("от ", "").replace("м²", "").replace("∞ (без ограничений)", "0")) or 0
    user.save()

    lang = user.language if user.language else 'ru'
    current_state = await state.get_state()
    next_state = {
        SearchSettings.rent_select_area: SearchSettings.rent_select_district,
        SearchSettings.buy_select_area: SearchSettings.buy_select_district
    }.get(current_state)
    await state.set_state(next_state)

    active_params = Apartment_Parameters.select().where(
        (Apartment_Parameters.user == user) &
        (Apartment_Parameters.parameter == True)
    )
    all_districts = [district.district for district in City_Districts.select().distinct(City_Districts.district)]
    selected_districts = [
        param.title_parameter for param in active_params
        if param.title_parameter in all_districts
    ]

    await call.message.edit_caption(caption=get_text('select_district', lang), reply_markup=get_district_kb(user.city, selected_districts, lang=lang))
    await call.answer()


# Выбор района
@router.callback_query(F.data.startswith("district_"))
async def select_district(call: CallbackQuery, state: FSMContext):
    user = Users.get(Users.user_id == call.from_user.id)
    district = call.data.split("_", 1)[-1]

    all_districts = [district.district for district in City_Districts.select().distinct(City_Districts.district)]
    selected_districts = [
        param.title_parameter for param in user.parameters
        if param.title_parameter in all_districts
    ]
    print(selected_districts)
    if district in selected_districts:
        user_district = Apartment_Parameters.get(
            (Apartment_Parameters.user == user) &
            (Apartment_Parameters.title_parameter == district)
        )
        user_district.delete_instance()
        selected_districts.remove(district)
    else:
        Apartment_Parameters.create(user=user, title_parameter=district, parameter=True)
        selected_districts.append(district)

    print(selected_districts)


    await state.update_data(districts=selected_districts)

    await call.message.edit_reply_markup(reply_markup=get_district_kb(user.city, selected_districts, lang=user.language))
    await call.answer()



# Навигация: Далее
@router.callback_query(F.data == "next")
async def next_step(call: CallbackQuery, state: FSMContext):
    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    current_state = await state.get_state()
    state_map = {
        SearchSettings.ad_type: SearchSettings.rent_select_city,
        SearchSettings.rent_select_city: SearchSettings.rent_select_apartment_params,
        SearchSettings.rent_select_apartment_params: SearchSettings.rent_select_price,
        SearchSettings.rent_select_price: SearchSettings.rent_select_area,
        SearchSettings.rent_select_area: SearchSettings.rent_select_district,
        SearchSettings.rent_select_district: SearchSettings.confirm_settings,
        SearchSettings.buy_select_city: SearchSettings.buy_select_property_type2,
        SearchSettings.buy_select_property_type2: SearchSettings.buy_select_property_type,
        SearchSettings.buy_select_property_type: SearchSettings.buy_select_apartment_params,
        SearchSettings.buy_select_apartment_params: SearchSettings.buy_select_price,
        SearchSettings.buy_select_price: SearchSettings.buy_select_area,
        SearchSettings.buy_select_area: SearchSettings.buy_select_district,
        SearchSettings.buy_select_district: SearchSettings.confirm_settings,
    }
    next_state = state_map.get(current_state)
    if next_state:
        await state.set_state(next_state)
        texts = {
            SearchSettings.rent_select_city: get_text('select_city', lang),
            SearchSettings.rent_select_apartment_params: get_text('select_apartment_params', lang),
            SearchSettings.rent_select_price: get_text('select_rent_price', lang),
            SearchSettings.rent_select_area: get_text('select_area', lang),
            SearchSettings.rent_select_district: get_text('select_district', lang),
            SearchSettings.buy_select_property_type2: get_text('select_property_type', lang),
            SearchSettings.buy_select_property_type: get_text('choose_residential_type', lang),
            SearchSettings.buy_select_apartment_params: get_text('select_apartment_params', lang),
            SearchSettings.buy_select_price: get_text('select_buy_price', lang),
            SearchSettings.buy_select_area: get_text('select_area', lang),
            SearchSettings.buy_select_district: get_text('select_district', lang),
            SearchSettings.confirm_settings: await format_settings_text(call.from_user.id, await state.get_data(), lang)
        }
        keyboard = get_search_settings_kb(user, lang)
        await call.message.edit_caption(caption=texts[next_state], reply_markup=keyboard[next_state])
    await call.answer()


# Навигация: Далее
@router.callback_query(F.data.startswith("any_option_"))
async def any_option(call: CallbackQuery, state: FSMContext):
    option = call.data.split("_", 2)[-1]
    user = Users.get(Users.user_id == call.from_user.id)

    match option:
        case 'city':
            await state.update_data(city=None)
            user.city = None
            user.save()
        case 'apartment_params':
            await state.update_data(apartment_params=None)

            params = [
                param for param in user.parameters
                if param.title_parameter in settings.SearchConstants.PARAMS_SEARCH
            ]
            [user_param.delete_instance() for user_param in params]

        case 'price':
            await state.update_data(price=None)
            user.price = None
            user.save()
        case 'area':
            await state.update_data(area=None)
            user.total_area = None
            user.save()
        case 'districts':
            await state.update_data(districts=None)
            all_districts = [district.district for district in City_Districts.select().distinct(City_Districts.district)]

            user_districts = [
                param for param in user.parameters
                if param.title_parameter in all_districts
            ]
            [user_district.delete_instance() for user_district in user_districts]

        case 'property_type':
            await state.update_data(buy_select_property_type=None)
            user.type_property = None
            user.save()

    await next_step(call, state)


# Навигация: Назад
@router.callback_query(F.data == "back")
async def back_step(call: CallbackQuery, state: FSMContext):
    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language if user.language else 'ru'

    current_state = await state.get_state()
    state_map = {
        SearchSettings.rent_select_apartment_params: SearchSettings.rent_select_city,
        SearchSettings.rent_select_price: SearchSettings.rent_select_apartment_params,
        SearchSettings.rent_select_area: SearchSettings.rent_select_price,
        SearchSettings.rent_select_district: SearchSettings.rent_select_area,
        SearchSettings.buy_select_property_type: SearchSettings.buy_select_property_type2,
        SearchSettings.buy_select_property_type2: SearchSettings.buy_select_city,
        SearchSettings.buy_select_apartment_params:
            SearchSettings.buy_select_property_type2 if user.type_object == 'land'
            else SearchSettings.buy_select_property_type,
        SearchSettings.buy_select_price: SearchSettings.buy_select_apartment_params,
        SearchSettings.buy_select_area: SearchSettings.buy_select_price,
        SearchSettings.buy_select_district: SearchSettings.buy_select_area,
        SearchSettings.confirm_settings: SearchSettings.rent_select_district
        if (await state.get_data()).get("ad_type") == "rent"
        else SearchSettings.buy_select_district
    }
    prev_state = state_map.get(current_state, SearchSettings.ad_type)
    await state.set_state(prev_state)
    texts = {
        SearchSettings.ad_type: get_text('select_ad_type', lang),
        SearchSettings.rent_select_city: get_text('select_city', lang),
        SearchSettings.rent_select_apartment_params: get_text('select_apartment_params', lang),
        SearchSettings.rent_select_price: get_text('select_rent_price', lang),
        SearchSettings.rent_select_area: get_text('select_area', lang),
        SearchSettings.rent_select_district: get_text('select_district', lang),
        SearchSettings.buy_select_city: get_text('select_city', lang),
        SearchSettings.buy_select_property_type2: get_text('select_property_type', lang),
        SearchSettings.buy_select_property_type: get_text('choose_residential_type', lang),
        SearchSettings.buy_select_apartment_params: get_text('select_apartment_params', lang),
        SearchSettings.buy_select_price: get_text('select_buy_price', lang),
        SearchSettings.buy_select_area: get_text('select_area', lang),
        SearchSettings.buy_select_district: get_text('select_district', lang)
    }
    keyboard = get_search_settings_kb(user, lang)
    await call.message.edit_caption(caption=texts[prev_state], reply_markup=keyboard[prev_state])
    await call.answer()


# Форматирование текста с настройками
async def format_settings_text(user_id: int, data: dict, lang: str = 'ru') -> str:
    user = Users.get_or_none(user_id=user_id)

    params = [
        param.title_parameter for param in user.parameters
        if param.title_parameter in settings.SearchConstants.PARAMS_SEARCH
    ]

    ad_type = get_text(data.get("ad_type", "rent"), lang)
    city = get_text("not_selected", lang) if data.get("city") is None else data.get("city", get_text("not_selected", lang))
    property_type = get_text(data.get("property_type", "not_selected"), lang) if ad_type == get_text("buy", lang) else None
    price = get_text("not_selected", lang) if data.get("price") is None else data.get("price", get_text("not_selected", lang))
    area = get_text("not_selected", lang) if data.get("area") is None else data.get("area", get_text("not_selected", lang))
    districts = [] if data.get("districts") is None else data.get("districts", [])
    districts = ", ".join([d for d in districts]) or get_text("not_selected", lang)

    text = f"{get_text('confirm_settings', lang)}\n\n" \
           f"{get_text('ad_type_label', lang)} {ad_type}\n" \
           f"{get_text('city_label', lang)} {city}\n"
    if property_type:
        text += f"{get_text('property_type_label', lang)} {property_type}\n"
    text += f"{get_text('apartment_params_label', lang)} {', '.join([get_text(p, lang) for p in params]) or get_text('not_selected', lang)}\n" \
            f"{get_text('budget_label', lang)} {price}\n" \
            f"{get_text('area_label', lang)} {area}\n" \
            f"{get_text('districts_label', lang)} {districts}\n"
    text += get_text('edit_settings_search', lang)
    return text


# Подтверждение настроек
@router.callback_query(SearchSettings.confirm_settings, F.data == "back_to_settings")
async def back_to_settings(call: CallbackQuery, state: FSMContext):
    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language if user.language else 'ru'

    data = await state.get_data()
    prev_state = SearchSettings.rent_select_district if data.get(
        "ad_type") == "rent" else SearchSettings.buy_select_district
    await state.set_state(prev_state)
    await call.message.edit_caption(caption=get_text('select_district', lang),
                                 reply_markup=get_district_kb(user.city, data.get("districts", []), lang=lang))
    await call.answer()


@router.callback_query(F.data == "start_search_settings")
async def start_search(call: CallbackQuery, state: FSMContext):
    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    data = await state.get_data()

    # Формируем текст с настройками
    settings_text = await format_settings_text(call.from_user.id, data, lang)

    # Выполняем поиск
    search_results = await search_realty(user)

    # Формируем ответ
    if search_results:
        result_text = f"{settings_text}\n\n{get_text('search_started', lang)}\n\n" \
                      f"{get_text('search_results_found', lang)} {len(search_results)}\n"
        for realty in search_results[:4]:  # Ограничиваем до 5 результатов для примера
            text = get_text_info_ad_incomplete(realty, lang)

            await call.message.answer(text, reply_markup=get_realty_card_kb(
                realty.id, user.user_id, lang
            ))
        if len(search_results) >= 5:
            realty = search_results[4]
            text = get_text_info_ad_incomplete(realty, lang)

            await call.message.answer(text, reply_markup=get_realty_card_kb(
                realty.id, user.user_id, page=1, lang=lang, this_last_one=True
            ))
    else:
        result_text = f"{settings_text}\n\n{get_text('search_started', lang)}\n\n" \
                      f"{get_text('no_results_found', lang)}"

    await call.message.edit_caption(caption=result_text)
    await state.clear()
    await call.answer()


