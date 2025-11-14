import logging
from pathlib import Path

LOG_FILE = Path("logs") / "bot.log"
LOG_FILE.parent.mkdir(exist_ok=True)

logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

# Очищаем предыдущие handlers
logger.handlers = []

# Консоль
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s — %(message)s"))
logger.addHandler(ch)

# Файл
fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s — %(message)s"))
logger.addHandler(fh)

logger.propagate = False

# Проверка
logger.info(f"Logger initialized. Logs will be written to {LOG_FILE.resolve()}")
