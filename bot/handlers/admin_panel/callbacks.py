from contextlib import suppress

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto

from bot.databases.database import Realty
from bot.handlers.commands.main import admin_panel
from bot.keyboards.admin_panel import *
from bot.utils.utils import get_text_info_ad_incomplete, get_text_info_ad_full
from bot.states.states import *

router = Router()

@router.callback_query(F.data.startswith('admin_mailing'))
async def mailing(call: CallbackQuery, state: FSMContext):
    await state.set_state(RunMailing.sending)

    await call.message.edit_caption(
        caption='Пришлите пост, который требуется разослать:',
        reply_markup=get_cancel_mailing_kb()
    )


@router.callback_query(F.data.startswith('back_to_admin_panel'))
async def cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()

    with suppress(Exception):
        await call.message.delete()
    await admin_panel(call.message, call.from_user.id)


@router.callback_query(F.data.startswith('all_ads_'))
async def all_ads(call: CallbackQuery):
    page = int(call.data.split('_', 2)[-1])

    active_adds = Realty.select().where(Realty.consent_admin == True).count()
    hidden_adds = Realty.select().where(Realty.consent_admin == False).count()
    moderation_adds = Realty.select().where(Realty.consent_admin.is_null()).count()

    text = f'''
📊 <b>Объявления: Обзор и Действия</b>

<b>Текущая статистика:</b>
✅ Активные: <i>{active_adds}</i>
🥷 Скрытые: <i>{hidden_adds}</i>
🔘 На модерации: <i>{moderation_adds}</i>

<b>Доступные действия:</b>    
'''

    keyboard = await get_list_all_ads_kb(page, call)

    try:
        await call.message.edit_caption(
            caption=text,
            reply_markup=keyboard
        )
    except Exception as e:
        await call.message.delete()
        await call.message.answer_photo(
            photo=settings.ImageIDs.ADMIN_PANEL,
            caption=text,
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith('admin_view_ad_'))
async def admin_view_ad(call: CallbackQuery):
    ad_id = call.data.split('_', 4)[-2]
    page = call.data.split('_', 4)[-1]

    realty = Realty.get(Realty.id == ad_id)
    status = '✅ Опубликовано' if realty.consent_admin else '🔘 На модерации' if realty.consent_admin is None else '🥷 Скрыто'

    text = get_text_info_ad_incomplete(realty, 'ru') + f'\n\n<pre>{status}</pre>'

    photo_number = 0
    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None

    if photo:
        try:
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=FSInputFile(photo),
                    caption=text
                ),
                reply_markup=get_manage_realty2_kb(realty.id, realty.consent_admin, photo_number, page)
            )
        except Exception as e:
            with suppress(Exception):
                await call.message.delete()
            await call.message.answer_photo(
                photo=FSInputFile(photo),
                caption=text,
                reply_markup=get_manage_realty2_kb(realty.id, realty.consent_admin, photo_number, page)
            )
    else:
        await call.answer('Фотографий нет')
        await call.message.edit_caption(
            caption=text,
            reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number, page)
        )


@router.callback_query(F.data.startswith('admin_in_detail_'))
async def admin_in_detail(call: CallbackQuery):
    ad_id = call.data.split('_', 5)[-3]
    photo_number = int(call.data.split('_', 5)[-2])
    page = call.data.split('_', 5)[-1]

    realty = Realty.get(Realty.id == ad_id)
    status = '✅ Опубликовано' if realty.consent_admin else '🔘 На модерации' if realty.consent_admin is None else '🥷 Скрыто'

    text = get_text_info_ad_full(realty, 'ru') + f'\n\n<pre>{status}</pre>'

    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None



    if photo:
        try:
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=FSInputFile(photo),
                    caption=text
                ),
                reply_markup=get_manage_realty2_kb(realty.id, realty.consent_admin, photo_number, page)
            )
        except Exception as e:
            await call.message.delete()
            await call.message.answer_photo(
                photo=FSInputFile(photo),
                caption=text,
                reply_markup=get_manage_realty2_kb(realty.id, realty.consent_admin, photo_number, page)
            )
    else:
        await call.answer('Фотографий нет')
        await call.message.edit_caption(
            caption=text,
            reply_markup=get_manage_realty2_kb(realty.id, realty.consent_admin, photo_number, page)
        )


