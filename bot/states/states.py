from aiogram.fsm.state import StatesGroup, State

class AddAd(StatesGroup):
    city = State()
    ad_type = State()
    type_property = State()
    object_type = State()
    number_rooms = State()
    price = State()
    district = State()
    street = State()
    square = State()
    floor = State()
    floor_in_house = State()
    description = State()
    photos_realty = State()
    name = State()
    contact = State()
    agency = State()
    agency_name = State()

    furniture = State()
    animals = State()
    children = State()

    realty_id = State()


class SearchSettings(StatesGroup):
    # Главное меню
    ad_type = State()  # Аренда или Покупка

    # Аренда
    rent_select_city = State()
    rent_select_apartment_params = State()
    rent_select_price = State()
    rent_select_area = State()
    rent_select_district = State()

    # Покупка
    buy_select_city = State()
    buy_select_property_type = State()  # Новостройки или Вторичное
    buy_select_property_type2 = State()  # Жилая недвижимость или Коммерческая недвижимость
    buy_select_apartment_params = State()
    buy_select_price = State()
    buy_select_area = State()
    buy_select_district = State()

    # Общие
    city = State()
    apartment_params = State()
    price = State()
    area = State()
    districts = State()


    # Финальный шаг
    confirm_settings = State()


class RunMailing(StatesGroup):
    sending = State()

