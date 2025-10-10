import asyncio
import logging

from bot.Middlewares.middlewares import BanMiddleware
from bot.utils.setup_all_routers import setup_all_routers
from misc import bot, dispatcher as dp


async def main() -> None:
    await bot.send_message(8062956903, '✅ Бот запущен')

    setup_all_routers(dp)

    dp.update.middleware(BanMiddleware())

    try:
        await dp.start_polling(bot)
    except Exception as _ex:
        print(f'There is an exception - {_ex}')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
