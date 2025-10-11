from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import settings

bot = Bot(settings.BotSettings.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dispatcher = Dispatcher()
