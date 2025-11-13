# downloader.py
import httpx
import re
from pathlib import Path
from utils import get_stable_video_id
from cache import get_cached_filepath, set_cached_filepath, clear_expired

VIDEO_DIR = "videos"
Path(VIDEO_DIR).mkdir(exist_ok=True)

async def download_and_cache(tiktok_url: str) -> str | None:
    """
    Скачивает видео по ссылке TikTok.
    Использует хеш URL как ключ.
    Возвращает путь к файлу (кэшируется).
    """
    # 1. Получаем стабильный хеш
    video_id = await get_stable_video_id(tiktok_url)
    if not video_id:
        print("[downloader] Не удалось получить video_id")
        return None

    # 2. Проверяем кэш: хеш → путь
    cached_path = get_cached_filepath(video_id)
    if cached_path:
        return cached_path

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 3. Запрос к tikwm API
            resp = await client.get("https://www.tikwm.com/api/", params={"url": tiktok_url})
            data = resp.json()

            if data.get("code") != 0:
                print("API ошибка:", data.get("msg"))
                return None

            video_url = data["data"]["play"]
            title = data["data"].get("title", "")[:50]  # ограничиваем

            # 4. Формируем имя файла
            safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
            suffix = f"_{safe_title}" if safe_title else ""
            filename = f"video_{video_id[:12]}{suffix}.mp4"  # короткий хеш в имени
            filepath = Path(VIDEO_DIR) / filename

            # 5. Скачиваем
            print(f"[downloader] Скачиваем → {filename}")
            video_resp = await client.get(video_url, timeout=120.0)
            if video_resp.status_code != 200:
                print("[downloader] Ошибка загрузки видео")
                return None

            filepath.write_bytes(video_resp.content)
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"[downloader] Сохранено: {filepath} ({size_mb:.1f} МБ)")

            # 6. Сохраняем в кэш: хеш → путь
            set_cached_filepath(video_id, str(filepath))
            clear_expired()  # опционально

            return str(filepath)

    except Exception as e:
        print(f"[downloader] Ошибка: {e}")
        return None


# === Тест ===
if __name__ == "__main__":
    import asyncio
    url = input("Введите ссылку TikTok: ")
    path = asyncio.run(download_and_cache(url))
    print("Готово:", path)