from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()


TOKEN = os.getenv('BOT_TOKEN')
if TOKEN is None:
    raise ValueError("BOT_TOKEN environment variable is not set!")

BOT_NAME = 'getdomix_bot'



ADMIN_CHAT_ID = -4728916434  # ID администратора для уведомлений
COUNT_IN_PAGE = 15



DIR_PHOTO = './bot/photos/'

# Photos
TUTORIAL = DIR_PHOTO + 'tutorial.jpg'


# Данные для подключения к бд
DB_HOST = os.getenv('DB_HOST', '83.217.209.163')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_USER = os.getenv('DB_USER', 'postgres')  # Имя пользователя БД
DB_PASSWORD = os.getenv('DB_PASSWORD')  # Пароль БД (обязательно из ENV)
if DB_PASSWORD is None:
    raise ValueError("DB_PASSWORD environment variable is not set!")
DB_NAME = os.getenv('DB_NAME', 'RealEstateBot')  # Имя базы данных


DIR_PHOTO_ESTATES = './bot/photos/photos_estates/'
HANDLERS_DIR = Path(__file__).parent / "bot" / "handlers"

# Параметры для создания объявления
PARAMS_CREATE = ["rooms_1_0", "rooms_1_1", "rooms_2_1", "rooms_3_1", "rooms_4_1", "rooms_5_1_more"]


COUNT_CARDS_IN_BATCH = 4


# Параметры для настройки поиска
PARAMS_SEARCH = PARAMS_CREATE + ["duplex", "villa", "only_owner", 'all_params']

PRICES_RENT_SEARCH = [
    "rent_price_1000zl", "rent_price_2000zl", "rent_price_3000zl", "rent_price_4000zl", "rent_price_5000zl",
    "rent_price_6000zl", "rent_price_7000zl", "rent_price_8000zl", "rent_price_9000zl", "rent_price_10000zl",
    "rent_price_13000zl", "rent_price_15000zl"
]

PRICES_BUY_SEARCH = [
    "buy_price_50000", "buy_price_100000", "buy_price_200000",
    "buy_price_300000", "buy_price_500000", "buy_price_1000000"
]

AREAS_SEARCH = [
    "area_40m", "area_50m", "area_60m", "area_70m", "area_80m",
    "area_100m", "area_120m", "area_150m", "area_200m", "area_0m"
]

TYPES_SEARCH = ["new_building", "secondary"]

CONTACT_MODE = "appointment"  # Или "contact"


SUPPORT_URL = 'https://t.me/GetDomix_support'




