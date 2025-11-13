# bot.py
import asyncio
import time
import re
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram import F
from aiogram.types import FSInputFile
from downloader import download_and_cache  # ← Только это!


load_dotenv()
# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регулярка — ловит все TikTok ссылки
TIKTOK_PATTERN = re.compile(
    r"https?://(?:vm\.|vt\.|t\.|www\.|m\.)?tiktok\.com",
    re.IGNORECASE
)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Кидай ссылку на TikTok — скачаю видео **без водяного знака**."
    )

@dp.message(F.text)
async def handle_tiktok(message: types.Message):
    url = message.text.strip()
    t_total = time.time()

    # — Проверка ссылки
    if not TIKTOK_PATTERN.search(url):
        await message.answer("Это не ссылка на TikTok.")
        return

    t_check = time.time()

    # — Статус
    #status_msg = await message.answer("Скачиваю видео...")
    t_status = time.time()

    # — Скачивание + кэширование
    file_path = await download_and_cache(url)
    t_download = time.time()

    if not file_path:
        #await status_msg.edit_text("Не удалось скачать видео.")
        print(f"[bot] ОШИБКА: скачивание провалено")
        return

    # — Подготовка к отправке
    video = FSInputFile(file_path)
    #await status_msg.edit_text("Отправляю видео в Telegram...")

    try:
        sent_msg = await message.answer_video(
            video,
            caption="Готово! Без водяного знака"
        )
        t_send = time.time()
        #await #status_msg.delete()

    except Exception as e:
        #await status_msg.edit_text("Ошибка при отправке в Telegram.")
        print(f"[bot] Ошибка отправки: {e}")
        return

    # — Финальный отчёт
    t_end = time.time()

    # Время по этапам
    time_check     = t_check - t_total
    time_status    = t_status - t_check
    time_download  = t_download - t_status
    time_send      = t_send - t_download
    time_total     = t_end - t_total

    report = (
        f"**Готово!**\n\n"
        f"**Отчёт по времени:**\n"
        f"• Проверка ссылки: `{time_check:.2f}с`\n"
        f"• Статус: `{time_status:.2f}с`\n"
        f"• Скачивание + кэш: `{time_download:.2f}с`\n"
        f"• Отправка в TG: `{time_send:.2f}с`\n"
        f"**Всего: `{time_total:.2f}с`**"
    )

    await sent_msg.reply(report, parse_mode="Markdown")

    # Лог в консоль
    print(
        f"[bot] УСПЕХ | "
        f"check:{time_check:.2f}s | "
        f"status:{time_status:.2f}s | "
        f"download:{time_download:.2f}s | "
        f"send:{time_send:.2f}s | "
        f"total:{time_total:.2f}s | "
        f"user:{message.from_user.id}"
    )

# === ЗАПУСК ===
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())