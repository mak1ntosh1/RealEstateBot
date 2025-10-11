import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto

from bot.databases.database import Users, City_Districts, Realty, PhotosRealty
from bot.filters.filters import CustomFilter

from bot.keyboards.add_ad import *
from bot.utils.utils import get_text_info_ad_full, get_text_info_ad_incomplete

from bot.states.states import *
from config import DIR_PHOTO_ESTATES
from misc import bot

router = Router()


@router.callback_query(CustomFilter(AddAd.ad_type, 'back_to_type_property_selected', F.data.in_(["rent", "sale"])))
async def ad_type_selected(call: CallbackQuery, state: FSMContext):
    """
    💾 Сохраняет - Тип (Аренда или продажа)
    📩 Запрашивает - Тип недвижимости
    """


    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    await state.update_data(ad_type=call.data)
    await call.message.edit_caption(
        caption=get_text("choose_property_type", lang),
        reply_markup=get_property_type_kb(lang)  # Возвращает к выбору аренда / продажа
    )
    await state.set_state(AddAd.type_property)


@router.callback_query(CustomFilter(AddAd.type_property, 'back_to_object_type_selected', F.data.in_(["residential_property", "commercial_property", "land"])))
async def type_property_selected(call: CallbackQuery, state: FSMContext):
    """
   💾 Сохраняет — Тип недвижимости (Жилая / Коммерческая / Земля)
   📩 Запрашивает — Тип объекта или Меблировку (в зависимости от выбора)
   """

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    await state.update_data(type_property=call.data)

    if call.data in ["residential_property", "commercial_property"]:
        await call.message.edit_caption(
            caption=get_text("choose_residential_type", lang),
            reply_markup=get_object_type_kb(lang)  # Возвращает к выбору типа недвижимости
        )
        await state.set_state(AddAd.object_type)
    else:
        await state.set_state(AddAd.furniture)
        await call.message.edit_caption(
            caption=get_text("furniture_question", lang),
            reply_markup=get_furniture_kb(lang)  # Возвращает к выбору типа недвижимости
        )


@router.callback_query(CustomFilter(AddAd.object_type, 'back_to_furniture_selected', F.data.in_(["new_building", "secondary"])))
async def object_type_selected(call: CallbackQuery, state: FSMContext):
    """
    💾 Сохраняет — Тип жилого объекта (🏗 Новостройка / 🏘 Вторичка)
    📩 Запрашивает — Наличие мебели
    """

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    if call.data != 'back_to_furniture_selected':
        await state.update_data(object_type=call.data)
    await state.set_state(AddAd.furniture)
    await call.message.edit_caption(
        caption=get_text("furniture_question", lang),
        reply_markup=get_furniture_kb(lang)  # Возвращает к выбору типа жилого объекта
    )


@router.callback_query(CustomFilter(AddAd.furniture, 'back_to_animals_selected', F.data.in_(["yes_furniture", "no_furniture"])))
async def furniture_selected(call: CallbackQuery, state: FSMContext):
    """
    💾 Сохраняет — Наличие мебели
    📩 Запрашивает — Возможность с животными или количество комнат
    """

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    if call.data != 'back_to_animals_selected':
        await state.update_data(furniture=call.data)

    data = await state.get_data()
    if data['ad_type'] == 'sale':
        await state.set_state(AddAd.number_rooms)
        await call.message.edit_caption(
            caption=get_text("choose_rooms", lang),
            reply_markup=get_rooms_kb(lang, 'back_to_furniture_selected')  # Наличие мебели
        )
    else:
        await state.set_state(AddAd.animals)
        await call.message.edit_caption(
            caption=get_text("animals_question", lang),
            reply_markup=get_animals_kb(lang)  # Возвращает к Наличие мебели
        )


