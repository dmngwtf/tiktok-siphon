import os
import subprocess
import requests
import logging
from dotenv import load_dotenv
from typing import Tuple, Optional
from pathlib import Path
from utils.logger import logger


#Инициализируем логгер
logger = logging.getLogger(__name__)
# Загружаем .env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv()


def recognize_mp4(
    file_path: str,
    start_sec: int = 0,
    duration: int = 10
) -> Tuple[Optional[str], Optional[str], Optional[str]]:

    API_TOKEN = os.getenv("AUDDIO_TOKEN")
    if not API_TOKEN:
        raise ValueError("AUDD_API_TOKEN не найден в .env файле!")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    if not file_path.lower().endswith(".mp4"):
        raise ValueError("Файл должен быть .mp4")

    temp_wav = "temp_recognize.wav"

    logger.info(f"Обрабатываю файл: {os.path.basename(file_path)}")

    # === ffmpeg ===
    cmd = [
        "ffmpeg", "-y",
        "-i", file_path,
        "-ss", str(start_sec),
        "-t", str(duration),
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "44100", "-ac", "2",
        "-af", "loudnorm=I=-16",
        temp_wav
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.error(f"ffmpeg ошибка: {e}")
        return (None, None, None)

    if not os.path.exists(temp_wav) or os.path.getsize(temp_wav) < 100 * 1024:
        logger.warning("Слишком маленький wav (тишина?)")
        try:
            os.remove(temp_wav)
        except:
            pass
        return (None, None, None)

    # === AUDD ===
    logger.info("Отправка в AUDD")

    try:
        with open(temp_wav, "rb") as f:
            files = {"file": f}
            data = {
                "api_token": API_TOKEN,
                "return": "apple_music,spotify"
            }
            response = requests.post(
                "https://api.audd.io/",
                data=data,
                files=files,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
    except Exception as e:
        logger.error(f"Сетевая ошибка: {e}")
        try:
            os.remove(temp_wav)
        except:
            pass
        return (None, None, None)

    # === Разбор ответа ===
    try:
        os.remove(temp_wav)
    except:
        pass

    if result.get("status") == "success" and result.get("result"):
        r = result["result"]
        artist = r.get("artist")
        title = r.get("title")
        album = r.get("album") or "—"

        logger.info(f"Найдено: {artist} — {title}")
        return (artist, title, album)

    error = result.get("error", {}).get("error_message", "Неизвестно")
    logger.warning(f"Не распознано: {error}")
    return (None, None, None)
