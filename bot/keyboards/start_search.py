from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.databases.database import Favorites, Users
from bot.utils.utils import get_text, get_share_link

def get_realty_card_kb(realty, user_id: int, page, lang: str = 'ru', this_last_one=0):
    ikb = InlineKeyboardBuilder()

    share_link = get_share_link(realty, lang)

    user = Users.get(Users.user_id == user_id)
    is_favorite = bool(Favorites.get_or_none((Favorites.user == user) & (Favorites.realty == realty)) is not None)

    ikb.row(InlineKeyboardButton(
        text=get_text('more_detailed', lang),
        callback_data=f'card_in_detail_{realty.id}_{page}_{this_last_one}'
    ))
    # Кнопки
    ikb.row(
        InlineKeyboardButton(
            text=get_text('remove_from_favorites', lang) if is_favorite else get_text('add_to_favorites', lang),
            callback_data=f"toggle_favorite_{realty.id}_{'remove' if is_favorite else 'add'}_{page}_{this_last_one}_full_0_0"
        ),
        InlineKeyboardButton(text=get_text('share', lang), url=share_link)
    )

    ikb.row(InlineKeyboardButton(text=get_text('make_appointment', lang), callback_data=f"contact_{realty.id}_{this_last_one}_{page}"))

    if this_last_one and page:
        ikb.row(InlineKeyboardButton(text=get_text('utils', lang), callback_data=f"more_{realty.id}_{page + 1}"))

    return ikb.as_markup()


def get_realty_card2_kb(realty, photo_number, user_id: int, lang: str = 'ru', this_last_one=0, page=None, is_favorites=0):
    ikb = InlineKeyboardBuilder()

    share_link = get_share_link(realty, lang)

    user = Users.get(Users.user_id == user_id)
    is_favorite = bool(Favorites.get_or_none((Favorites.user == user) & (Favorites.realty == realty)) is not None)

    if not is_favorites:
        ikb.row(InlineKeyboardButton(
            text=get_text('hide', lang),
            callback_data=f'card_hide_{realty.id}_{page}_{this_last_one}'
        ))
    ikb.row(InlineKeyboardButton(
        text=get_text('next_photo', lang),
        callback_data=f'card_next_photo_{realty.id}_{photo_number}_{page}_{this_last_one}'
    ))

    ikb.row(
        InlineKeyboardButton(
            text=get_text('remove_from_favorites', lang) if is_favorite else get_text('add_to_favorites', lang),
            callback_data=f"toggle_favorite_{realty.id}_{'remove' if is_favorite else 'add'}_{page}_{this_last_one}_hide_{photo_number}_{is_favorites}"
        ),
        InlineKeyboardButton(text=get_text('share', lang), url=share_link)
    )

    ikb.row(InlineKeyboardButton(text=get_text('make_appointment', lang), callback_data=f"contact_{realty.id}_{this_last_one}_{page}"))

    if this_last_one and page and not is_favorites:
        ikb.row(InlineKeyboardButton(text=get_text('utils', lang), callback_data=f"more_{realty.id}_{page + 1}"))

    if is_favorites:
        ikb.row(InlineKeyboardButton(text=get_text('back', lang), callback_data=f"favorites_{page}"))

    return ikb.as_markup()