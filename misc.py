from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import settings

bot = Bot(settings.bot.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dispatcher = Dispatcher()
