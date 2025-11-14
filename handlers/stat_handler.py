# stat_handler.py
from aiogram import types
from aiogram.filters import Command
from db.crud import get_user_videos

async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    videos = await get_user_videos(user_id)

    if not videos:
        await message.answer("Ты ещё не скачивал видео.")
        return

    text = "<b>Твои скачанные видео:</b>\n\n"
    for i, (url, suffix) in enumerate(videos, 1):
        short_url = url.split("?")[0]
        if len(short_url) > 50:
            short_url = short_url[:47] + "..."

        # ← Кликабельная ссылка
        line = f"{i}. <a href='{url}'>{short_url}</a>"

        # ← Добавляем suffix, если есть
        if suffix and suffix.strip():
            # Убираем подчёркивания в начале
            clean_suffix = suffix.lstrip("_").strip()
            if clean_suffix:
                line += f" — {clean_suffix}"

        text += line + "\n"

    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )