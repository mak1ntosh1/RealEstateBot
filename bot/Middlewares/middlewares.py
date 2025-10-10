from aiogram import BaseMiddleware, types

from bot.databases.database import Users


class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.TelegramObject, data: dict):
        event_type = event.message or event.callback_query
        username = event_type.from_user.username
        user_id = event_type.from_user.id

        user = Users.get_or_none(Users.user_id == user_id)
        if not user:
            Users.create(
                user_id=user_id,
                username=username
            )

        return await handler(event, data)
