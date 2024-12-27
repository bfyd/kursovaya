import asyncio
import logging
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher

from config import TOKEN
from app.handlers import router
from database.models import async_main

bot= Bot(token= TOKEN,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def main():
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