@router.callback_query(CustomFilter(AddAd.animals, 'back_to_children_selected', F.data.in_(["animals_yes", "animals_no", "animals_discuss"])))
async def animals_selected(call: CallbackQuery, state: FSMContext):
    """
    💾 Сохраняет — Отношение к животным
    📩 Запрашивает — Отношение к детям
    """

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    if call.data != 'back_to_children_selected':
        await state.update_data(animals=call.data)
    await state.set_state(AddAd.children)
    await call.message.edit_caption(
        caption=get_text("children_question", lang),
        reply_markup=get_children_kb(lang)  # Возвращает к выбору отношения к животным
    )


@router.callback_query(CustomFilter(AddAd.children, 'back_to_rooms_selected', F.data.in_(["children_yes", "children_no", "children_discuss"])))
async def children_selected(call: CallbackQuery, state: FSMContext):
    """
    💾 Сохраняет — Отношение к детям
    📩 Запрашивает — Количество комнат
    """

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    if call.data != 'back_to_rooms_selected':
        await state.update_data(children=call.data)
    await state.set_state(AddAd.number_rooms)
    await call.message.edit_caption(
        caption=get_text("choose_rooms", lang),
        reply_markup=get_rooms_kb(lang, 'back_to_children_selected')  # Возвращает к выбору отношения к детям
    )


@router.callback_query(CustomFilter(AddAd.number_rooms, 'back_to_price_entered', F.data.startswith("room_")))
async def rooms_selected(call: CallbackQuery, state: FSMContext):
    """
    💾 Сохраняет — Количество комнат
    📩 Запрашивает — Стоимость объекта
    """

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    data = await state.get_data()

    rooms = call.data.split('_', 1)[-1]
    if call.data != 'back_to_price_entered':
        await state.update_data(number_rooms=rooms)
    await state.set_state(AddAd.price)
    text = get_text("select_rent_price", lang) if data['ad_type'] == 'rent' else get_text("select_buy_price", lang)
    await call.message.edit_caption(
        caption=text,
        reply_markup=get_back_from_message_kb(lang, 'back_to_rooms_selected')  # Возвращает к выбору количества комнат
    )


@router.message(AddAd.price)
async def price_entered(msg: Message, state: FSMContext, message_text=None, user_id=None):
    """
    💾 Сохраняет — Стоимость объекта
    🧹 Удаляет сообщение с ценой
    📩 Запрашивает — Район
    """

    user_id = user_id if user_id else msg.from_user.id
    user = Users.get(Users.user_id == user_id)
    lang = user.language

    data = await state.get_data()
    city = data["city"]


    districts = City_Districts.select().where(City_Districts.city_name == city)

    await state.update_data(price=message_text or msg.text)
    await state.set_state(AddAd.district)

    message_id = msg.message_id

    if message_text:
        await msg.delete()
    else:
        try:
            await bot.delete_message(msg.chat.id, message_id)
            await bot.delete_message(msg.chat.id, message_id - 1)
        except Exception as ex:
            print(ex)
    await msg.answer_photo(
        photo=FSInputFile(ADD_AD),
        caption=get_text("choose_district", lang),
        reply_markup=get_districts_kb(lang, districts)  # Возвращает к вводу стоимости
    )


@router.callback_query(F.data == "back_to_district_selected")
async def price_entered_callback(call: CallbackQuery, state: FSMContext):
    """🔁 Возвращает — К шагу ввода цены"""

    data = await state.get_data()
    price = data["price"]
    await price_entered(call.message, state, price, call.from_user.id)


@router.callback_query(CustomFilter(AddAd.district, 'back_to_street_entered', F.data.startswith("district_")))
async def district_selected(call: CallbackQuery, state: FSMContext):
    """
    💾 Сохраняет — Район
    📩 Запрашивает — Улицу или предлагает пропустить
    """

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    district = call.data.split("_", 2)[-1]
    if call.data != 'back_to_street_entered':
        await state.update_data(district=district)
    await state.set_state(AddAd.street)
    await call.message.edit_caption(
        caption=get_text("enter_street_or_skip", lang),
        reply_markup=get_skip_street_kb(lang)  # Возвращает к выбору района
    )


