# handlers.py
import re
import time
from aiogram import types
from aiogram.types import FSInputFile
from utils.downloader import download_and_cache, get_video_id_from_url
from db.crud import add_user_video
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder
from urllib.parse import quote
import os
from utils.logger import logger

FILE_CACHE = {}

def get_recognize_keyboard(file_path: str):
    # Кодируем путь, чтобы не было проблем с символами
    safe_path = quote(file_path, safe='')
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Распознать музыку",
        callback_data=f"recognize:{safe_path}"
    )
    return builder.as_markup()


# Регулярка TikTok
TIKTOK_PATTERN = re.compile(
    r"https?://(?:vm\.|vt\.|t\.|www\.|m\.)?tiktok\.com",
    re.IGNORECASE
)

# /start — без декоратора
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"/start from user={user_id}")
    await message.answer(
        "Привет! Кидай ссылку на TikTok — скачаю видео **без водяного знака**."
    )


# Обработка ссылок
async def handle_tiktok(message: types.Message):
    url = message.text.strip()
    user_id = message.from_user.id
    logger.info(f"New TikTok request user={user_id}, url={url}")

    t_total = time.time()

    # — Проверка ссылки
    if not TIKTOK_PATTERN.search(url):
        logger.warning(f"Invalid TikTok URL from user={user_id}: {url}")
        await message.answer("Это не ссылка на TikTok.")
        return

    t_check = time.time()

    # — Скачивание
    file_path, suffix = await download_and_cache(url)
    logger.info(f"Downloaded video user={user_id}, path={file_path}, suffix={suffix}")
    t_download = time.time()

    if not file_path:
        logger.error(f"Download failed url={url} user={user_id}")
        await message.answer("Не удалось скачать видео.")
        return

    file_hash = get_video_id_from_url(url)
    FILE_CACHE[file_hash] = file_path
    logger.debug(f"Generated file_hash={file_hash} for user={user_id}")

    # — Отправка
    try:
        video = FSInputFile(file_path)
        sent_msg = await message.answer_video(
            video,
            caption="Готово! Без водяного знака",
            reply_markup=get_recognize_keyboard(file_hash[:12])
        )
        logger.info(f"Video sent user={user_id}, file={file_path}")
        t_send = time.time()

    except Exception as e:
        logger.exception(f"Send failed user={user_id}: {e}")
        await message.answer("Ошибка при отправке в Telegram.")
        return

    language = message.from_user.language_code or "unknown"
    await add_user_video(user_id=user_id, url=url, region=language, suffix=suffix)
    logger.info(f"DB updated user={user_id}, url={url}, region={language}, suffix={suffix}")

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

    logger.info(
        f"Timing user={user_id} | "
        f"check:{time_check:.2f}s | "
        f"download:{time_download:.2f}s | "
        f"send:{time_send:.2f}s | "
        f"total:{time_total:.2f}s"
    )
