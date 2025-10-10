from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from bot.databases.database import Users, Realty
from bot.keyboards.main import *
from bot.keyboards.start_search import get_realty_card_kb
from bot.utils.utils import get_text, get_text_info_ad_full, get_text_info_ad_incomplete
from config import TUTORIAL

router = Router()


@router.callback_query(F.data == 'change_lang')
async def choice_lang(call: CallbackQuery):
    await call.message.edit_text(
        'Please select your language',
        reply_markup=get_choice_lang_kb()
    )


@router.callback_query(F.data.startswith('choice_lang_'))
async def choice_lang(call: CallbackQuery):
    lang = call.data.split('_', 3)[-2]
    ad_id = call.data.split('_', 3)[-1]

    user = Users.get_or_none(Users.user_id == call.from_user.id)
    if user:
        user.language = lang
        user.save()
    else:
        Users.create(
            user_id=call.from_user.id,
            username=call.from_user.username,
            language=lang
        )

    await call.message.delete()
    await call.message.answer(
        text=get_text(key='welcome_text', lang=lang),
        reply_markup=get_main_menu_reply_kb(lang)
    )

    await call.message.answer_photo(
        photo=FSInputFile(TUTORIAL),
        caption=get_text(key='watch_tutorial', lang=lang),
    )

    await call.message.answer(
        text=get_text(key='main_menu', lang=lang),
        reply_markup=get_main_menu_kb(lang)
    )

    if ad_id != 'None':
        realty = Realty.get(Realty.id == ad_id)
        text = get_text_info_ad_incomplete(realty, user.language)
        await call.message.answer(text, reply_markup=get_realty_card_kb(
            realty, user.user_id, page=1, lang=user.language
        ))


@router.callback_query(F.data == 'cancel_to_menu')
async def cancel_to_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()

    user = Users.get_or_none(Users.user_id == call.from_user.id)
    await call.message.delete()
    await call.message.answer(
        text=get_text(key='main_menu', lang=user.language),
        reply_markup=get_main_menu_kb(user.language)
    )


@router.callback_query(F.data == 'my_ads')
async def my_ads(call: CallbackQuery):
    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language
    ads = user.ads

    try:
        await call.message.edit_text(
            get_text('your_ads', lang),
            reply_markup=get_my_ads_kb(ads, lang)
        )
    except Exception as e:
        await call.message.delete()
        await call.message.answer(
            get_text('your_ads', lang),
            reply_markup=get_my_ads_kb(ads, lang)
        )


@router.callback_query(F.data.startswith('view_ad_'))
async def view_ad(call: CallbackQuery):
    relaty_id = call.data.split('_', 2)[-1]
    realty = Realty.get(Realty.id == relaty_id)

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    text = get_text_info_ad_full(realty, lang)

    photo_number = 0
    photos = realty.photos
    if len(photos) > photo_number:
        photo = photos[photo_number]
    elif len(photos):
        photo = photos[0]
        photo_number = 0
    else:
        photo = None

    await call.message.delete()
    if photo:
        await call.message.answer_photo(
            photo=FSInputFile(photo.photo_path),
            caption=text,
            reply_markup=get_my_ad_kb(realty.id, photo_number + 1, lang)
        )
    else:
        await call.message.answer(
            text,
            reply_markup=get_my_ad_kb(realty.id, photo_number + 1, lang)
        )


@router.callback_query(F.data.startswith('remove_ad_'))
async def remove_ad(call: CallbackQuery):
    relaty_id = call.data.split('_', 2)[-1]
    realty = Realty.get(Realty.id == relaty_id)
    realty.delete_instance()

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language
    await call.answer(get_text('remove_complete', lang))
    await my_ads(call)



