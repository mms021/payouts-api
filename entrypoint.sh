#!/bin/bash
set -e

echo "=========================================="
echo "Настройка Django приложения..."
echo "=========================================="

# Ожидание готовности базы данных (только для web сервиса)
if [ -n "$DB_HOST" ] && command -v pg_isready >/dev/null 2>&1; then
    echo "Ожидание готовности базы данных..."
    until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" 2>/dev/null; do
        echo "База данных недоступна - ожидание..."
        sleep 2
    done
    echo "✓ База данных готова!"
fi

# Выполнение миграций (только для web сервиса)
if echo "$@" | grep -q "runserver\|gunicorn\|uwsgi"; then
    echo "Выполнение миграций..."
    python manage.py migrate --noinput
    echo "✓ Миграции выполнены"
    
    # Сбор статических файлов (только для web сервиса)
    echo "Сбор статических файлов..."
    python manage.py collectstatic --noinput || true
    echo "✓ Статические файлы собраны"
fi

echo "=========================================="
echo "Запуск: $@"
echo "=========================================="
exec "$@"

