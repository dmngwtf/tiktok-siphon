from urllib.parse import unquote
from glob import glob
from typing import Optional, Tuple
from pathlib import Path
ALLOWED_EXT = (".mp4", ".webm", ".mov")

def parse_hash(data: str) -> Optional[str]:
    try:
        return unquote(data.split(":", 1)[1])
    except Exception:
        return None

def find_video_by_hash(video_dir: Path, file_hash: str) -> Optional[Path]:
    pattern = str(video_dir / f"*{file_hash}*")
    for fp in glob(pattern):
        p = Path(fp)
        if p.is_file() and p.suffix.lower() in ALLOWED_EXT:
            return p
    return None

def format_track_text(track: Optional[Tuple[Optional[str], Optional[str], Optional[str]]]) -> str:
    if not track:
        return "Музыка не распознана."
    artist, title, album = track
    artist = (artist or "Неизвестно").strip()
    title = (title or "Без названия").strip()
    album = (album or "—").strip()
    return (
        "**Найдено!**\n\n"
        f"**Исполнитель:** `{artist}`\n"
        f"**Трек:** `{title}`\n"
        f"**Альбом:** `{album}`"
    )
