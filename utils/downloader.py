import httpx
import hashlib
from pathlib import Path
from utils.cache import get_cached_filepath, set_cached_filepath, clear_expired
from utils.logger import logger
import asyncio
import yt_dlp

VIDEO_DIR = "videos"
Path(VIDEO_DIR).mkdir(exist_ok=True)

# ====== Общие функции ======

def get_video_id_from_url(url: str) -> str:
    url = url.strip().lower()
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def sanitize_title(title: str) -> str:
    return "".join(c for c in title if c.isalnum() or c in " _-").strip()

# ====== Сервисные загрузчики ======

async def download_tiktok(url: str) -> tuple[str | None, str | None]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get("https://www.tikwm.com/api/", params={"url": url, "hd": 1})
            data = resp.json()
            if data.get("code") != 0:
                logger.warning(f"[tiktok] API ошибка: {data.get('msg')}")
                return None, None

            video_url = data["data"]["play"]
            title = data["data"].get("title", "")[:50]
            suffix = f"_{sanitize_title(title)}" if title else ""

            video_id = get_video_id_from_url(url)
            filename = f"video_{video_id[:12]}{suffix}.mp4"
            filepath = Path(VIDEO_DIR) / filename

            logger.info(f"[tiktok] Скачиваем → {filename}")
            video_resp = await client.get(video_url, timeout=120.0)
            if video_resp.status_code != 200:
                logger.error("[tiktok] Ошибка загрузки")
                return None, None

            filepath.write_bytes(video_resp.content)
            size_mb = filepath.stat().st_size / (1024 * 1024)
            logger.info(f"[tiktok] Сохранено: {filepath} ({size_mb:.1f} МБ)")

            return str(filepath), suffix.strip('_')
    except Exception as e:
        logger.exception(f"[tiktok] Ошибка: {e}")
        return None, None

async def download_instagram(url: str) -> tuple[str | None, str | None]:
    try:
        def _download_blocking(u: str):
            ydl_opts = {
                "outtmpl": f"{VIDEO_DIR}/ig_%(id)s.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "restrictfilenames": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(u, download=True)
                if not info:
                    return None, None

                filepath = info.get("_filename") or ydl.prepare_filename(info)
                suffix = sanitize_title(info.get("title") or "instagram")

                return filepath, suffix

        filepath, suffix = await asyncio.to_thread(_download_blocking, url)
        if not filepath:
            return None, None

        size_mb = Path(filepath).stat().st_size / (1024 * 1024)
        logger.info(f"[instagram] Сохранено: {filepath} ({size_mb:.1f} МБ)")

        return str(filepath), suffix

    except Exception as e:
        logger.exception(f"[instagram] Ошибка: {e}")
        return None, None

# ====== Словарь сервисов ======

SERVICES = {
    "tiktok": download_tiktok,
    "instagram": download_instagram,
}

def detect_service(url: str) -> str | None:
    url_lower = url.lower()
    if "tiktok.com" in url_lower:
        return "tiktok"
    if "instagram.com" in url_lower:
        return "instagram"
    return None

# ====== Универсальная функция ======

async def download_and_cache(url: str) -> tuple[str | None, str | None]:
    video_id = get_video_id_from_url(url)
    logger.debug(f"[downloader] Ключ кэша: {video_id[:16]}...")

    cached_path = get_cached_filepath(video_id)
    if cached_path:
        logger.info(f"[cache] HIT: {cached_path}")
        suffix = cached_path.split("/")[-1].split(".")[0].rsplit("_", 1)[-1]
        return cached_path, suffix

    service_name = detect_service(url)
    if not service_name or service_name not in SERVICES:
        logger.warning(f"[downloader] Неизвестный сервис для URL: {url}")
        return None, None

    download_func = SERVICES[service_name]
    filepath, suffix = await download_func(url)
    if not filepath:
        return None, None

    set_cached_filepath(video_id, filepath)
    clear_expired()

    return filepath, suffix
