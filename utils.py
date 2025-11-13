# utils.py
import httpx
import hashlib
import re
import asyncio

async def get_stable_video_id(url: str) -> str | None:
    """
    Возвращает SHA-256 хеш от финального URL TikTok.
    Работает с ЛЮБЫМИ ссылками: короткими, полными, с www, m, параметрами.
    """
    url = url.strip()

    # Исправленная регулярка: ловит vm., vt., t., www., m. — или ничего
    if re.search(r"https?://(?:vm\.|vt\.|t\.|www\.|m\.)?tiktok\.com", url, re.IGNORECASE):
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
                # HEAD быстрее, чем GET
                resp = await client.head(url)
                url = str(resp.url)  # финальный URL после всех редиректов
        except Exception as e:
            print(f"[utils] Ошибка редиректа: {e}")
            return None

    # Хешируем финальный URL (без GET-параметров — опционально)
    # Убираем query-параметры, чтобы хеш был стабильным
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
    
    video_id = hashlib.sha256(clean_url.encode("utf-8")).hexdigest()
    return video_id


if __name__ == "__main__":
    url = input("Введите ссылку: ")
    video_id = asyncio.run(get_stable_video_id(url))
    print("Хеш-ID:", video_id)