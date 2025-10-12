from typing import Callable, Any, Tuple, List

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.databases.database import Realty, City_Districts
from bot.utils.utils import get_text


def create_paginated_keyboard(
    items_on_page: List[Any],
    total_pages: int,
    current_page: int,
    item_to_button_func: Callable[[Any, Any], Tuple[str, str]],
    items_in_row: int = 1,
    nav_prefix: str = "pag",
    other_parameters: dict = None
):
    ikb = InlineKeyboardBuilder()
    """
    Создает инлайн-клавиатуру с элементами страницы и кнопками пагинации,
    используя обычные строковые коллбэки.

    :param items_on_page: Cписок элементов на текущей странице (current_page) для пагинации.
    :param total_pages: Количество страниц
    :param current_page: Текущая страница (начинается с 0).
    :param item_to_button_func: Функция, которая формирует callback_data и текст кнопок
    :param items_in_row: Количество кнопок элементов в одном ряду.
    :param nav_prefix: Префикс для строковых коллбэков навигации (например, "pag").
    :param lang: Язык пользователя
    """

    # --- Добавляем кнопки для элементов текущей страницы ---
    for item in items_on_page:
        button_text, button_callback_data = item_to_button_func(item, other_parameters)
        ikb.button(text=button_text, callback_data=f'{button_callback_data}_{current_page}')

    if items_on_page:
        ikb.adjust(items_in_row)

    # --- Добавляем кнопки пагинации (стрелки и номер страницы) ---
    nav_row: List[InlineKeyboardButton] = []

    # Кнопка "Предыдущая"
    if current_page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{nav_prefix}_{current_page - 1}"  # Формируем строку
            )
        )
    else:
        nav_row.append(InlineKeyboardButton(text=" ", callback_data="ignore_prev"))

    # Индикатор страницы
    nav_row.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}",
            callback_data=f"Null"
        )
    )

    # Кнопка "Следующая"
    if current_page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"{nav_prefix}_{current_page + 1}"  # Формируем строку
            )
        )
    else:
        nav_row.append(InlineKeyboardButton(text=" ", callback_data="ignore_next"))

    ikb.row(*nav_row)
    return ikb


def format_my_ads_for_button(ad: Realty, other_parameters=None) -> Tuple[str, str]:
    """Эта функция используется для форматирования кнопок в пагинации с объектами Ads"""
    button_text = f"{ad.price}€ - {ad.city} - {get_text(ad.ad_type, other_parameters.get('lang'))}"
    callback_data = f"view_ad_{ad.id}"
    return button_text, callback_data


def format_district_for_button(district: City_Districts, other_parameters=None) -> Tuple[str, str]:
    """Эта функция используется для форматирования кнопок в пагинации с объектами Ads"""
    button_text = f"✅ {district.district}" if district.district in other_parameters.get('selected_districts') else f"{district.district}"
    callback_data = f"district_{district.district}"
    return button_text, callback_data