# stat_handler.py
from aiogram import types
from db.crud import get_user_videos
from utils.logger import logger


async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"Запрос статистики от user={user_id}")

    videos = await get_user_videos(user_id)

    if not videos:
        logger.info(f"У user={user_id} нет скачанных видео")
        await message.answer("Ты ещё не скачивал видео.")
        return

    logger.info(f"Найдено {len(videos)} видео у user={user_id}")

    text = "<b>Твои скачанные видео:</b>\n\n"

    for i, (url, suffix) in enumerate(videos, 1):
        short_url = url.split("?")[0]
        if len(short_url) > 50:
            short_url = short_url[:47] + "..."

        line = f"{i}. <a href='{url}'>{short_url}</a>"

        if suffix and suffix.strip():
            clean_suffix = suffix.lstrip("_").strip()
            if clean_suffix:
                line += f" — {clean_suffix}"

        text += line + "\n"

    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

    logger.info(f"Статистика отправлена user={user_id}")
