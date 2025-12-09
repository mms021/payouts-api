FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание директории для логов
RUN mkdir -p logs && \
    touch logs/django.log && \
    chmod 777 logs

# Создание entrypoint скрипта исполняемым
RUN chmod +x entrypoint.sh

# Открытие порта
EXPOSE 8000

# Использование entrypoint для автоматической настройки
ENTRYPOINT ["./entrypoint.sh"]

# Команда по умолчанию (может быть переопределена в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
