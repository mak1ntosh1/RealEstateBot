from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.databases.database import City_Districts, Apartment_Parameters
from bot.states.states import SearchSettings
from bot.utils.utils import get_text
from config import settings


def get_ad_type_kb(selected_type=None, lang: str = 'ru'):
    ikb = InlineKeyboardBuilder()

    params = ['rent', 'buy']
    for param in params:
        text = f"✅ {get_text(param, lang)}" if selected_type == param else get_text(param, lang)
        ikb.row(InlineKeyboardButton(text=text, callback_data=f"ad_type_{param}"),)

    ikb.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="cancel_to_menu"))
    return ikb.as_markup()


def get_city_kb(selected_city=None, lang: str = 'ru'):
    ikb = InlineKeyboardBuilder()
    cities = City_Districts.select().distinct(City_Districts.city_name)

    for city in cities:
        text = f"✅ {selected_city}" if selected_city == city.city_name else city.city_name
        ikb.row(InlineKeyboardButton(text=f"🏙 {text}", callback_data=f"city_{city.city_name}"))

    ikb.row(InlineKeyboardButton(text=get_text('any_option', lang), callback_data="any_option_city"))

    ikb.row(
        InlineKeyboardButton(text=get_text('back', lang), callback_data="back"),
        InlineKeyboardButton(text=get_text('next', lang), callback_data="next")
    )
    return ikb.as_markup()


def get_apartment_params_kb(selected_params=None, lang: str = 'ru'):
    if selected_params is None:
        selected_params = []
    ikb = InlineKeyboardBuilder()
    for param in settings.search.PARAMS_SEARCH:
        status = ''  if ('all_params' in selected_params or param not in selected_params) and param != 'all_params' else  "✅"
        text = f'{status} {get_text(param, lang)}'
        ikb.row(InlineKeyboardButton(text=text, callback_data=f"param_{param}"))

    ikb.row(InlineKeyboardButton(text=get_text('any_option', lang), callback_data="any_option_apartment_params"))

    ikb.row(
        InlineKeyboardButton(text=get_text('back', lang), callback_data="back"),
        InlineKeyboardButton(text=get_text('next', lang), callback_data="next")
    )
    return ikb.as_markup()


def get_rent_price_kb(selected_price=None, lang: str = 'ru'):
    ikb = InlineKeyboardBuilder()
    prices = [
        "rent_price_1000", "rent_price_2000", "rent_price_3000", "rent_price_4000", "rent_price_5000",
        "rent_price_6000", "rent_price_7000", "rent_price_8000", "rent_price_9000", "rent_price_10000",
        "rent_price_13000", "rent_price_15000"
    ]
    for price in prices:
        text = f"✅ {get_text(price, lang)}" if selected_price == price else get_text(price, lang)
        ikb.row(InlineKeyboardButton(text=text, callback_data=f"rent_price_{price}"))

    ikb.row(InlineKeyboardButton(text=get_text('any_option', lang), callback_data="any_option_price"))

    ikb.row(
        InlineKeyboardButton(text=get_text('back', lang), callback_data="back"),
        InlineKeyboardButton(text=get_text('next', lang), callback_data="next")
    )
    return ikb.as_markup()


def get_buy_price_kb(selected_price=None, lang: str = 'ru'):
    ikb = InlineKeyboardBuilder()
    prices = [
        "buy_price_50000", "buy_price_100000", "buy_price_200000",
        "buy_price_300000", "buy_price_500000", "buy_price_1000000"
    ]
    for price in prices:
        text = f"✅ {get_text(price, lang)}" if selected_price == price else get_text(price, lang)
        ikb.row(InlineKeyboardButton(text=text, callback_data=f"buy_price_{price}"))

    ikb.row(InlineKeyboardButton(text=get_text('any_option', lang), callback_data="any_option_price"))

    ikb.row(
        InlineKeyboardButton(text=get_text('back', lang), callback_data="back"),
        InlineKeyboardButton(text=get_text('next', lang), callback_data="next")
    )
    return ikb.as_markup()


def get_area_kb(selected_area=None, lang: str = 'ru'):
    ikb = InlineKeyboardBuilder()
    areas = ["area_40m", "area_50m", "area_60m", "area_70m", "area_80m",
             "area_100m", "area_120m", "area_150m", "area_200m", "area_0m"]
    for area in areas:
        text = f"✅ {get_text(area, lang)}" if selected_area == area else get_text(area, lang)
        ikb.row(InlineKeyboardButton(text=text, callback_data=f"area_{area}"))

    ikb.row(InlineKeyboardButton(text=get_text('any_option', lang), callback_data="any_option_area"))

    ikb.row(
        InlineKeyboardButton(text=get_text('back', lang), callback_data="back"),
        InlineKeyboardButton(text=get_text('next', lang), callback_data="next")
    )
    return ikb.as_markup()


