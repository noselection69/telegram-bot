FROM python:3.11-slim

# Установи рабочую директорию
WORKDIR /app

# Установи системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируй requirements
COPY requirements.txt .

# Установи Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируй весь проект
COPY . .

# Создай директории если их нет
RUN mkdir -p certs logs data

# Ensure data directory has proper permissions
RUN chmod 755 data

# Expose порт
EXPOSE 5000

# Здоровье-проверка
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000', timeout=5)" || exit 1

# Запусти бота
CMD ["python", "-m", "bot.main"]
