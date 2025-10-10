import itertools

from bot.databases.database import City_Districts, Realty, Users


def add_all_options(user_id_db: int, options: dict):
    Realty.create(
        user=user_id_db,  # или user.id, если требуется ID
        city=options.get("city"),
        ad_type=options.get("ad_type"),
        type_property=options.get("type_property"),
        object_type=options.get("object_type"),
        number_rooms=options.get("number_rooms"),
        price=options.get("price"),
        district=options.get("district"),
        street=options.get("street"),
        square=options.get("square"),
        floor=options.get("floor"),
        floors_in_house=options.get("floors_in_house"),
        description=options.get("description"),
        furniture=options.get("furniture"),
        animals=options.get("animals"),
        children=options.get("children"),
        consent_admin=True
    )




if __name__ == '__main__':
    cities = [city_district.city_name for city_district in City_Districts.select(City_Districts.city_name).distinct()]
    user = Users.get(Users.user_id == 8062956903)

    options = {
        'number_rooms': ["rooms_1_0", "rooms_1_1", "rooms_2_1", "rooms_3_1", "rooms_4_1", "rooms_5_1_more"],
        'floors_in_house': ['10'],
        'floor': ['5'],
        'square': ['80'],
        'city': cities[:1],
        'ad_type': ['rent', 'sale'],
        'type_property': ['land', 'commercial_property', 'residential_property'],
        'object_type': ['villa', 'duplex', 'flat'],
        'street': [
            "İstiklal Caddesi No: 78, D: 4, Cihangir Mahallesi, Beyoğlu / İstanbul, 34433"
        ],
        'price': [180000],
        'description': ['test_description'],
        'furniture': ['furnished_yes', 'furnished_no'],
        'animals': ['animals_yes', 'animals_no', 'animals_maybe'],
        'children': ['children_yes', 'children_no', 'children_maybe'],
    }

    # 1. Получаем список значений из словаря 'options'
    # Важно! Порядок важен, если вы хотите сопоставить значения с ключами по индексу.
    # Лучше использовать keys() и values() вместе, чтобы потом собрать словарь.
    keys = list(options.keys())
    values = list(options.values())

    # 2. Используем itertools.product для генерации всех комбинаций значений
    all_combinations = itertools.product(*values)

    print(f"\nTotal possible combinations (if not stopped early): {2 * len(options['number_rooms']) * len(options['floors_in_house']) * len(options['floor']) * len(options['square']) * len(options['city']) * len(options['ad_type']) * len(options['type_property']) * len(options['object_type']) * len(options['street']) * len(options['price']) * len(options['description']) * len(options['furniture']) * len(options['animals']) * len(options['children'])}")

    # 3. Перебираем все комбинации и создаем новый словарь для каждой
    # Этот цикл может выполняться очень долго, если комбинаций много!
    count = 0
    for combination_values in all_combinations:
        # Создаем словарь для текущей комбинации
        base_dict = dict(zip(keys, combination_values))

        districts = City_Districts.select().where(City_Districts.city_name == base_dict.get('city'))
        for district in districts[:2]:
            final_combination_dict = base_dict.copy()  # Создаем копию, чтобы не менять base_dict
            final_combination_dict['district'] = district.district

            # Теперь final_combination_dict содержит город И район, и это уникальная комбинация
            count += 1
            # print(f"Processed {count} combinations. Example: {final_combination_dict}")

            add_all_options(user.id, final_combination_dict)



    # add_all_options()