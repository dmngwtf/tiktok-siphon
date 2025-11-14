# stat_handler.py
from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.crud import get_user_videos
from utils.logger import logger

PAGE_SIZE = 5


async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"Запрос статистики от user={user_id}")

    await show_stats_page(message, user_id, page=0)


async def show_stats_page(message_or_callback: types.Message | types.CallbackQuery,
                          user_id: int,
                          page: int):
    videos = await get_user_videos(user_id)
    total = len(videos)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_videos = videos[start:end]

    if not page_videos and page == 0:
        logger.info(f"У user={user_id} нет скачанных видео")
        await _answer_or_edit(message_or_callback, "Ты ещё не скачивал видео.")
        return

    text = f"<b>Твои скачанные видео:</b> ({total} всего)\n\n"

    for i, (url, suffix) in enumerate(page_videos, 1):
        global_idx = start + i
        short_url = url.split("?")[0]
        if len(short_url) > 50:
            short_url = short_url[:47] + "..."

        line = f"{global_idx}. <a href='{url}'>{short_url}</a>"

        if suffix and suffix.strip():
            clean_suffix = suffix.lstrip("_").strip()
            if clean_suffix:
                line += f" — {clean_suffix}"

        text += line + "\n"

    # === Клавиатура ===
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    row = []

    if page > 0:
        row.append(
            InlineKeyboardButton(text="Назад", callback_data=f"stats_{user_id}_{page-1}")
        )

    if end < total:
        row.append(
            InlineKeyboardButton(text="Вперёд", callback_data=f"stats_{user_id}_{page+1}")
        )

    if row:
        keyboard.inline_keyboard.append(row)

    # === Отправка / редактирование ===
    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=keyboard
        )
    else:
        await message_or_callback.message.edit_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=keyboard
        )

    logger.info(f"Статистика страница {page} отправлена user={user_id}")


# Вспомогательная функция
async def _answer_or_edit(msg_or_cb, text, **kwargs):
    if isinstance(msg_or_cb, types.Message):
        await msg_or_cb.answer(text, **kwargs)
    else:
        await msg_or_cb.message.edit_text(text, **kwargs)

# Обработчик кнопок
async def stats_callback(callback: types.CallbackQuery):
    try:
        _, user_id_str, page_str = callback.data.split("_")
        user_id = int(user_id_str)
        page = int(page_str)
    except ValueError:
        await callback.answer("Ошибка данных.", show_alert=True)
        return

    if callback.from_user.id != user_id:
        await callback.answer("Это не твоя статистика!", show_alert=True)
        return

    await show_stats_page(callback, user_id, page)
    await callback.answer()
