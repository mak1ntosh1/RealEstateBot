import math

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from peewee import fn

from bot.databases.database import Realty
from bot.utils.utils import get_text
from config import settings


def get_admin_panel_kb():
    ikb = InlineKeyboardBuilder()
    ikb.row(
        InlineKeyboardButton(text="Рассылка 📢", callback_data="admin_mailing"),
        InlineKeyboardButton(text="Управление объявлениями ⚙️", callback_data="all_ads_1"),
        width=1
    )
    return ikb.as_markup(resize_keyboard=True)



def get_cancel_mailing_kb():
    ikb = InlineKeyboardBuilder()

    ikb.row(InlineKeyboardButton(text='Отмена', callback_data=f'back_to_admin_panel'))

    return ikb.as_markup()


async def get_list_all_ads_kb(page, call):
    ikb = InlineKeyboardBuilder()
    # 1. Получаем общее количество объявлений (быстрый запрос COUNT)
    total_ads_count = Realty.select(fn.COUNT(Realty.id)).scalar()

    # 2. Расчет общего количества страниц
    total_pages = math.ceil(total_ads_count / settings.bot.COUNT_IN_PAGE) if total_ads_count > 0 else 1

    # 3. Корректировка страницы для предотвращения отрицательного OFFSET
    if page < 1:
        page = 1
    # Если запрашиваемая страница больше общего количества, но объявления есть, отвечаем и выходим.
    if total_ads_count > 0 and page > total_pages:
        await call.answer('Дальше страниц нет!')
        return None

    # 4. Расчет OFFSET
    start_idx = (page - 1) * settings.bot.COUNT_IN_PAGE

    # 5. Получаем ТОЛЬКО нужные объявления (LIMIT и OFFSET)
    ads_on_page = (
        Realty.select()
        .order_by(Realty.consent_admin.asc(nulls='FIRST'))
        .limit(settings.bot.COUNT_IN_PAGE)
        .offset(start_idx)
    )
    ads_list = list(ads_on_page)

    if total_ads_count > settings.bot.COUNT_IN_PAGE:

        count = start_idx
        for ad in ads_list:
            status = '✅' if ad.consent_admin else '🔘' if ad.consent_admin is None else '🥷'

            ikb.row(InlineKeyboardButton(
                text=f'{status} {ad.price}€ - {ad.city} - {get_text(ad.ad_type, "ru")}',
                callback_data=f'admin_view_ad_{ad.id}_{page}'
            ))
            count += 1

        big_jump_right = page + 10 if total_pages > page + 10 else total_pages
        big_jump_left = page - 10 if page - 10 > 1 else 1

        ikb.row(
            InlineKeyboardButton(text='⬅️', callback_data=f'all_ads_{big_jump_left}'),
            InlineKeyboardButton(text='⬅️', callback_data=f'all_ads_{page - 1}'),
            InlineKeyboardButton(text=f'{page}/{total_pages}', callback_data='all_ads'),
            InlineKeyboardButton(text='➡️', callback_data=f'all_ads_{page + 1}'),
            InlineKeyboardButton(text='⏩', callback_data=f'all_ads_{big_jump_right}')
        )

    else:
        count = 1
        for ad in ads_list:
            status = '✅' if ad.consent_admin else '🔘' if ad.consent_admin is None else '🥷'

            ikb.row(InlineKeyboardButton(
                text=f'{status} {ad.price} € - {ad.city} - {get_text(ad.ad_type, "ru")}',
                callback_data=f'admin_view_ad_{ad.id}_{page}'
            ))
            count += 1

    ikb.row(InlineKeyboardButton(text='↩ Назад', callback_data=f'back_to_admin_panel'))

    return ikb.as_markup()


def get_manage_realty_kb(realty_id, consent_admin, photo_number, page) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='🔘 Подробнее', callback_data=f'admin_in_detail_{realty_id}_{photo_number}_{page}')
    )
    builder.row(
        InlineKeyboardButton(text='🔄 Следующее фото', callback_data=f'admin_next_photo_{realty_id}_{photo_number}_{page}')
    )

    if consent_admin is None:
        builder.row(
            InlineKeyboardButton(text='✅ Опубликовать', callback_data=f'admin_accept_realty_{realty_id}_{photo_number}_{page}'),
            InlineKeyboardButton(text='❌ Отклонить', callback_data=f'admin_decline_realty_{realty_id}_{photo_number}_{page}'),
        )
    elif consent_admin:
        builder.row(InlineKeyboardButton(text='🥷 Скрыть', callback_data=f'admin_decline_realty_{realty_id}_{photo_number}_{page}'))
    else:
        builder.row(InlineKeyboardButton(text='✅ Опубликовать', callback_data=f'admin_accept_realty_{realty_id}_{photo_number}_{page}'))

    builder.row(InlineKeyboardButton(text='↩ Назад', callback_data=f'all_ads_{page}'))

    return builder.as_markup()


def get_manage_realty2_kb(realty_id, consent_admin, photo_number, page) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='▫️ скрыть', callback_data=f'admin_hide_details_{realty_id}_{photo_number}_{page}')
    )
    builder.row(
        InlineKeyboardButton(text='🔄 Следующее фото', callback_data=f'admin_next_photo2_{realty_id}_{photo_number}_{page}')
    )
    if consent_admin is None:
        builder.row(
            InlineKeyboardButton(text='✅ Опубликовать', callback_data=f'admin_accept_realty_{realty_id}_{photo_number}_{page}'),
            InlineKeyboardButton(text='❌ Отклонить', callback_data=f'decline_realty_{realty_id}_{photo_number}_{page}'),
        )
    elif consent_admin:
        builder.row(InlineKeyboardButton(text='🥷 Скрыть', callback_data=f'admin_decline_realty_{realty_id}_{photo_number}_{page}'))
    else:
        builder.row(InlineKeyboardButton(text='✅ Опубликовать', callback_data=f'admin_accept_realty_{realty_id}_{photo_number}_{page}'))

    builder.row(InlineKeyboardButton(text='↩ Назад', callback_data=f'all_ads_{page}'))
    return builder.as_markup()