@router.message(AddAd.street)
async def street_entered(msg: Message, state: FSMContext):
    """
    💾 Сохраняет — Улицу
    🧹 Удаляет сообщение с улицей
    📩 Запрашивает — Площадь
    """

    user = Users.get(Users.user_id == msg.from_user.id)
    lang = user.language

    await state.update_data(street=msg.text)
    await state.set_state(AddAd.square)

    try:
        await bot.delete_message(msg.chat.id, msg.message_id)
        await bot.delete_message(msg.chat.id, msg.message_id - 1)
    except Exception as ex:
        print(ex)

    await msg.answer(
        caption=get_text("enter_square", lang),
        reply_markup=get_back_from_message_kb(lang, 'back_to_street_entered')  # Возвращает к вводу улицы
    )


@router.callback_query(CustomFilter(AddAd.street, 'None', F.data == "skip_street"))
async def skip_street(call: CallbackQuery, state: FSMContext):
    """
    🚫 Пропускает — Ввод улицы
    📩 Запрашивает — Площадь
    """

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    await state.update_data(street=None)
    await state.set_state(AddAd.square)
    await call.message.edit_caption(
        caption=get_text("enter_square", lang),
        reply_markup=get_back_from_message_kb(lang, 'back_to_street_entered')  # Возвращает к вводу улицы
    )


@router.message(AddAd.square)
async def square_entered(msg: Message, state: FSMContext, message_text=None, user_id=None):
    """
    💾 Сохраняет — Площадь
    🧹 Удаляет сообщение с площадью
    📩 Запрашивает — Этаж
    """

    user_id = user_id if user_id else msg.from_user.id
    user = Users.get(Users.user_id == user_id)
    lang = user.language

    await state.update_data(square=msg.text)
    await state.set_state(AddAd.floor)


    if message_text:
        await msg.delete()
    else:
        try:
            await bot.delete_message(msg.chat.id, msg.message_id)
            await bot.delete_message(msg.chat.id, msg.message_id - 1)
        except Exception as ex:
            print(ex)

    await msg.answer_photo(
        photo=FSInputFile(ADD_AD),
        caption=get_text("enter_floor", lang),
        reply_markup=get_back_from_message_kb(lang, 'back_to_street_entered')  # Возвращает к вводу улицы
    )


@router.callback_query(F.data == "back_to_floor_entered")
async def floor_entered_callback(call: CallbackQuery, state: FSMContext):
    """🔁 Возвращает — К шагу ввода этажа"""

    data = await state.get_data()
    floor = data["floor"]
    await square_entered(call.message, state, floor, call.from_user.id)



@router.message(AddAd.floor)
async def floor_entered(msg: Message, state: FSMContext, message_text=None, user_id=None):
    """
    💾 Сохраняет — Этаж
    🧹 Удаляет сообщение с этажом
    📩 Запрашивает — Количество этажей в доме
    """

    user_id = user_id if user_id else msg.from_user.id
    user = Users.get(Users.user_id == user_id)
    lang = user.language

    await state.update_data(floor=msg.text)
    await state.set_state(AddAd.floor_in_house)

    if message_text:
        await msg.delete()
    else:
        try:
            await bot.delete_message(msg.chat.id, msg.message_id)
            await bot.delete_message(msg.chat.id, msg.message_id - 1)
        except Exception as ex:
            print(ex)

    await msg.answer_photo(
        photo=FSInputFile(ADD_AD),
        caption=get_text("enter_floor_total", lang),
        reply_markup=get_back_from_message_kb(lang, 'back_to_floor_entered')  # Возвращает к вводу этажа
    )


@router.callback_query(F.data == "back_to_floor_in_house_entered")
async def floor_in_house_entered_callback(call: CallbackQuery, state: FSMContext):
    """🔁 Возвращает — К шагу ввода этажей в доме"""

    data = await state.get_data()
    floors = data["floor_in_house"]
    await floor_entered(call.message, state, floors, call.from_user.id)


