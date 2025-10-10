from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import TOKEN

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dispatcher = Dispatcher()
