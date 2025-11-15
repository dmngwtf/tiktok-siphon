# Dockerfile (в корне, код в корне)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируй из корня, а не из bot/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Исключаем ненужное через .dockerignore
RUN mkdir -p /app/videos /app/logs

CMD ["python", "bot.py"]