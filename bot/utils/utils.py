from urllib.parse import quote

from bot.databases.database import *
from bot.texts.texts import LEXICON_RU, LEXICON_TR, LEXICON_EN


def get_text(key: str, lang: str = 'ru') -> str:
    """ get text based on language settings """
    match lang:
        case 'tr':
            return LEXICON_TR[key]
        case 'ru':
            return LEXICON_RU[key]
        case _: # by default in English
            return LEXICON_EN[key]


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
        '{agency}',  realty.agency
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
        '{agency}', get_text(realty.agency, lang) or "None"
    ).replace(
        '{agency_name}', f'{get_text("agency_name", lang)} {realty.agency_name}' if realty.agency_name else ""
    )



async def search_realty(user, without_filters=None):
    if not without_filters:
        with db.atomic():
            params = [p.title_parameter for p in Apartment_Parameters.select().where(Apartment_Parameters.user == user)]

            districts = []
            room_params = []

            for param in params:
                if param in ['rooms_1-0', 'rooms_1-1', 'rooms_2-1', 'rooms_3-1', 'rooms_4-1', 'rooms_5-1_more']:
                    room_params.append(param)
                else:
                    districts.append(param)

        query = Realty.select().where(
            ((Realty.ad_type == user.ad_type) if user.ad_type else True) &
            ((Realty.object_type == user.type_object) if user.type_object else True) &
            ((Realty.type_property == user.type_property) if user.type_property else True) &
            ((Realty.city == user.city) if user.city else True) &
            ((Realty.price.cast('INTEGER') <= user.price) if user.price else True) &
            ((Realty.square.cast('INTEGER') >= user.total_area) if user.total_area is not None and user.total_area > 0 else True) &
            (Realty.consent_admin == True)
        )

        if districts:
            query = query.where(Realty.district.in_(districts))

        if room_params:
            query = query.where(Realty.number_rooms.in_(room_params))

        if user.ad_type == "sale" and user.type_property:
            query = query.where(Realty.type_property == user.type_property)
    else:
        query = Realty.select().where(Realty.consent_admin == True)

    return list(query)


def format_realty_card(realty) -> str:
    return (
        f"📍 {realty.city}, {realty.district}\n"
        f"🏠 {LEXICON_RU.get(realty.object_type, realty.object_type)} ({LEXICON_RU.get(realty.number_rooms, realty.number_rooms)})\n"
        f"💶 {realty.price} € \n"
        f"📏 {realty.square} м²\n"
        f"📝 {realty.description or LEXICON_RU.get('no_description', 'Нет описания')}"
    )



def get_share_link(realty, lang) -> str:
    message_text = get_text('get_text_info_for_share', lang).replace('{bot_name}', BOT_NAME)

    encoded_share_message_text = quote(message_text)
    encoded_share_target_url = quote(f"https://t.me/{BOT_NAME}?start={realty.id}", safe='')

    return (
        f"https://t.me/share/url?url={encoded_share_target_url}"
        f"&text={encoded_share_message_text}"
    )

def get_share_link_to_bot(lang) -> str:
    message_text = get_text('get_text_info_for_share_to_bot', lang).replace('{bot_name}', BOT_NAME)

    encoded_share_message_text = quote(message_text)
    encoded_share_target_url = quote(f"https://t.me/{BOT_NAME}", safe='')

    return (
        f"https://t.me/share/url?url={encoded_share_target_url}"
        f"&text={encoded_share_message_text}"
    )




