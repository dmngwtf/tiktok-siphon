# handlers.py
import re
import time
from aiogram import types, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from downloader import download_and_cache

# Регулярка TikTok
TIKTOK_PATTERN = re.compile(
    r"https?://(?:vm\.|vt\.|t\.|www\.|m\.)?tiktok\.com",
    re.IGNORECASE
)

# /start — без декоратора
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Кидай ссылку на TikTok — скачаю видео **без водяного знака**."
    )

# Обработка ссылок
async def handle_tiktok(message: types.Message):
    url = message.text.strip()
    t_total = time.time()

    # — Проверка ссылки
    if not TIKTOK_PATTERN.search(url):
        await message.answer("Это не ссылка на TikTok.")
        return

    t_check = time.time()

    # — Скачивание
    file_path = await download_and_cache(url)
    t_download = time.time()

    if not file_path:
        await message.answer("Не удалось скачать видео.")
        print(f"[bot] ОШИБКА: скачивание провалено")
        return

    # — Отправка
    try:
        video = FSInputFile(file_path)
        sent_msg = await message.answer_video(
            video,
            caption="Готово! Без водяного знака"
        )
        t_send = time.time()

    except Exception as e:
        await message.answer("Ошибка при отправке в Telegram.")
        print(f"[bot] Ошибка отправки: {e}")
        return

    # — Отчёт
    t_end = time.time()

    time_check = t_check - t_total
    time_download = t_download - t_check
    time_send = t_send - t_download
    time_total = t_end - t_total

    report = (
        f"**Готово!**\n\n"
        f"**Отчёт по времени:**\n"
        f"• Проверка: `{time_check:.2f}с`\n"
        f"• Скачивание + кэш: `{time_download:.2f}с`\n"
        f"• Отправка: `{time_send:.2f}с`\n"
        f"**Всего: `{time_total:.2f}с`**"
    )
    await sent_msg.reply(report, parse_mode="Markdown")

    print(
        f"[bot] УСПЕХ | "
        f"check:{time_check:.2f}s | "
        f"download:{time_download:.2f}s | "
        f"send:{time_send:.2f}s | "
        f"total:{time_total:.2f}s | "
        f"user:{message.from_user.id}"
    )