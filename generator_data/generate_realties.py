import itertools
import random  # <-- Добавляем импорт модуля random

from bot.databases.database import City_Districts, Realty, Users


def add_all_options(user_id_db: int, options: dict):
    # Эта функция остается без изменений
    Realty.create(
        user=user_id_db,
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
    # Получаем все города один раз
    cities = [city_district.city_name for city_district in City_Districts.select(City_Districts.city_name).distinct()]
    user = Users.get(Users.user_id == 8488874560)

    options = {
        'city': cities,  # <-- Используем полный список городов
        'ad_type': ['rent', 'sale'],
        'type_property': ['land', 'commercial_property', 'residential_property'],
        'object_type': ['villa', 'duplex', 'flat'],
        'number_rooms': ["rooms_1_0", "rooms_1_1", "rooms_2_1", "rooms_3_1", "rooms_4_1", "rooms_5_1_more"],
        'price': [180000, 250000, 95000, 500000],  # <-- Добавим разнообразия
        'square': ['80', '120', '45', '200'],  # <-- Добавим разнообразия
        'floor': ['1', '5', '10', '15'],  # <-- Добавим разнообразия
        'floors_in_house': ['5', '10', '16', '25'],  # <-- Добавим разнообразия
        'street': ["İstiklal Caddesi", "Atatürk Bulvarı", "Bağdat Caddesi"],  # <-- Добавим разнообразия
        'description': ['test_description'],
        'furniture': ['furnished_yes', 'furnished_no'],
        'animals': ['animals_yes', 'animals_no', 'animals_maybe'],
        'children': ['children_yes', 'children_no', 'children_maybe'],
    }

    # === НОВАЯ ЛОГИКА ===

    # 1. Получаем ключи и значения, как и раньше
    keys = list(options.keys())
    values = list(options.values())

    # 2. Генерируем все возможные базовые комбинации
    # itertools.product возвращает итератор, который не занимает много памяти
    all_combinations_iterator = itertools.product(*values)

    # 3. Превращаем итератор в список
    # ВНИМАНИЕ: Если комбинаций МИЛЛИОНЫ, это может потребовать много оперативной памяти.
    # Но для генерации тестовых данных это самый правильный подход.
    print("Generating all combinations into a list...")
    all_combinations_list = list(all_combinations_iterator)
    print("Done. Shuffling the list...")

    # 4. Перемешиваем список в случайном порядке!
    random.shuffle(all_combinations_list)
    print("Shuffle complete. Starting data generation.")

    # 5. Перебираем УЖЕ ПЕРЕМЕШАННЫЙ список
    total_combinations = len(all_combinations_list)
    count = 0
    for i, combination_values in enumerate(all_combinations_list, 1):
        # Создаем словарь для текущей (случайной) комбинации
        base_dict = dict(zip(keys, combination_values))

        # Получаем районы для города из текущей комбинации
        districts = City_Districts.select().where(City_Districts.city_name == base_dict.get('city'))

        # Если для города нет районов в БД, пропускаем его
        if not districts:
            print(f"Warning: No districts found for city '{base_dict.get('city')}'. Skipping.")
            continue

        # Берем до 2-х районов для каждого города, как в вашем примере
        for district in districts[:2]:
            final_combination_dict = base_dict.copy()
            final_combination_dict['district'] = district.district

            count += 1
            print(
                f"Processing combination {i}/{total_combinations} | DB entry #{count} | City: {base_dict['city']}, Ad: {base_dict['ad_type']}, Rooms: {base_dict['number_rooms']}")

            # Добавляем запись в базу данных
            add_all_options(user.id, final_combination_dict)

    print(f"\nGeneration complete! Total entries added: {count}")