@router.message(AddAd.floor_in_house)
async def floor_in_house_entered(msg: Message, state: FSMContext, message_text=None, user_id=None):
    """
    💾 Сохраняет — Этажность дома
    🧹 Удаляет сообщение с этажностью
    📩 Запрашивает — Полное описание
    """

    user_id = user_id if user_id else msg.from_user.id
    user = Users.get(Users.user_id == user_id)
    lang = user.language

    await state.update_data(floor_in_house=msg.text)
    await state.set_state(AddAd.description)

    if message_text:
        await msg.delete()
    else:
        try:
            await bot.delete_message(msg.chat.id, msg.message_id)
            await bot.delete_message(msg.chat.id, msg.message_id - 1)
        except Exception as ex:
            print(ex)

    await msg.answer_photo(
        photo=FSInputFile(ADD_AD),
        caption=get_text("enter_description", lang),
        reply_markup=get_skip_description_kb(lang)
    )


@router.callback_query(F.data == "back_to_description_entered")
async def description_entered_callback(call: CallbackQuery, state: FSMContext):
    """🔁 Возвращает — К шагу ввода описания"""

    data = await state.get_data()
    description = data["description"]
    await floor_in_house_entered(call.message, state, description, call.from_user.id)


@router.message(AddAd.description)
async def description_entered(msg: Message, state: FSMContext):
    """
    💾 Сохраняет — Описание
    📩 Запрашивает — Фото недвижимости
    """

    user = Users.get(Users.user_id == msg.from_user.id)
    lang = user.language

    data = await state.get_data()

    realty = Realty.create(
        user=user,  # или user.id, если требуется ID
        city=data.get("city"),
        ad_type=data.get("ad_type"),
        type_property=data.get("type_property"),
        object_type=data.get("object_type"),
        number_rooms=data.get("number_rooms"),
        price=data.get("price"),
        district=data.get("district"),
        street=data.get("street"),
        square=data.get("square"),
        floor=data.get("floor"),
        floors_in_house=data.get("floor_in_house"),
        description=msg.text,
        furniture=data.get("furniture"),
        animals=data.get("animals"),
        children=data.get("children")
    )

    await state.update_data(description=msg.text)
    await state.update_data(realty_id=realty.id)
    await state.set_state(AddAd.photos_realty)

    try:
        await bot.delete_message(msg.chat.id, msg.message_id)
        await bot.delete_message(msg.chat.id, msg.message_id - 1)
    except Exception as ex:
        print(ex)

    await msg.answer_photo(
        photo=FSInputFile(ADD_AD),
        caption=get_text("attach_photos", lang),
        reply_markup=get_back_to_description_entered_kb(lang)  # Возвращает к вводу описания
    )


@router.callback_query(CustomFilter(AddAd.description, 'None', F.data == "skip_description"))
async def skip_description(call: CallbackQuery, state: FSMContext):
    """
    🚫 Пропускает — Ввод описания
    📩 Запрашивает — Фото недвижимости
    """

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    data = await state.get_data()

    realty = Realty.create(
        user=user,
        city=data.get("city"),
        ad_type=data.get("ad_type"),
        type_property=data.get("type_property"),
        object_type=data.get("object_type"),
        number_rooms=data.get("number_rooms"),
        price=data.get("price"),
        district=data.get("district"),
        street=data.get("street"),
        square=data.get("square"),
        floor=data.get("floor"),
        floor_in_house=data.get("floor_in_house"),
        description=None,
        furniture=data.get("furniture"),
        animals=data.get("animals"),
        children=data.get("children")
    )

    await state.update_data(description=None)
    await state.update_data(realty_id=realty.id)
    await state.set_state(AddAd.photos_realty)
    await call.message.edit_caption(
        caption=get_text("attach_photos", lang),
        reply_markup=get_back_to_description_entered_kb(lang)  # Кнопка Stop для перехода к шагу после фотографий
    )


