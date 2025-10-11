from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Базовая директория ---
# Это гарантирует, что все пути будут относительными к файлу настроек
BASE_DIR = Path(__file__).parent.resolve()

# Загрузка переменных окружения
load_dotenv()


# ====================================================================
# I. КЛАССЫ НАСТРОЕК (Pydantic Settings)
# ====================================================================

class BotSettings(BaseSettings):
    """Настройки для Telegram-бота и общие константы."""
    # Префикс 'BOT_' в .env (например, BOT_TOKEN)
    model_config = SettingsConfigDict(env_prefix='BOT_')

    TOKEN: str = Field(..., description="Токен Telegram-бота", min_length=1)
    NAME: str = Field('rea1_estate_bot', description="Имя бота")
    ADMIN_CHAT_ID: int = Field(..., description="ID администратора для уведомлений")
    SUPPORT_URL: str = Field('https://t.me/BotFather', description="URL поддержки")

    # Константы пагинации
    COUNT_IN_PAGE: int = Field(8, ge=1, description="Количество объектов на страницу в списках")
    COUNT_CARDS_IN_BATCH: int = Field(4, ge=1, description="Количество карточек в одной пачке для поиска")

    # Режим контакта
    CONTACT_MODE: str = Field("appointment", description="Режим контакта: 'appointment' или 'contact'")


class DatabaseSettings(BaseSettings):
    """Настройки для PostgreSQL базы данных."""
    # Префикс 'DB_' в .env
    model_config = SettingsConfigDict(env_prefix='DB_')

    HOST: str = Field("localhost", description="Хост базы данных")
    PORT: int = Field(5432, description="Порт базы данных")
    USER: str = Field("postgres", description="Имя пользователя базы данных")
    PASSWORD: str = Field(..., description="Пароль пользователя базы данных", min_length=1)
    NAME: str = Field('RealEstateBot', description="Имя базы данных")

    @property
    def DATABASE_URL(self) -> str:
        """Формирует URL для подключения к базе данных (для синхронных ORM)."""
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Формирует URL для асинхронных ORM (например, с asyncpg)."""
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


class PathSettings(BaseSettings):
    """Настройки путей к файлам и директориям проекта."""
    model_config = SettingsConfigDict(env_prefix='PATH_')

    DIR_PHOTO_ESTATES: Path = Field(BASE_DIR / "bot" / "photos" / "photos_estates",
                                    description="Путь к директории с фото объявлений")
    HANDLERS_DIR: Path = Field(BASE_DIR / "bot" / "handlers", description="Директория с файлами хендлеров")


class ImageIDs(BaseSettings):
    """Настройки Telegram File ID для изображений."""
    # Здесь нет префикса, так как это константы, а не переменные окружения

    MAIN_MENU: str = 'AgACAgIAAxkBAAPyaOpA6ppOc1VsXjEK3uis-em_WXIAAqYLMhtjpVlLXlsHPM6l8MoBAAMCAAN5AAM2BA'
    TUTORIAL: str = 'AgACAgIAAxkBAAP2aOpA6mg7urCWDFBfAAHnR-3FxdmdAAKqCzIbY6VZS-wxpVnyqYfdAQADAgADeAADNgQ'
    FAVORITES_ADS: str = 'AgACAgIAAxkBAAPxaOpA6vxql1Lw5vcGDJD60l9_Gk4AAqcLMhtjpVlLD-GFDGL1wSQBAAMCAAN5AAM2BA'
    ADD_AD: str = 'AgACAgIAAxkBAAPuaOpA6mjiHVIH34Z6yaPyrhMIabAAAqQLMhtjpVlLieZoJ9JVsIoBAAMCAAN5AAM2BA'
    ADMIN_PANEL: str = 'AgACAgIAAxkBAAPvaOpA6po4aH-Ph4RZgads9bMGZpAAAqMLMhtjpVlLAXJO1ULzeq4BAAMCAAN5AAM2BA'
    CHANGE_LANG: str = 'AgACAgIAAxkBAAPwaOpA6gQ2BLMtqMOfyiHI-m_SMn0AAqULMhtjpVlLXKPzXptTRgMBAAMCAAN5AAM2BA'
    SETTINGS_SEARCH: str = 'AgACAgIAAxkBAAP1aOpA6tq0Ho18Dahoo3Sesj9bz-kAAqsLMhtjpVlLg98ayxg26FIBAAMCAAN5AAM2BA'
    MY_ADS: str = 'AgACAgIAAxkBAAPzaOpA6rtgI17w2urkurJnomyNjeYAAqgLMhtjpVlLySJYp6pnTtYBAAMCAAN5AAM2BA'
    SEARCH: str = 'AgACAgIAAxkBAAP0aOpA6jV5wArkIznU9SWYSIqr51IAAqkLMhtjpVlLSQddB9DfM2QBAAMCAAN5AAM2BA'


class SearchConstants(BaseSettings):
    """Константы, используемые для фильтрации и создания объявлений."""

    # Параметры комнат
    PARAMS_CREATE: list[str] = [
        "rooms_1_0", "rooms_1_1", "rooms_2_1", "rooms_3_1", "rooms_4_1", "rooms_5_1_more"
    ]

    # Параметры поиска
    PARAMS_SEARCH: list[str] = PARAMS_CREATE + ["duplex", "villa", "only_owner", 'all_params']

    PRICES_RENT_SEARCH: list[str] = [
        "rent_price_1000zl", "rent_price_2000zl", "rent_price_3000zl", "rent_price_4000zl", "rent_price_5000zl",
        "rent_price_6000zl", "rent_price_7000zl", "rent_price_8000zl", "rent_price_9000zl", "rent_price_10000zl",
        "rent_price_13000zl", "rent_price_15000zl"
    ]

    PRICES_BUY_SEARCH: list[str] = [
        "buy_price_50000", "buy_price_100000", "buy_price_200000",
        "buy_price_300000", "buy_price_500000", "buy_price_1000000"
    ]

    AREAS_SEARCH: list[str] = [
        "area_40m", "area_50m", "area_60m", "area_70m", "area_80m",
        "area_100m", "area_120m", "area_150m", "area_200m", "area_0m"
    ]

    TYPES_SEARCH: list[str] = ["new_building", "secondary"]


# ====================================================================
# II. ГЛАВНЫЙ КЛАСС НАСТРОЕК
# ====================================================================

class Settings(BaseSettings):
    """Основные настройки приложения, объединяющие все конфигурации."""
    model_config = SettingsConfigDict(
        env_file_encoding='utf-8',
        extra='ignore'  # Игнорировать переменные окружения, которые не определены в моделях
    )

    bot: BotSettings = Field(default_factory=BotSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    images: ImageIDs = Field(default_factory=ImageIDs)
    search: SearchConstants = Field(default_factory=SearchConstants)

    ENVIRONMENT: str = Field("development", description="Среда выполнения (development, testing, production)")


# Создание экземпляра настроек
settings = Settings()