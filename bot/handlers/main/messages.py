from aiogram import Router, F
from aiogram.types import Message

from bot.databases.database import Users
from bot.keyboards.main import get_main_menu_kb
from bot.utils.utils import get_text

router = Router()

OLD_MAIN_MENU = [
    '🖥 Главное меню', '🖥 Main Menu', '🖥 Головне меню', '🖥 Ana menü', '🖥 Ana Menü'
]

@router.message(F.text.in_(['🗂 Главное меню', '🗂 Main Menu', '🗂 Головне меню', '🗂 Ana menü'] + OLD_MAIN_MENU))
async def main_menu(message: Message):
    user = Users.get_or_none(Users.user_id == message.from_user.id)
    await message.answer(
        text=get_text(key='main_menu', lang=user.language),
        reply_markup=get_main_menu_kb(user.language)
    )

