@router.callback_query(F.data.startswith('admin_hide_details_'))
async def admin_hide_details(call: CallbackQuery):
    ad_id = call.data.split('_', 5)[-3]
    photo_number = int(call.data.split('_', 5)[-2])
    page = call.data.split('_', 5)[-1]

    realty = Realty.get(Realty.id == ad_id)
    status = '✅ Опубликовано' if realty.consent_admin else '🔘 На модерации' if realty.consent_admin is None else '🥷 Скрыто'

    text = get_text_info_ad_incomplete(realty, 'ru') + f'\n\n<pre>{status}</pre>'

    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None

    if photo:
        try:
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=FSInputFile(photo),
                    caption=text
                ),
                reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number, page)
            )
        except Exception as e:
            await call.message.delete()
            await call.message.answer_photo(
                photo=FSInputFile(photo),
                caption=text,
                reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number, page)
            )
    else:
        await call.answer('Фотографий нет')
        await call.message.edit_caption(
            caption=text,
            reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number, page)
        )


@router.callback_query(F.data.startswith('admin_next_photo_'))
async def admin_next_photo(call: CallbackQuery):
    realty_id = call.data.split('_', 5)[-3]
    photo_number = int(call.data.split('_', 5)[-2])
    page = int(call.data.split('_', 5)[-1])
    realty = Realty.get(Realty.id == realty_id)

    status = '✅ Опубликовано' if realty.consent_admin else '🔘 На модерации' if realty.consent_admin is None else '🥷 Скрыто'

    text = get_text_info_ad_incomplete(realty, 'ru') + f'\n\n<pre>{status}</pre>'

    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None

    if photo:
        await call.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(photo.photo_path), caption=text),
            reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number + 1, page)
        )
    else:
        await call.message.edit_caption(
            caption=text,
            reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number + 1, page)
        )
        await call.answer('Фотографий нет')


@router.callback_query(F.data.startswith('admin_next_photo2_'))
async def admin_next_photo(call: CallbackQuery):
    realty_id = call.data.split('_', 5)[-3]
    photo_number = int(call.data.split('_', 5)[-2])
    page = int(call.data.split('_', 5)[-1])
    realty = Realty.get(Realty.id == realty_id)

    status = '✅ Опубликовано' if realty.consent_admin else '🔘 На модерации' if realty.consent_admin is None else '🥷 Скрыто'

    text = get_text_info_ad_full(realty, 'ru') + f'\n\n<pre>{status}</pre>'

    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None

    if photo:
        await call.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(photo.photo_path), caption=text),
            reply_markup=get_manage_realty2_kb(realty.id, realty.consent_admin, photo_number + 1, page)
        )
    else:
        await call.message.edit_caption(
            caption=text,
            reply_markup=get_manage_realty2_kb(realty.id, realty.consent_admin, photo_number + 1, page)
        )
        await call.answer('Фотографий нет')


@router.callback_query(F.data.startswith('admin_accept_realty_'))
async def admin_accept_realty(call: CallbackQuery):
    realty_id = call.data.split('_', 5)[-3]
    photo_number = int(call.data.split('_', 5)[-2])
    page = int(call.data.split('_', 5)[-1])
    realty = Realty.get(Realty.id == realty_id)

    realty.consent_admin = True
    realty.save()

    text = get_text_info_ad_incomplete(realty, 'ru') + f'\n\n<pre>✅ Опубликовано</pre>'

    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None

    if photo:
        await call.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(photo.photo_path), caption=text),
            reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number + 1, page)
        )
    else:
        await call.message.edit_caption(
            caption=text,
            reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number + 1, page)
        )
        await call.answer('Фотографий нет')


@router.callback_query(F.data.startswith('admin_decline_realty_'))
async def admin_accept_realty(call: CallbackQuery):
    realty_id = call.data.split('_', 5)[-3]
    photo_number = int(call.data.split('_', 5)[-2])
    page = int(call.data.split('_', 5)[-1])
    realty = Realty.get(Realty.id == realty_id)

    realty.consent_admin = False
    realty.save()

    text = get_text_info_ad_incomplete(realty, 'ru') + f'\n\n<pre>🥷 Скрыто</pre>'

    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None

    if photo:
        await call.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(photo.photo_path), caption=text),
            reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number + 1, page)
        )
    else:
        await call.message.edit_caption(
            caption=text,
            reply_markup=get_manage_realty_kb(realty.id, realty.consent_admin, photo_number + 1, page)
        )
        await call.answer('Фотографий нет')





