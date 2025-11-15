import re
import time
import os
from aiogram import types
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from urllib.parse import quote
from aiogram.exceptions import TelegramEntityTooLarge
from utils.downloader import download_and_cache, get_video_id_from_url, detect_service
from db.crud import add_user_video
from utils.logger import logger

FILE_CACHE = {}

URL_PATTERNS = {
    "tiktok": re.compile(r"https?://(?:vm\.|vt\.|t\.|www\.|m\.)?tiktok\.com", re.IGNORECASE),
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com", re.IGNORECASE),
    "youtube": re.compile(r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/(?:shorts/)?", re.IGNORECASE)
}

def get_recognize_keyboard(file_hash: str):
    safe_hash = quote(file_hash, safe='')
    builder = InlineKeyboardBuilder()
    builder.button(text="Распознать музыку", callback_data=f"recognize:{safe_hash}")
    return builder.as_markup()

# ====== Логические блоки ======

async def check_service_url(message: types.Message, url: str) -> str | None:
    service = detect_service(url)
    if not service or not URL_PATTERNS.get(service, re.compile("")).search(url):
        logger.warning(f"Invalid URL from user={message.from_user.id}: {url}")
        await message.answer("Ссылка не поддерживается.")
        return None
    return service

async def download_media(message: types.Message, url: str):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_video")
    result = await download_and_cache(url)
    if not result:
        logger.error(f"Download failed url={url} user={message.from_user.id}")
        await message.answer("Не удалось скачать файл.")
        return None, None, None

    file_path, suffix = result
    file_hash = get_video_id_from_url(url)
    FILE_CACHE[file_hash] = file_path
    logger.debug(f"Generated file_hash={file_hash} for user={message.from_user.id}")
    return file_path, suffix, file_hash

async def check_file_size(message: types.Message, file_path: str) -> bool:
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > 50:
        logger.warning(f"File too large: {file_size_mb:.1f}MB user={message.from_user.id}")
        await message.answer(
            f"**Файл слишком большой!**\n\n"
            f"Размер: `{file_size_mb:.1f} МБ`\n"
            f"Telegram не позволяет отправлять видео > 50 МБ.\n"
            f"Попробуй другое видео.",
            parse_mode="Markdown"
        )
        return False
    return True

async def send_file(message: types.Message, file_path: str, file_hash: str):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_video")
    try:
        file = FSInputFile(file_path)
        sent_msg = await message.answer_video(
            video=file,
            caption="Готово! Без водяного знака",
            reply_markup=get_recognize_keyboard(file_hash[:12])
        )
        logger.info(f"File sent user={message.from_user.id}, size={os.path.getsize(file_path)/(1024*1024):.1f}MB")
        t_send = time.time()
        return sent_msg, t_send
    except TelegramEntityTooLarge:
        logger.warning(f"TelegramEntityTooLarge caught for user={message.from_user.id}")
        await message.answer(
            f"**Не удалось отправить файл**\n"
            f"Размер слишком большой: `{os.path.getsize(file_path)/(1024*1024):.1f} МБ`\n"
            f"Максимум для видео — 50 МБ.",
            parse_mode="Markdown"
        )
        return None, None
    except Exception as e:
        logger.exception(f"Send failed user={message.from_user.id}: {e}")
        await message.answer("Ошибка при отправке в Telegram.")
        return None, None

async def update_db(user_id: int, url: str, lang: str, suffix: str):
    language = lang or "unknown"
    await add_user_video(user_id=user_id, url=url, region=language, suffix=suffix)
    logger.info(f"DB updated user={user_id}, url={url}, region={language}, suffix={suffix}")

async def send_report(sent_msg: types.Message, t_total: float, t_check: float, t_download: float, t_send: float):
    t_end = time.time()
    report = (
        f"**Готово!**\n\n"
        f"**Отчёт по времени:**\n"
        f"• Проверка: `{t_check - t_total:.2f}с`\n"
        f"• Скачивание + кэш: `{t_download - t_check:.2f}с`\n"
        f"• Отправка: `{t_send - t_download:.2f}с`\n"
        f"**Всего: `{t_end - t_total:.2f}с`**"
    )
    await sent_msg.reply(report, parse_mode="Markdown")
    logger.info(
        f"Timing user={sent_msg.chat.id} | "
        f"check:{t_check - t_total:.2f}s | "
        f"download:{t_download - t_check:.2f}s | "
        f"send:{t_send - t_download:.2f}s | "
        f"total:{t_end - t_total:.2f}s"
    )

# ====== Главная функция ======

async def handle_media(message: types.Message):
    url = message.text.strip()
    user_id = message.from_user.id
    t_total = time.time()

    service = await check_service_url(message, url)
    if not service:
        return
    t_check = time.time()

    file_path, suffix, file_hash = await download_media(message, url)
    t_download = time.time()
    if not file_path:
        return

    if not await check_file_size(message, file_path):
        return

    sent_msg, t_send = await send_file(message, file_path, file_hash)
    if not sent_msg:
        return

    await update_db(user_id, url, message.from_user.language_code, suffix)
    await send_report(sent_msg, t_total, t_check, t_download, t_send)
