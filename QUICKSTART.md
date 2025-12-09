# Быстрый старт проекта

## Запуск через Docker (1 команда)

```bash
docker-compose up --build
```

Готово! Проект доступен по адресу: http://localhost:8000

## Что происходит при запуске:

1. Собираются Docker образы
2. Запускается PostgreSQL (порт 5432)
3. Запускается Redis (порт 6379)
4. Автоматически выполняются миграции БД
5. Запускается Django сервер (порт 8000)
6. Запускается Celery worker

## Полезные команды:

```bash
# Остановка всех сервисов
docker-compose down

# Просмотр логов
docker-compose logs -f

# Пересборка после изменений
docker-compose up --build

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Запуск тестов
docker-compose exec web python manage.py test
```

## Доступные URL:

- **API**: http://localhost:8000/api/payouts/
- **Swagger документация**: http://localhost:8000/api/docs/
- **ReDoc документация**: http://localhost:8000/api/redoc/
- **Админ панель**: http://localhost:8000/admin/

## Пример создания заявки:

```bash
curl -X POST http://localhost:8000/api/payouts/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "1000.00",
    "currency": "USD",
    "recipient_details": {
      "account": "1234567890",
      "bank": "Test Bank",
      "name": "John Doe"
    },
    "description": "Test payout"
  }'
```

