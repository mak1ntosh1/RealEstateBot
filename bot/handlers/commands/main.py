from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.databases.database import Users, City_Districts, Realty
from bot.decorators.handle_only_admin import handle_only_admin
from bot.keyboards.admin_panel import get_admin_panel_kb
from bot.keyboards.main import *
from bot.keyboards.start_search import get_realty_card_kb
from bot.utils.utils import get_text, get_text_info_ad_incomplete
from config import settings
from misc import bot

router = Router()


@router.message(Command("start"))
async def start_message(message: Message):
    user = Users.get_or_none(Users.user_id == message.from_user.id)

    params = message.text.split()
    ad_id = None
    if len(params) == 2:
        ad_id = params[-1]

    if user.language:
        await message.answer(
            text=get_text(key='welcome_text', lang=user.language),
            reply_markup=get_main_menu_reply_kb(user.language),
            disable_web_page_preview=True
        )

        await message.answer_photo(
            photo=settings.ImageIDs.MAIN_MENU,
            caption=get_text(key='main_menu', lang=user.language),
            reply_markup=get_main_menu_kb(user.language)
        )

        if len(params) == 2:
            realty = Realty.get(Realty.id == ad_id)
            text = get_text_info_ad_incomplete(realty, user.language)
            await message.answer(text, reply_markup=get_realty_card_kb(
                realty, user.user_id, page=1, lang=user.language
            ))

    else:
        await message.reply(
            'Please select your language',
            reply_markup=get_choice_lang_kb(ad_id)
        )




@router.message(Command("add_cities"))
@handle_only_admin
async def add_cities(message: Message):
    params = message.text.split('\n')[1:]
    if params:
        text = ''
        for city in params:
            city_name = city.split(':')[0]
            district = city.split(':')[-1]
            if City_Districts.get_or_none(City_Districts.district == district):
                text += f'♨ Район <code>{district}</code> уже есть в базе данных\n'
            else:
                City_Districts.create(
                    city_name=city_name.strip(),
                    district=district.strip(),
                )
                text += f'✅ Район <code>{district}</code> успешно добавлен\n'

        await message.answer(text)
    else:
        text = '''
♨ Неверное число параметров!
/add_cities
{Город}:{Район}

Например
/add_cities
Москва:Останкино
Москва:Лефортово
Москва:Измайлово
Санкт-Петербург:Невский
Санкт-Петербург:Адмиралтейский
Санкт-Петербург:Кировский
'''
        await message.answer(text)



@router.message(Command("id"))
async def get_id(message: Message):
    await message.answer(
        text=str(message.chat.id),
    )


@router.message(Command("admin"))
@handle_only_admin
async def admin_panel(message: Message, user_id = None):
    user_channel_status = await bot.get_chat_member(chat_id=settings.BotSettings.ADMIN_CHAT_ID, user_id=user_id if user_id else message.from_user.id)
    if user_channel_status.status != 'left':
        count_users = Users.select().count()
        active_adds = Realty.select().where(Realty.consent_admin == True).count()
        hidden_adds = Realty.select().where(Realty.consent_admin == False).count()
        moderation_adds = Realty.select().where(Realty.consent_admin.is_null()).count()

        text = f'''
🔑 <b><u>Административный Доступ</u></b> ✨

<b>Статистика:</b>
▪️ Всего пользователей: <b>{count_users}</b> 👥

<b>📝 Объявления:</b>
✅ Активные: <i>{active_adds}</i>
🥷 Скрытые: <i>{hidden_adds}</i>
🔘 На модерации: <i>{moderation_adds}</i>
'''

        await message.answer_photo(
            photo=settings.ImageIDs.ADMIN_PANEL,
            caption=text,
            reply_markup=get_admin_panel_kb()
        )


@router.message(Command("rm_me"))
async def remove_me(message: Message):
    user_channel_status = await bot.get_chat_member(chat_id=settings.BotSettings.ADMIN_CHAT_ID, user_id=message.from_user.id)
    if user_channel_status.status != 'left':
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if user:
            user.delete_instance()
            text = '✅ Вы успешно удалены из базы данных, обязательно пропишите /start чтобы снова зарегистрироваться!'
        else:
            text = '⚠️ Вас уже нет в базе данных, пропишите /start чтобы снова зарегистрироваться!'

        await message.answer(text)


@router.message(F.photo | F.video | F.document | F.animation | F.audio | F.voice | F.sticker)
@handle_only_admin
async def get_file_id_for_any_media(message: Message):
    """
    Получает file_id для любого отправленного медиафайла (фото, видео, документ, аудио, анимация, голосовое сообщение, стикер).
    Отвечает на каждое медиа в группе как на отдельное сообщение.
    """
    file_id = None

    if message.photo:
        file_id = message.photo[-1].file_id # Берем последнее (самое большое) фото
    elif message.video:
        file_id = message.video.file_id
    elif message.document:
        file_id = message.document.file_id
    elif message.animation:
        file_id = message.animation.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.voice:
        file_id = message.voice.file_id
    elif message.sticker:
        file_id = message.sticker.file_id

    if file_id:
        response_text = f"File ID: <code>{file_id}</code>"
        await message.reply(response_text)
