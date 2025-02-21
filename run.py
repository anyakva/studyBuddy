import asyncio
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from aiogram import Bot, Dispatcher
from app.handllers import router
from app.bd.models import async_main

load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("No TOKEN provided")

bot = Bot(TOKEN)
dp = Dispatcher()
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok"}

async def start_bot():
    logging.info("Starting bot polling...")
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)

async def start_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)), log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    bot_task = asyncio.create_task(start_bot())
    server_task = asyncio.create_task(start_server())
    await asyncio.gather(bot_task, server_task)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())  # Теперь сервер и бот работают без конфликта event loop
