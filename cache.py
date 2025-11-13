# cache.py
import diskcache as dc
from pathlib import Path
from typing import Optional

CACHE_DIR = "cache"
VIDEO_DIR = "videos"  # ← Папка с .mp4 файлами
Path(CACHE_DIR).mkdir(exist_ok=True)
Path(VIDEO_DIR).mkdir(exist_ok=True)

cache = dc.Cache(CACHE_DIR)

# === НАСТРОЙКИ ===
DEFAULT_TTL = 7 * 24 * 3600
MAX_TTL = 30 * 24 * 3600
HIGH_USAGE_THRESHOLD = 5
MAX_CACHE_SIZE_GB = 1  # ← ЛИМИТ КЭША
MAX_CACHE_SIZE_BYTES = MAX_CACHE_SIZE_GB * 1024**3

# === Внутренние функции ===
def _get_usage_count(video_id: str) -> int:
    return cache.get(f"usage:{video_id}", 0)

def _increment_usage(video_id: str) -> int:
    key = f"usage:{video_id}"
    current = cache.get(key)
    if current is None:
        cache.set(key, 1)
        return 1
    try:
        cache.incr(key)
        return current + 1
    except Exception:
        # защита на случай нестандартного поведения incr
        new = current + 1
        cache.set(key, new)
        return new

def _calculate_ttl(video_id: str) -> int:
    usage = _get_usage_count(video_id)
    if usage >= HIGH_USAGE_THRESHOLD * 3:
        return MAX_TTL
    elif usage >= HIGH_USAGE_THRESHOLD:
        return DEFAULT_TTL * 2
 
    return DEFAULT_TTL

def _get_cache_size() -> int:
    total = 0
    for key in cache.iterkeys():
        if key.startswith("path:"):
            path = cache.get(key)
            if path and Path(path).exists():
                try:
                    total += Path(path).stat().st_size
                except OSError:
                    pass
    return total

def _evict_least_used(max_bytes: int = MAX_CACHE_SIZE_BYTES):
    """Удаляет редко используемые файлы, пока размер <= лимита"""
    current_size = _get_cache_size()
    if current_size <= max_bytes:
        return

    print(f"[cache] КЭШ ПЕРЕПОЛНЕН: {current_size // 1024**2} МБ > {max_bytes // 1024**2} МБ")
    print(f"[cache] Очистка...")

    # Собираем все video_id с путями и usage
    candidates = []
    for key in cache:
        if key.startswith("path:"):
            video_id = key.split(":", 1)[1]
            filepath = cache.get(key)
            if not filepath or not Path(filepath).exists():
                continue
            usage = _get_usage_count(video_id)
            size = Path(filepath).stat().st_size
            candidates.append((usage, size, video_id, filepath))

    # Сортируем: по частоте (asc), потом по размеру (desc)
    candidates.sort(key=lambda x: (x[0], -x[1]))

    # Удаляем, пока не влезем
    for usage, size, video_id, filepath in candidates:
        if current_size <= max_bytes:
            break
        try:
            Path(filepath).unlink()
            cache.delete(f"path:{video_id}")
            cache.delete(f"usage:{video_id}")
            current_size -= size
            print(f"[cache] УДАЛЕНО: {Path(filepath).name} ({size // 1024**2} МБ, usage: {usage})")
        except Exception as e:
            print(f"[cache] Ошибка удаления {filepath}: {e}")

    print(f"[cache] Размер после очистки: {current_size // 1024**2} МБ")

# === Публичные функции ===
def get_cached_filepath(video_id: str) -> Optional[str]:
    filepath = cache.get(f"path:{video_id}")
    if filepath and Path(filepath).exists():
        _increment_usage(video_id)
        ttl = _calculate_ttl(video_id)
        cache.set(f"path:{video_id}", filepath, expire=ttl)
        print(f"[cache] ХИТ: {filepath} (usage: {_get_usage_count(video_id)})")
        return filepath
    if filepath:
        cache.delete(f"path:{video_id}")
        cache.delete(f"usage:{video_id}")
    return None

def set_cached_filepath(video_id: str, filepath: str):
    # если файл уже был — сохранить старое usage
    usage = cache.get(f"usage:{video_id}") or 0
    usage = usage or 1
    cache.set(f"usage:{video_id}", usage)
    ttl = _calculate_ttl(video_id)
    cache.set(f"path:{video_id}", filepath, expire=ttl)
    print(...)
    _evict_least_used()


def clear_expired():
    removed = cache.expire()
    if removed:
        print(f"[cache] Удалено по TTL: {removed} записей")