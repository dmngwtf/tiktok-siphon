# bot.py
import asyncio
import os
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram import F
from handlers.handlers import cmd_start, handle_tiktok  # ← импортируем функции
from handlers.stat_handler import cmd_stats

load_dotenv()

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ===
dp.message.register(cmd_start, CommandStart())
dp.message.register(cmd_stats, Command("stats"))
       # ← фильтр здесь
dp.message.register(handle_tiktok, F.text)
         # ← любой текст

# === ЗАПУСК ===
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())