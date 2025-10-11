from urllib.parse import quote

from bot.databases.database import *
from bot.texts.lexicon_en import LEXICON_EN
from bot.texts.lexicon_ru import LEXICON_RU
from bot.texts.lexicon_tr import LEXICON_TR


def get_text(key: str, lang: str = 'ru') -> str:
    """ get text based on language settings """
    match lang:
        case 'tr':
            return LEXICON_TR.get(key)
        case 'ru':
            return LEXICON_RU.get(key)
        case _: # by default in English
            return LEXICON_EN.get(key)


def get_text_info_ad_full(realty, lang, result: bool = None) -> str:
    result = get_text('app_ad_accept') if result else '' if result is None else get_text('app_ad_rejected')
    return get_text('info_ad_full', lang).replace(
        '{result}', result
    ).replace(
        '{number_rooms}', get_text(realty.number_rooms, lang) or "Не указано"
    ).replace(
        '{floors_in_house}', realty.floors_in_house or "Не указано"
    ).replace(
        '{floor}', realty.floor or "Не указано"
    ).replace(
        '{square}', realty.square or "Не указано"
    ).replace(
        '{city}', realty.city or "Не указано"
    ).replace(
        '{ad_type}', get_text(realty.ad_type, lang) or "Не указано"
    ).replace(
        '{type_property}', get_text(realty.type_property) or "Не указано"
    ).replace(
        '{object_type}', realty.object_type or "Не указано"
    ).replace(
        '{street}', realty.street or "Не указано"
    ).replace(
        '{district}', realty.district or "Не указано"
    ).replace(
        '{price}', realty.price or "Не указано"
    ).replace(
        '{description}', realty.description or "Описание отсутствует."
    ).replace(
        '{furniture}', get_text(realty.furniture, lang) or "Не указано"
    ).replace(
        '{animals}', get_text(realty.animals, lang) if realty.animals else "Не указано"
    ).replace(
        '{children}', get_text(realty.children, lang) if realty.children else "Не указано"
    ).replace(
        '{name}', realty.name or "Не указано"
    ).replace(
        '{contact}', realty.contact or "Не указано"
    ).replace(
        '{agency}',  realty.agency or "Не указано"
    ).replace(
        '{agency_name}', f'{get_text("agency_name", lang)} {realty.agency_name}' if realty.agency_name else ""
    )


def get_text_info_ad_incomplete(realty, lang) -> str:
    return get_text('info_ad_incomplete', lang).replace(
        '{square}', realty.square or "Не указано"
    ).replace(
        '{city}', realty.city or "Не указано"
    ).replace(
        '{ad_type}', get_text(realty.ad_type, lang) or "Не указано"
    ).replace(
        '{district}', realty.district or "Не указано"
    ).replace(
        '{price}', realty.price or "Не указано"
    ).replace(
        '{id}', str(realty.id)
    ).replace(
        '{agency}', get_text(realty.agency, lang) or "Не указано"
    ).replace(
        '{agency_name}', f'{get_text("agency_name", lang)} {realty.agency_name}' if realty.agency_name else ""
    )


async def search_realty(user, without_filters=None):
    query = Realty.select().where(Realty.consent_admin == True)

    if not without_filters:
        param_query = (
            Apartment_Parameters
            .select(Apartment_Parameters.title_parameter)
            .where(Apartment_Parameters.user == user)
        )
        params = [p.title_parameter for p in param_query]

        districts = []
        room_params = []

        for param in params:
            if param.startswith('rooms_'):
                room_params.append(param)
            else:
                districts.append(param)

        base_conditions = []

        if user.ad_type:
            base_conditions.append(Realty.ad_type == user.ad_type)

        if user.type_object:
            base_conditions.append(Realty.object_type == user.type_object)

        if user.type_property:
            base_conditions.append(Realty.type_property == user.type_property)

        if user.city:
            base_conditions.append(Realty.city == user.city)

        if user.price:
            base_conditions.append(Realty.price.cast('INTEGER') <= user.price)

        if user.total_area is not None and user.total_area > 0:
            base_conditions.append(Realty.square.cast('INTEGER') >= user.total_area)

        if base_conditions:
            query = query.where(*base_conditions)

        if districts:
            query = query.where(Realty.district.in_(districts))

        if room_params:
            query = query.where(Realty.number_rooms.in_(room_params))

    return query

def format_realty_card(realty) -> str:
    return (
        f"📍 {realty.city}, {realty.district}\n"
        f"🏠 {LEXICON_RU.get(realty.object_type, realty.object_type)} ({LEXICON_RU.get(realty.number_rooms, realty.number_rooms)})\n"
        f"💶 {realty.price} € \n"
        f"📏 {realty.square} м²\n"
        f"📝 {realty.description or LEXICON_RU.get('no_description', 'Нет описания')}"
    )



def get_share_link(realty, lang) -> str:
    message_text = get_text('get_text_info_for_share', lang).replace('{bot_name}', settings.BotSettings.BOT_NAME)

    encoded_share_message_text = quote(message_text)
    encoded_share_target_url = quote(f"https://t.me/{settings.BotSettings.BOT_NAME}?start={realty.id}", safe='')

    return (
        f"https://t.me/share/url?url={encoded_share_target_url}"
        f"&text={encoded_share_message_text}"
    )

def get_share_link_to_bot(lang) -> str:
    message_text = get_text('get_text_info_for_share_to_bot', lang).replace('{bot_name}', settings.BotSettings.BOT_NAME)

    encoded_share_message_text = quote(message_text)
    encoded_share_target_url = quote(f"https://t.me/{settings.BotSettings.BOT_NAME}", safe='')

    return (
        f"https://t.me/share/url?url={encoded_share_target_url}"
        f"&text={encoded_share_message_text}"
    )




