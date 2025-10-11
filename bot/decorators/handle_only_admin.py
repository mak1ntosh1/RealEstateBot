from functools import wraps
from aiogram import types

from config import ADMIN_CHAT_ID
from misc import bot


def handle_only_admin(func):
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        user_channel_status = await bot.get_chat_member(chat_id=ADMIN_CHAT_ID, user_id=message.from_user.id)
        if user_channel_status.status != 'left':
            return await func(message, *args, **kwargs)
    return wrapper