import asyncio
import logging
from aiogram import Bot, Dispatcher
import os
TOKEN = os.getenv("TOKEN")

from app.handllers import router
from app.bd.models import async_main

bot = Bot(TOKEN)
dp= Dispatcher()

async def main():
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Exit')