# downloader.py
import httpx
import hashlib
from pathlib import Path
from cache import get_cached_filepath, set_cached_filepath, clear_expired

VIDEO_DIR = "videos"
Path(VIDEO_DIR).mkdir(exist_ok=True)

def get_video_id_from_url(url: str) -> str:
    """
    Делает SHA-256 хеш от исходной ссылки.
    Без редиректов, без ожидания.
    """
    url = url.strip().lower()  # нормализация
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

async def download_and_cache(tiktok_url: str) -> tuple[str | None, str | None]:
    """
    Скачивает видео TikTok.
    Ключ кэша — хеш от исходной ссылки.
    """
    # 1. КЛЮЧ КЭША — сразу от ссылки
    video_id = get_video_id_from_url(tiktok_url)
    print(f"[downloader] Ключ кэша: {video_id[:16]}...")

    # 2. Проверяем кэш
    cached_path = get_cached_filepath(video_id)
    if cached_path:
        print(f"[cache] ХИТ: {cached_path}")
        return cached_path, ''

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 3. TikWM API
            resp = await client.get(
                "https://www.tikwm.com/api/",
                params={"url": tiktok_url, "hd": 1}
            )
            data = resp.json()

            if data.get("code") != 0:
                print("API ошибка:", data.get("msg"))
                return None

            video_url = data["data"]["play"]
            title = data["data"].get("title", "")[:50]

            # 4. Имя файла
            safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
            suffix = f"_{safe_title}" if safe_title else ""


            #SUFFIX!!!!!!!!



            print(f"SUFFIX = {suffix}")
            filename = f"video_{video_id[:12]}{suffix}.mp4"
            filepath = Path(VIDEO_DIR) / filename

            # 5. Скачиваем
            print(f"[downloader] Скачиваем → {filename}")
            video_resp = await client.get(video_url, timeout=120.0)
            if video_resp.status_code != 200:
                print("[downloader] Ошибка загрузки")
                return None

            filepath.write_bytes(video_resp.content)
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"[downloader] Сохранено: {filepath} ({size_mb:.1f} МБ)")

            # 6. КЭШИРУЕМ
            set_cached_filepath(video_id, str(filepath))
            clear_expired()

            return str(filepath), suffix

    except Exception as e:
        print(f"[downloader] Ошибка: {e}")
        return None


# === ТЕСТ ===
if __name__ == "__main__":
    import asyncio
    url = input("Введите ссылку TikTok: ")
    path = asyncio.run(download_and_cache(url))
    print("Готово:", path)