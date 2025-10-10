import asyncio

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.databases.database import Users
from bot.handlers.commands.main import admin_panel
from bot.states.states import RunMailing
from misc import bot

router = Router()

@router.message(RunMailing.sending)
async def sending(message: Message, state: FSMContext):
    await state.clear()

    users = list(Users.select())
    total_users = len(users)
    batch_size = 20  # Размер пачки пользователей

    count_users_blocked = 0
    shipped = 0
    text =f'''
Отправлено <code>{shipped}</code> юзерам.
Получили рассылку <code>{shipped - count_users_blocked}</code> юзеров.
'''

    newsletter_information = await message.answer(text)

    # Разделяем пользователей на группы по batch_size
    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]

        for user in batch:
            try:
                await bot.copy_message(user.user_id, message.chat.id, message.message_id)
            except Exception as ex:
                print(f"Ошибка при отправке пользователю {user.user_id}: {ex}")
                count_users_blocked += 1

        shipped += len(batch)

        try:
            text = f'''
    Отправлено <code>{shipped}</code> юзерам.
    Получили рассылку <code>{shipped - count_users_blocked}</code> юзеров.
'''
            await newsletter_information.edit_text(text)
        except Exception as ex:
            print(ex)
            print(len(batch))
            print(shipped)

        if shipped != total_users:
            # Задержка между отправкой каждой группы
            await asyncio.sleep(5)  # Задержка в 5 секунд между группами

    text = f'''
Отправлено <code>{total_users}</code> юзерам.
Получили рассылку <code>{total_users - count_users_blocked}</code> юзеров.
✅ Рассылка завершена!
'''

    await newsletter_information.delete()
    await newsletter_information.answer(text)

    await admin_panel(message)