def get_district_kb(selected_city=None, selected_districts=None, lang: str = 'ru'):
    if selected_districts is None:
        selected_districts = []
    ikb = InlineKeyboardBuilder()
    if selected_city is not None:
        districts = City_Districts.select().where(City_Districts.city_name == selected_city).distinct(City_Districts.district)
    else:
        districts = City_Districts.select().distinct(City_Districts.district)

    for district in districts:
        text = f"✅ {district.district}" if district.district in selected_districts else district.district
        ikb.row(InlineKeyboardButton(text=text, callback_data=f"district_{district.district}"))

    ikb.row(InlineKeyboardButton(text=get_text('any_option', lang), callback_data="any_option_districts"))

    ikb.row(
        InlineKeyboardButton(text=get_text('back', lang), callback_data="back"),
        InlineKeyboardButton(text=get_text('next', lang), callback_data="next")
    )
    return ikb.as_markup()


def get_property_type_kb2(selected_type=None, lang: str = 'ru'):
    ikb = InlineKeyboardBuilder()
    types = ["residential_property", "commercial_property", 'land']
    for type in types:
        text = f"✅ {get_text(type, lang)}" if selected_type == type else get_text(type, lang)
        ikb.row(InlineKeyboardButton(text=text, callback_data=f"property_type_{type}"))

    ikb.row(InlineKeyboardButton(text=get_text('any_option', lang), callback_data="any_option_property_type"))

    ikb.row(
        InlineKeyboardButton(text=get_text('back', lang), callback_data="back"),
        InlineKeyboardButton(text=get_text('next', lang), callback_data="next")
    )
    return ikb.as_markup()


def get_property_type_kb(selected_type=None, lang: str = 'ru'):
    ikb = InlineKeyboardBuilder()
    types = ["new_building", "secondary"]
    for type in types:
        text = f"✅ {get_text(type, lang)}" if selected_type == type else get_text(type, lang)
        ikb.row(InlineKeyboardButton(text=text, callback_data=f"property_type_{type}"))

    ikb.row(InlineKeyboardButton(text=get_text('any_option', lang), callback_data="any_option_property_type"))

    ikb.row(
        InlineKeyboardButton(text=get_text('back', lang), callback_data="back"),
        InlineKeyboardButton(text=get_text('next', lang), callback_data="next")
    )
    return ikb.as_markup()


def get_confirm_settings_kb(lang: str = 'ru'):
    ikb = InlineKeyboardBuilder()
    ikb.row(
        InlineKeyboardButton(text=get_text('back_to_settings', lang), callback_data="back_to_settings"),
        InlineKeyboardButton(text=get_text('start_search', lang), callback_data="start_search_settings")
    )
    return ikb.as_markup()



def get_search_settings_kb(user, lang):
    active_params = Apartment_Parameters.select().where(
        (Apartment_Parameters.user == user) &
        (Apartment_Parameters.parameter == True)
    )
    selected_params = [
        param.title_parameter for param in active_params
        if param.title_parameter in settings.search.PARAMS_SEARCH
    ]

    all_districts = [district.district for district in City_Districts.select().distinct(City_Districts.district)]
    selected_districts = [
        param.title_parameter for param in active_params
        if param.title_parameter in all_districts
    ]

    return {
        SearchSettings.ad_type: get_ad_type_kb(selected_type=user.ad_type, lang=lang),
        SearchSettings.rent_select_city: get_city_kb(selected_city=user.city, lang=lang),
        SearchSettings.rent_select_apartment_params: get_apartment_params_kb(selected_params=selected_params, lang=lang),
        SearchSettings.rent_select_price: get_rent_price_kb(selected_price=f"rent_price_{user.price}", lang=lang),
        SearchSettings.rent_select_area: get_area_kb(selected_area=f"area_{user.total_area}m", lang=lang),
        SearchSettings.rent_select_district: get_district_kb(
            selected_city=user.city,
            selected_districts=selected_districts,
            lang=lang
        ),
        SearchSettings.buy_select_city: get_city_kb(selected_city=user.city, lang=lang),
        SearchSettings.buy_select_property_type2: get_property_type_kb2(selected_type=user.type_property, lang=lang),
        SearchSettings.buy_select_property_type: get_property_type_kb(selected_type=user.type_property, lang=lang),
        SearchSettings.buy_select_apartment_params: get_apartment_params_kb(selected_params=selected_params, lang=lang),
        SearchSettings.buy_select_price: get_buy_price_kb(selected_price=f"buy_price_{user.price}", lang=lang),
        SearchSettings.buy_select_area: get_area_kb(selected_area=f"area_{user.total_area}m", lang=lang),
        SearchSettings.buy_select_district: get_district_kb(
            selected_city=user.city,
            selected_districts=selected_districts,
            lang=lang
        ),
        SearchSettings.confirm_settings: get_confirm_settings_kb(lang=lang)
    }

