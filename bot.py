# bot.py
import asyncio
import os
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram import F

# Импортируем хендлеры
from handlers.start_handler import cmd_start
from handlers.handlers import handle_media
from handlers.stat_handler import cmd_stats, stats_callback  # ← ДОБАВИЛИ stats_callback
from handlers.recognize_handler import handle_recognize_callback

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ===
dp.message.register(cmd_start, CommandStart())
dp.message.register(cmd_stats, Command("stats"))
dp.message.register(handle_media, F.text)

# Пагинация статистики: stats_{user_id}_{page}
dp.callback_query.register(
    stats_callback,
    lambda c: c.data and c.data.startswith("stats_") and len(c.data.split("_")) == 3
)

# Распознавание: recognize:...
dp.callback_query.register(
    handle_recognize_callback,
    lambda c: c.data and c.data.startswith("recognize:")
)

# === ЗАПУСК ===
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())