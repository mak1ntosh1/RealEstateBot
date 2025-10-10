from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.utils import get_text
from config import *



# Кнопки для создания объявления
def get_ad_type_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('rent', lang), callback_data="rent"),
        InlineKeyboardButton(text=get_text('sell', lang), callback_data="sale")
    )
    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="back_to_choice_city"))
    return builder.as_markup()


def get_property_type_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('residential_property', lang), callback_data="residential_property"),
        InlineKeyboardButton(text=get_text('commercial_property', lang), callback_data="commercial_property"),
        InlineKeyboardButton(text=get_text('land', lang), callback_data="land"),
    )
    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="back_to_ad_type_selected"))
    builder.adjust(1)
    return builder.as_markup()


def get_object_type_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('new_building', lang), callback_data="new_building"),
        InlineKeyboardButton(text=get_text('secondary', lang), callback_data="secondary"),
    )
    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="back_to_type_property_selected"))
    builder.adjust(1)
    return builder.as_markup()


def get_furniture_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('furnished_yes', lang), callback_data="furnished_yes"),
        InlineKeyboardButton(text=get_text('furnished_no', lang), callback_data="furnished_no")
    )
    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="back_to_type_property_selected"))
    builder.adjust(1)
    return builder.as_markup()


def get_animals_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('animals_yes', lang), callback_data="animals_yes"),
        InlineKeyboardButton(text=get_text('animals_no', lang), callback_data="animals_no"),
        InlineKeyboardButton(text=get_text('animals_maybe', lang), callback_data="animals_maybe")
    )
    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="back_to_furniture_selected"))
    builder.adjust(1)
    return builder.as_markup()


def get_children_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('children_yes', lang), callback_data="children_yes"),
        InlineKeyboardButton(text=get_text('children_no', lang), callback_data="children_no"),
        InlineKeyboardButton(text=get_text('children_maybe', lang), callback_data="children_maybe")
    )
    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="back_to_animals_selected"))
    builder.adjust(1)
    return builder.as_markup()


def get_rooms_kb(lang, callback_data_str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for param in PARAMS_CREATE:
        builder.row(InlineKeyboardButton(text=get_text(param, lang), callback_data=f"rooms_{param}"))

    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data=callback_data_str))
    builder.adjust(1)
    return builder.as_markup()


def get_back_from_message_kb(lang, callback_data_str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data=callback_data_str))
    builder.adjust(1)
    return builder.as_markup()


def get_districts_kb(lang, districts):
    builder = InlineKeyboardBuilder()
    print(districts)
    for district in districts:
        builder.row(InlineKeyboardButton(text=district.district, callback_data=f'choice_district_{district.district}'))

    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="back_to_price_entered"))
    builder.adjust(1)
    return builder.as_markup()


def get_skip_street_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_text('skip', lang), callback_data='skip_street'))
    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="back_to_district_selected"))
    builder.adjust(1)
    return builder.as_markup()


def get_skip_description_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_text('skip', lang), callback_data='skip_description'))
    builder.row(InlineKeyboardButton(text=get_text('back', lang), callback_data="back_to_floor_in_house_entered"))
    builder.adjust(1)
    return builder.as_markup()


def get_agency_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_text('owner', lang), callback_data='owner'))
    builder.row(InlineKeyboardButton(text=get_text('realtor', lang), callback_data='realtor'))
    builder.adjust(1)
    return builder.as_markup()


def get_back_to_description_entered_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_text('stop', lang), callback_data='go_to_name_entered'))
    builder.adjust(1)
    return builder.as_markup()


def get_consent_admin_kb(realty_id, consent_admin, photo_number) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='🔘 Подробнее', callback_data=f'in_detail_{realty_id}_{photo_number}')
    )
    builder.row(
        InlineKeyboardButton(text='🔄 Следующее фото', callback_data=f'next_photo_{realty_id}_{photo_number}')
    )

    if consent_admin is None:
        builder.row(
            InlineKeyboardButton(text='✅ Опубликовать', callback_data=f'accept_realty_{realty_id}_{photo_number}'),
            InlineKeyboardButton(text='❌ Отклонить', callback_data=f'decline_realty_{realty_id}_{photo_number}'),
        )
    elif consent_admin:
        builder.row(InlineKeyboardButton(text='✅ Опубликовано', callback_data=f'-'))
    else:
        builder.row(InlineKeyboardButton(text='❌ Отклонено', callback_data=f'-'))

    return builder.as_markup()


def get_consent_admin2_kb(realty_id, consent_admin, photo_number) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='▫️ скрыть', callback_data=f'hide_details_{realty_id}_{photo_number}')
    )
    builder.row(
        InlineKeyboardButton(text='🔄 Следующее фото', callback_data=f'next_photo2_{realty_id}_{photo_number}')
    )
    if consent_admin is None:
        builder.row(
            InlineKeyboardButton(text='✅ Опубликовать', callback_data=f'accept_realty_{realty_id}_{photo_number}'),
            InlineKeyboardButton(text='❌ Отклонить', callback_data=f'decline_realty_{realty_id}_{photo_number}'),
        )
    elif consent_admin:
        builder.row(InlineKeyboardButton(text='✅ Опубликовано', callback_data=f'-'))
    else:
        builder.row(InlineKeyboardButton(text='❌ Отклонено', callback_data=f'-'))

    return builder.as_markup()


