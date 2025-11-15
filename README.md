
---

# tiktok-siphon

<p align="center">
  <h2 align="center">Универсальный Telegram-бот для скачивания видео</h2>
  <p align="center">
    <b>TikTok • Instagram Reels • YouTube Shorts</b><br>
    <b>Распознавание музыки • Кэширование • Аналитика • Docker</b>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.12-blue" />
    <img src="https://img.shields.io/badge/aiogram-3.x-green" />
    <img src="https://img.shields.io/badge/PostgreSQL-16-blue" />
    <img src="https://img.shields.io/badge/Docker-%F0%9F%90%B3-blue" />
    <img src="https://img.shields.io/badge/Audio%20Recognition-%F0%9F%8E%B5-orange" />
    <img src="https://img.shields.io/badge/Cache-diskcache-brightgreen" />
  </p>

---

## Возможности

| Функция                           | Описание                                  |
| --------------------------------- | ----------------------------------------- |
| **Скачивание без водяных знаков** | TikTok, Instagram Reels, YouTube Shorts   |
| **Распознавание музыки**          | Кнопка → название трека, артист, ссылка   |
| **Кэширование**                   | Повторные запросы возвращаются мгновенно  |
| **Личная статистика**             | `/stats` — список скачанных видео         |
| **Глобальная аналитика**          | `/all_stats` — общее количество + регионы |
| **Продакшен-готовность**          | Docker + PostgreSQL + конфигурации        |

---

## Стек

```yaml
Language: Python 3.12
Framework: aiogram 3.x (async)
Database: PostgreSQL + SQLAlchemy
Cache: diskcache
Downloader: httpx + TikWM API
Audio Recognition: recognize_mp4() (Shazam/ACRCloud)
Deploy: Docker + docker-compose
```

---

## Быстрый старт

```bash
git clone https://github.com/yourname/tiktok-siphon.git
cd tiktok-siphon
cp .env.example .env
```

---

## Настройка ENV

```env
BOT_TOKEN=your_telegram_bot_token
POSTGRES_DB=tiktok_siphon
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
```

---

## Запуск через Docker

```bash
docker-compose up -d
```

Бот и база подняты.
Логи:

```bash
docker-compose logs -f bot
```


Коротко по каждому файлу/папке — можно вставить в README как “Project Structure”.

---

### **📁 handlers/**

Логика всех хендлеров aiogram.

* **handlers.py** — регистрация всех хендлеров.
* **start_handler.py** — обработка `/start`, приветствие.
* **stat_handler.py** — личная статистика пользователя.
* **all_stat_handler.py** — глобальная статистика по всем скачиваниям.
* **recognize_handler.py** — распознавание музыки по отправленному видео.

---

### **📁 utils/**

Утилиты бота.

* **cache.py** — кэширование скачанных видео (diskcache).
* **downloader.py** — загрузка видео (httpx + TikWM API).
* **logger.py** — настройки логирования.
* **music_finder.py** — распознавание музыки (AUDD.IO).
* **utils.py** — вспомогательные функции.

---

### **📁 db/**

Работа с PostgreSQL.

* инициализация БД, модели, запросы.

---


### **bot.py**

Точка входа. Создание бота, диспетчера, запуск polling.

---


## Telegram-бот для теста

👉 **@ttsave_eb_bot**

---