@router.message(AddAd.photos_realty, F.photo)
async def photos_received(message: Message, album: list[Message] = None, state: FSMContext = None):
    """💾 Сохраняет — Фото недвижимости"""

    data = await state.get_data()
    realty = Realty.get_or_none(Realty.id == data["realty_id"])
    if realty:
        photos = album if album else [message]
        saved_files = []

        for msg in photos:
            photo = msg.photo[-1]  # Самое качественное фото
            unique_filename = f"{uuid.uuid4()}.jpg"
            file_path = os.path.join(DIR_PHOTO_ESTATES, unique_filename)

            await bot.download(photo.file_id, destination=file_path)

            PhotosRealty.create(
                realty=realty,
                photo_path=file_path
            )

            saved_files.append(unique_filename)

        await message.reply(f"✅ Фото сохранено!")


@router.callback_query(CustomFilter(AddAd.photos_realty, 'None', F.data == "go_to_name_entered"))
async def skip_description(call: CallbackQuery, state: FSMContext):
    """📩 Запрашивает — Имя создателя объявления"""

    user = Users.get(Users.user_id == call.from_user.id)
    lang = user.language

    await state.set_state(AddAd.name)

    await call.message.delete()
    await call.message.answer_photo(
        photo=FSInputFile(ADD_AD),
        caption=get_text("enter_name", lang)
    )


@router.message(AddAd.name)
async def name_entered(msg: Message, state: FSMContext):
    """
    💾 Сохраняет — Имя создателя объявления
    📩 Запрашивает — Контактный номер
    """
    user = Users.get(Users.user_id == msg.from_user.id)
    lang = user.language

    await state.update_data(name=msg.text)
    await state.set_state(AddAd.contact)

    try:
        await bot.delete_message(msg.chat.id, msg.message_id)
        await bot.delete_message(msg.chat.id, msg.message_id - 1)
    except Exception as ex:
        print(ex)

    await msg.answer_photo(
        photo=FSInputFile(ADD_AD),
        caption=get_text("enter_phone", lang)
    )


@router.message(AddAd.contact)
async def contact_entered(msg: Message, state: FSMContext):
    user = Users.get(Users.user_id == msg.from_user.id)
    lang = user.language

    await state.update_data(contact=msg.text)
    await state.set_state(AddAd.agency)

    try:
        await bot.delete_message(msg.chat.id, msg.message_id)
        await bot.delete_message(msg.chat.id, msg.message_id - 1)
    except Exception as ex:
        print(ex)

    await msg.answer_photo(
        photo=FSInputFile(ADD_AD),
        caption=get_text("enter_agency", lang),
        reply_markup=get_agency_kb(lang)
    )


@router.callback_query(CustomFilter(AddAd.agency, 'None', F.data.in_(['owner', 'realtor'])))
async def agency_entered(call: CallbackQuery, state: FSMContext):
    await state.update_data(agency=call.data)

    if call.data == 'realtor':
        await state.set_state(AddAd.agency_name)
        await call.message.delete()
        await call.message.answer(get_text('enter_agency_name'))
    else:
        try:
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.delete_message(call.message.chat.id, call.message.message_id - 1)
        except Exception as ex:
            print(ex)

        await finish_add_ad(call.message, state, call.from_user.id)


@router.message(AddAd.agency_name)
async def agency_name_entered(msg: Message, state: FSMContext):
    await state.update_data(agency_name=msg.text)

    await finish_add_ad(msg, state, msg.from_user.id)


# Сохранение объявления и отправка на рассмотрение в админ чат
async def finish_add_ad(message: Message, state: FSMContext, user_id):
    user = Users.get(Users.user_id == user_id)
    lang = user.language

    data = await state.get_data()
    realty_id = data["realty_id"]

    realty = Realty.get_or_none(Realty.id == realty_id)
    realty.name = data.get("name")
    realty.contact = data.get("contact")
    realty.agency = data.get("agency")
    realty.agency_name = data.get("agency_name")
    realty.save()

    await message.answer(get_text("success_saved", lang))
    await state.clear()

    text = get_text_info_ad_incomplete(realty, lang)

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
        await bot.send_photo(
            photo=FSInputFile(photo.photo_path),
            chat_id=ADMIN_CHAT_ID,
            caption=text,
            reply_markup=get_consent_admin_kb(realty.id, realty.consent_admin, photo_number + 1)
        )
    else:
        await bot.send_message(
            ADMIN_CHAT_ID, text,
            reply_markup=get_consent_admin_kb(realty.id, realty.consent_admin, photo_number + 1)
        )


