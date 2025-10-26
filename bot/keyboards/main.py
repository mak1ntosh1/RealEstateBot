import math

from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.databases.database import Realty
from bot.keyboards.utils import create_paginated_keyboard, format_my_ads_for_button
from bot.utils.utils import get_text, get_share_link_to_bot
from config import settings


def get_choice_lang_kb(ad_id=None):
    ikb = InlineKeyboardBuilder()
    ikb.row(
        InlineKeyboardButton(text='English 🇬🇧', callback_data=f'choice_lang_en_{ad_id}'),
        InlineKeyboardButton(text='Türk 🇹🇷', callback_data=f'choice_lang_tr_{ad_id}')
    )
    ikb.row(
        InlineKeyboardButton(text='Русский 🇷🇺', callback_data=f'choice_lang_ru_{ad_id}')
    )
    return ikb.as_markup()


def get_main_menu_kb(lang):
    ikb = InlineKeyboardBuilder()
    share_link = get_share_link_to_bot(lang)

    ikb.row(InlineKeyboardButton(text=get_text('start_search_without_filters', lang), callback_data="start_search_without_filters"))
    ikb.row(
        InlineKeyboardButton(text=get_text('start_search', lang), callback_data="start_search"),
        InlineKeyboardButton(text=get_text(key='set_up_search', lang=lang), callback_data='set_up_search'),
    )
    ikb.row(
        InlineKeyboardButton(text=get_text(key='add_ad', lang=lang), callback_data='add_ad'),
        InlineKeyboardButton(text=get_text(key='my_ads', lang=lang), callback_data='my_ads'),
        InlineKeyboardButton(text=get_text(key='favorites', lang=lang), callback_data='favorites_1'),
        InlineKeyboardButton(text=get_text(key='change_lang', lang=lang), callback_data='change_lang'),
        width=1
    )
    ikb.row(
        InlineKeyboardButton(text=get_text(key='support', lang=lang), url=settings.bot.SUPPORT_URL),
        InlineKeyboardButton(text=get_text(key='share', lang=lang), url=share_link),
    )
    return ikb.as_markup()


def get_main_menu_reply_kb(lang):
    ikb = ReplyKeyboardBuilder()
    ikb.row(KeyboardButton(text=get_text(key='main_menu_reply', lang=lang)))
    return ikb.as_markup(resize_keyboard=True)


def get_choice_city_kb(cities, lang):
    ikb = InlineKeyboardBuilder()
    for city in cities:
        ikb.row(InlineKeyboardButton(text=city.city_name, callback_data=f'choice_city_{city.city_name}'))

    ikb.row(InlineKeyboardButton(text=get_text('cancel', lang), callback_data=f'cancel_to_menu'))
    return ikb.as_markup(resize_keyboard=True)


def get_my_ads_kb(current_page, lang, user):
    total_ads_count = user.ads.count()
    # total_pages должна быть не меньше 1, если есть хоть 1 объявление
    total_pages = (total_ads_count + settings.bot.COUNT_IN_PAGE - 1) // settings.bot.COUNT_IN_PAGE if total_ads_count > 0 else 1

    # 1. Если элементов нет, страница должна быть 1 (хотя total_pages = 1)
    if total_ads_count == 0:
        current_page = 1
    # 2. Страница не может быть меньше 1
    elif current_page < 1:
        current_page = 1
    # 3. Страница не может превышать общее количество страниц
    elif current_page > total_pages:
        current_page = total_pages

    # Если current_page = 1, OFFSET = 0. OFFSET всегда >= 0.
    offset = (current_page - 1) * settings.bot.COUNT_IN_PAGE

    ads_on_page = user.ads.select().order_by(Realty.created_at.desc()).limit(settings.bot.COUNT_IN_PAGE).offset(offset)

    other_parameters = {'lang': lang}

    ikb = create_paginated_keyboard(
        items_on_page=list(ads_on_page),
        total_pages=total_pages,
        current_page=current_page,
        item_to_button_func=format_my_ads_for_button,
        items_in_row=1,
        nav_prefix='my_ads',
        other_parameters=other_parameters
    )

    ikb.row(InlineKeyboardButton(text=get_text('cancel', lang), callback_data=f'cancel_to_menu'))
    return ikb.as_markup(resize_keyboard=True)


def get_my_ad_kb(realty_id, photo_number, lang):
    ikb = InlineKeyboardBuilder()
    ikb.row(
        InlineKeyboardButton(text=get_text('next_photo', lang), callback_data=f'user_next_photo_{realty_id}_{photo_number}')
    )
    ikb.row(
        InlineKeyboardButton(text=get_text('remove_ad', lang), callback_data=f'remove_ad_{realty_id}')
    )

    ikb.row(InlineKeyboardButton(text=get_text('cancel', lang), callback_data=f'my_ads'))
    return ikb.as_markup(resize_keyboard=True)


async def get_realty_cards_favorites_kb(favorites, page, call, lang):
    ikb = InlineKeyboardBuilder()

    if len(favorites) > settings.bot.COUNT_IN_PAGE:
        total_pages = math.ceil(len(favorites) / settings.bot.COUNT_IN_PAGE)

        if page <= 0 or (total_pages < page):
            await call.answer('Дальше страниц нет!')
            return None
        else:
            start_idx = (page - 1) * settings.bot.COUNT_IN_PAGE

            end_idx = min(page * settings.bot.COUNT_IN_PAGE, len(favorites))
            count = start_idx
            for favorite in favorites[start_idx:end_idx]:
                ad = favorite.realty
                ikb.row(InlineKeyboardButton(
                    text=f'{ad.price} € - {ad.city} - {get_text(ad.ad_type, "ru")}',
                    callback_data=f'favorite_{ad.id}_{page}'
                ))
                count += 1

            ikb.row(
                InlineKeyboardButton(text='⬅️', callback_data=f'favorites_{page - 1}'),
                InlineKeyboardButton(text=f'{page}/{total_pages}', callback_data='-'),
                InlineKeyboardButton(text='➡️', callback_data=f'favorites_{page + 1}')
            )
    else:
        count = 1
        for favorite in favorites:
            ad = favorite.realty
            ikb.row(InlineKeyboardButton(
                text=f'{ad.price} € - {ad.city} - {get_text(ad.ad_type, "ru")}',
                callback_data=f'favorite_{ad.id}_{page}'
            ))
            count += 1

    ikb.row(InlineKeyboardButton(text=get_text('cancel', lang), callback_data=f'cancel_to_menu'))

    return ikb.as_markup(resize_keyboard=True)


