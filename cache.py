# cache.py
import diskcache as dc
from pathlib import Path

CACHE_DIR = "cache"
Path(CACHE_DIR).mkdir(exist_ok=True)

# TTL = 7 дней
cache = dc.Cache(CACHE_DIR, timeout=1 * 24 * 3600)

def get_cached_filepath(video_id: str) -> str | None:
    """Получить путь к файлу из кэша по хешу"""
    if video_id in cache:
        filepath = cache[video_id]
        if Path(filepath).exists():
            print(f"[cache] ХИТ: {filepath}")
            return filepath
        else:
            print(f"[cache] Файл удалён, очищаем кэш: {video_id}")
            del cache[video_id]
    return None


def set_cached_filepath(video_id: str, filepath: str):
    """Сохранить: хеш → путь к файлу"""
    cache[video_id] = filepath
    print(f"[cache] СОХРАНЕНО: {video_id} → {filepath}")


def clear_expired():
    """Очистить устаревшие записи (по TTL)"""
    cache.expire()