# handlers/recognize_handler.py
from pathlib import Path
import asyncio
from aiogram import types
from urllib.parse import unquote
from glob import glob
from typing import Optional, Tuple
from utils.utils import parse_hash, find_video_by_hash, format_track_text
VIDEOS_DIR = Path("videos")


async def recognize_audio(file_path: Path, start_sec: int = 0, duration: int = 10):
    # импорт внутри, т.к. может быть тяжёлый
    from utils.music_finder import recognize_mp4
    # запуск в отдельном потоке, чтобы не блокировать event loop
    return await asyncio.to_thread(recognize_mp4, str(file_path), start_sec, duration)

async def safe_edit_reply_markup(message: types.Message):
    try:
        await message.edit_reply_markup(reply_markup=None)
    except Exception:
        # логирование по необходимости
        pass




async def handle_recognize_callback(callback: types.CallbackQuery):
    await callback.answer()
    file_hash = parse_hash(callback.data or "")
    if not file_hash:
        await callback.message.reply("Ошибка: неверный формат данных.")
        return

    file_path = find_video_by_hash(VIDEOS_DIR, file_hash)
    if not file_path:
        await callback.message.reply("Видео больше недоступно.")
        return

    # Показать печатает
    await callback.bot.send_chat_action(chat_id=callback.message.chat.id, action="typing")

    try:
        track = await recognize_audio(file_path, start_sec=0, duration=10)
    except Exception as e:
        # логировать e
        await callback.message.reply("Ошибка при распознавании музыки.")
        return

    text = format_track_text(track)
    await callback.message.reply(text, parse_mode="Markdown")
    await safe_edit_reply_markup(callback.message)