# Подробное описание объявления
@router.callback_query(F.data.startswith("in_detail_"))
async def in_detail(call: CallbackQuery):
    realty_id = call.data.split('_', 3)[-2]
    photo_number = int(call.data.split('_', 3)[-1])
    realty = Realty.get(Realty.id == realty_id)
    user = Users.get(Users.id == realty.user_id)
    lang = user.language


    text = get_text_info_ad_full(realty, lang)

    await call.message.edit_caption(
        caption=text,
        reply_markup=get_consent_admin2_kb(
            realty.id,
            realty.consent_admin,
            photo_number
        )
    )

# Скрыть подробности объявления
@router.callback_query(F.data.startswith("hide_details_"))
async def hide_details(call: CallbackQuery):
    realty_id = call.data.split('_', 3)[-2]
    photo_number = int(call.data.split('_', 3)[-1])
    realty = Realty.get(Realty.id == realty_id)
    user = Users.get(Users.id == realty.user_id)
    lang = user.language

    text = get_text_info_ad_incomplete(realty, lang)
    await call.message.edit_caption(
        caption=text,
        reply_markup=get_consent_admin_kb(
            realty.id,
            realty.consent_admin,
            photo_number
        )
    )


# Одобрение объявления
@router.callback_query(F.data.startswith("accept_realty_"))
async def accept_realty(call: CallbackQuery, state: FSMContext):
    realty_id = call.data.split('_', 3)[-2]
    photo_number = int(call.data.split('_', 3)[-1])
    realty = Realty.get(Realty.id == realty_id)

    realty.consent_admin = True
    realty.save()

    user = Users.get(Users.id == realty.user_id)
    lang = user.language

    text = get_text_info_ad_full(realty, lang, result=True)

    await bot.send_message(user.user_id, text)

    await call.message.edit_reply_markup(
        reply_markup=get_consent_admin2_kb(
            realty.id,
            realty.consent_admin,
            photo_number
        )
    )


# Отклонение объявления
@router.callback_query(F.data.startswith("decline_realty_"))
async def decline_realty(call: CallbackQuery, state: FSMContext):
    realty_id = call.data.split('_', 3)[-2]
    photo_number = int(call.data.split('_', 3)[-1])
    realty = Realty.get(Realty.id == realty_id)

    realty.consent_admin = False
    realty.save()

    user = Users.get(Users.id == realty.user_id)
    lang = user.language

    text = get_text_info_ad_full(realty, lang, result=False)

    await bot.send_message(user.user_id, text)

    await call.message.edit_reply_markup(
        reply_markup=get_consent_admin2_kb(
            realty.id,
            realty.consent_admin,
            photo_number
        )
    )


# Переключить фото объявления
@router.callback_query(F.data.startswith("next_photo_"))
async def next_photo(call: CallbackQuery, state: FSMContext):
    realty_id = call.data.split('_', 3)[-2]
    photo_number = int(call.data.split('_', 3)[-1])
    realty = Realty.get(Realty.id == realty_id)

    user = Users.get(Users.id == realty.user_id)
    lang = user.language

    text = get_text_info_ad_incomplete(realty, lang)

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
            reply_markup=get_consent_admin_kb(realty.id, realty.consent_admin, photo_number + 1)
        )
    else:
        await call.answer('Фотографий нет')


# Переключить фото объявления
@router.callback_query(F.data.startswith("next_photo2_"))
async def next_photo2(call: CallbackQuery, state: FSMContext):
    realty_id = call.data.split('_', 3)[-2]
    photo_number = int(call.data.split('_', 3)[-1])
    realty = Realty.get(Realty.id == realty_id)

    user = Users.get(Users.id == realty.user_id)
    lang = user.language

    text = get_text_info_ad_full(realty, lang)

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
            reply_markup=get_consent_admin_kb(realty.id, realty.consent_admin, photo_number + 1)
        )
    else:
        await call.answer('Фотографий нет')


