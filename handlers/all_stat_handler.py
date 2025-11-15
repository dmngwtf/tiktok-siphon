# all_stat_handler.py
from aiogram import types
from aiogram.filters import Command
from db.crud import get_total_videos, get_region_stats
from utils.logger import logger

# Маппинг кодов → страны + эмодзи
REGION_MAP = {
    "ru": ("🇷🇺 Россия", 0),
    "en": ("🇺🇸 США", 1),
    "es": ("🇪🇸 Испания", 2),
    "fr": ("🇫🇷 Франция", 3),
    "de": ("🇩🇪 Германия", 4),
    "it": ("🇮🇹 Италия", 5),
    "pt": ("🇵🇹 Португалия", 6),
    "tr": ("🇹🇷 Турция", 7),
    "ar": ("🇸🇦 Арабский", 8),
    "zh": ("🇨🇳 Китай", 9),
    "ja": ("🇯🇵 Япония", 10),
    "ko": ("🇰🇷 Корея", 11),
    "hi": ("🇮🇳 Индия", 12),
    "unknown": ("🌍 Неизвестно", 99),
}

async def cmd_all_stats(message: types.Message):

    logger.info(f"/all_stats requested by user")

    total = await get_total_videos()
    if total == 0:
        await message.answer("Нет данных.")
        return

    region_data = await get_region_stats()
    if not region_data:
        await message.answer("Нет данных по регионам.")
        return

    # Сортируем: сначала по REGION_MAP, потом по количеству
    sorted_regions = sorted(
        region_data,
        key=lambda x: (
            REGION_MAP.get(x[0], ("🌍 Другие", 999))[1],
            -x[1]
        )
    )

    # Топ-5 + "Другие"
    top_regions = []
    other_count = 0
    for code, count in sorted_regions:
        if code in REGION_MAP and REGION_MAP[code][1] < 99:
            name = REGION_MAP[code][0]
            percent = count / total * 100
            top_regions.append(f"{name} — {count} ({percent:.1f}%)")
        else:
            other_count += count

    if other_count > 0:
        percent = other_count / total * 100
        top_regions.append(f"🌍 Другие — {other_count} ({percent:.1f}%)")

    text = f"<b>Всего видео скачано:</b> {total}\n\n"
    text += "<b>Распределение по регионам:</b>\n"
    text += "\n".join(top_regions)

    await message.answer(text, parse_mode="HTML")