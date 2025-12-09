# Payouts API

REST-сервис для управления заявками на выплату средств с асинхронной обработкой через Celery.

## Технологический стек

- **Python 3.11+**
- **Django 4.2+**
- **Django REST Framework**
- **Celery** с Redis в качестве брокера сообщений
- **PostgreSQL** (в Docker контейнере)
- **Docker** и **Docker Compose**

## Возможности

- CRUD операции для заявок на выплату
- Асинхронная обработка заявок через Celery
- Валидация данных (сумма, валюта, реквизиты)
- Документация API (Swagger/Redoc)
- Полное покрытие тестами
- Docker контейнеризация всех сервисов

## Быстрый старт

### Вариант 1: Запуск через Docker (Рекомендуется)

**Предварительные требования:**
- Docker и Docker Compose

**Запуск проекта:**

```bash
# Клонирование репозитория (если используется Git)
git clone <repository-url>
cd test_django_app

# Запуск всех сервисов одной командой
docker-compose up --build
```

Проект автоматически:
- Соберет Docker образы
- Запустит PostgreSQL и Redis
- Выполнит миграции базы данных
- Запустит Django сервер
- Запустит Celery worker

**Важно**: При первом запуске миграции выполняются автоматически через entrypoint скрипт.

После запуска:
- Django приложение доступно по адресу: http://localhost:8000
- API документация (Swagger): http://localhost:8000/api/docs/
- API документация (ReDoc): http://localhost:8000/api/redoc/
- Админ панель: http://localhost:8000/admin/

**Полезные команды:**

```bash
# Запуск в фоновом режиме
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f web
docker-compose logs -f celery

# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes (очистка БД)
docker-compose down -v

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Выполнение команд в контейнере
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py test
```

### Вариант 2: Локальная установка

**Предварительные требования:**
- Python 3.11+
- Docker и Docker Compose (для PostgreSQL и Redis)
- Git

### Установка и запуск

1. **Клонирование репозитория** (если используется Git):
```bash
git clone <repository-url>
cd test_django_app
```

2. **Создание виртуальной среды**:
```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. **Установка зависимостей**:
```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения**:
Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
# Отредактируйте .env файл при необходимости
```

5. **Запуск PostgreSQL и Redis в Docker**:
```bash
docker-compose up -d db redis
```

6. **Выполнение миграций**:
```bash
python manage.py migrate
```

7. **Создание суперпользователя** (опционально):
```bash
python manage.py createsuperuser
```

8. **Запуск Django сервера**:
```bash
python manage.py runserver
```

9. **Запуск Celery worker** (в отдельном терминале):
```bash
celery -A config worker --loglevel=info
```

### Использование Makefile

Для упрощения работы доступны команды через Makefile:

```bash
make install          # Установить зависимости
make migrate          # Выполнить миграции
make run              # Запустить Django сервер
make worker           # Запустить Celery worker
make test             # Запустить тесты
make lint             # Проверить код линтерами
make docker-up        # Запустить все сервисы в Docker
make docker-down      # Остановить все сервисы Docker
```

## API Endpoints

### Заявки на выплату

- `GET /api/payouts/` - Список всех заявок
- `GET /api/payouts/{id}/` - Получение заявки по ID
- `POST /api/payouts/` - Создание новой заявки
- `PATCH /api/payouts/{id}/` - Частичное обновление заявки (статус, описание)
- `DELETE /api/payouts/{id}/` - Удаление заявки

### Пример создания заявки

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

### Статусы заявки

- `PENDING` - Ожидает обработки (по умолчанию)
- `PROCESSING` - В обработке
- `COMPLETED` - Завершена
- `FAILED` - Ошибка

## Тестирование

Запуск всех тестов:
```bash
python manage.py test
```

Или через pytest:
```bash
pytest
```

Запуск тестов с покрытием кода:
```bash
pytest --cov=payouts --cov-report=html
```

## Структура проекта

```
test_django_app/
├── config/                 # Конфигурация Django проекта
│   ├── settings/          # Настройки по окружениям
│   ├── celery.py          # Конфигурация Celery
│   └── urls.py            # Главный URL роутинг
├── payouts/               # Приложение для заявок на выплату
│   ├── models.py          # Модель PayoutRequest
│   ├── serializers.py     # DRF сериализаторы
│   ├── views.py           # API представления
│   ├── tasks.py           # Celery задачи
│   ├── validators.py      # Кастомные валидаторы
│   └── tests/             # Тесты
├── docker-compose.yml      # Docker Compose конфигурация
├── Dockerfile             # Docker образ для Django
├── requirements.txt       # Зависимости Python
├── Makefile              # Команды для управления проектом
└── README.md             # Документация
```

## Деплой в продакшн

### Архитектура деплоя

Проект развертывается в виде микросервисной архитектуры с разделением ответственности:

```
┌─────────────┐
│   Nginx     │ ← Reverse Proxy / Load Balancer
│  (Port 80)  │
└──────┬──────┘
       │
       ├───→ ┌──────────────┐
       │     │   Gunicorn   │ ← Django WSGI Application
       │     │  (Port 8000) │   (Multiple workers)
       │     └──────────────┘
       │
       └───→ ┌──────────────┐
             │   Celery     │ ← Background Task Workers
             │   Workers    │   (Multiple instances)
             └──────┬───────┘
                    │
       ┌────────────┴────────────┐
       │                         │
┌──────▼──────┐         ┌───────▼──────┐
│ PostgreSQL  │         │    Redis     │
│  (Port 5432)│         │  (Port 6379) │
└─────────────┘         └──────────────┘
```

### Необходимые сервисы

Для деплоя в продакшн требуются следующие компоненты:

#### Обязательные сервисы:

1. **PostgreSQL 15+** — основная база данных для хранения заявок
2. **Redis 7+** — брокер сообщений для Celery и хранилище результатов задач
3. **Django Application** (Gunicorn/uWSGI) — веб-сервер для обработки HTTP запросов
4. **Celery Worker** — один или несколько воркеров для асинхронной обработки задач

#### Рекомендуемые сервисы:

5. **Nginx** — reverse proxy для маршрутизации запросов, SSL терминации и раздачи статики
6. **Supervisor/systemd** — управление процессами и автозапуск
7. **Monitoring** (Sentry, Prometheus, Grafana) — мониторинг ошибок и метрик
8. **Backup система** — регулярное резервное копирование БД

### Минимальные шаги по подготовке окружения

#### 1. Подготовка сервера (Ubuntu/Debian)

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python 3.11+
sudo apt install -y python3.11 python3.11-venv python3-pip

# Установка PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Установка Redis
sudo apt install -y redis-server

# Установка Nginx
sudo apt install -y nginx

# Установка системных зависимостей для psycopg2
sudo apt install -y libpq-dev gcc python3-dev
```

#### 2. Настройка базы данных PostgreSQL

```bash
# Переход в PostgreSQL shell
sudo -u postgres psql

# Создание базы данных и пользователя
CREATE DATABASE payouts_db;
CREATE USER payouts_user WITH PASSWORD 'secure_password_here';
ALTER ROLE payouts_user SET client_encoding TO 'utf8';
ALTER ROLE payouts_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE payouts_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE payouts_db TO payouts_user;
\q

# Настройка PostgreSQL для удаленных подключений (если нужно)
sudo nano /etc/postgresql/15/main/postgresql.conf
# Раскомментировать: listen_addresses = 'localhost'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# Добавить: host    payouts_db    payouts_user    127.0.0.1/32    md5

sudo systemctl restart postgresql
```

#### 3. Настройка Redis

```bash
# Проверка статуса Redis
sudo systemctl status redis-server

# Настройка Redis (опционально)
sudo nano /etc/redis/redis.conf
# Установить: maxmemory 256mb
# Установить: maxmemory-policy allkeys-lru

sudo systemctl restart redis-server
```

#### 4. Развертывание приложения

```bash
# Создание пользователя для приложения
sudo useradd -m -s /bin/bash payouts
sudo su - payouts

# Клонирование репозитория
cd /home/payouts
git clone <repository-url> payouts_app
cd payouts_app

# Создание виртуальной среды
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Добавить в requirements.txt для продакшна

# Создание директорий для логов и статики
mkdir -p logs staticfiles media
chmod 755 logs staticfiles media

# Настройка переменных окружения
cp .env.example .env
nano .env  # Настроить продакшн значения
```

**Пример `.env` для продакшна:**
```bash
SECRET_KEY=your-very-secure-secret-key-generate-with-openssl-rand-hex-32
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

DB_NAME=payouts_db
DB_USER=payouts_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### 5. Инициализация базы данных

```bash
# Выполнение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Сбор статических файлов
python manage.py collectstatic --noinput
```

### Запуск Django и Celery в реальной системе

#### Вариант 1: Использование systemd (Рекомендуется)

**Создание systemd сервиса для Django (Gunicorn):**

```bash
sudo nano /etc/systemd/system/payouts-web.service
```

```ini
[Unit]
Description=Payouts Django Web Application
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=notify
User=payouts
Group=payouts
WorkingDirectory=/home/payouts/payouts_app
Environment="PATH=/home/payouts/payouts_app/venv/bin"
EnvironmentFile=/home/payouts/payouts_app/.env
ExecStart=/home/payouts/payouts_app/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --worker-connections 1000 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --bind 127.0.0.1:8000 \
    --access-logfile /home/payouts/payouts_app/logs/gunicorn-access.log \
    --error-logfile /home/payouts/payouts_app/logs/gunicorn-error.log \
    --log-level info \
    config.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Создание systemd сервиса для Celery Worker:**

```bash
sudo nano /etc/systemd/system/payouts-celery.service
```

```ini
[Unit]
Description=Payouts Celery Worker
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=forking
User=payouts
Group=payouts
WorkingDirectory=/home/payouts/payouts_app
Environment="PATH=/home/payouts/payouts_app/venv/bin"
EnvironmentFile=/home/payouts/payouts_app/.env
ExecStart=/home/payouts/payouts_app/venv/bin/celery \
    -A config worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --logfile=/home/payouts/payouts_app/logs/celery-worker.log \
    --pidfile=/home/payouts/payouts_app/celery-worker.pid \
    --detach

ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Активация и запуск сервисов:**

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable payouts-web.service
sudo systemctl enable payouts-celery.service

# Запуск сервисов
sudo systemctl start payouts-web.service
sudo systemctl start payouts-celery.service

# Проверка статуса
sudo systemctl status payouts-web.service
sudo systemctl status payouts-celery.service

# Просмотр логов
sudo journalctl -u payouts-web.service -f
sudo journalctl -u payouts-celery.service -f
```

#### Вариант 2: Использование Supervisor

**Установка Supervisor:**

```bash
sudo apt install -y supervisor
```

**Конфигурация для Django:**

```bash
sudo nano /etc/supervisor/conf.d/payouts-web.conf
```

```ini
[program:payouts-web]
command=/home/payouts/payouts_app/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 4
directory=/home/payouts/payouts_app
user=payouts
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/payouts/payouts_app/logs/gunicorn.log
environment=PATH="/home/payouts/payouts_app/venv/bin"
```

**Конфигурация для Celery:**

```bash
sudo nano /etc/supervisor/conf.d/payouts-celery.conf
```

```ini
[program:payouts-celery]
command=/home/payouts/payouts_app/venv/bin/celery -A config worker --loglevel=info --concurrency=4
directory=/home/payouts/payouts_app
user=payouts
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/payouts/payouts_app/logs/celery.log
environment=PATH="/home/payouts/payouts_app/venv/bin"
```

**Запуск через Supervisor:**

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start payouts-web
sudo supervisorctl start payouts-celery
sudo supervisorctl status
```

#### Настройка Nginx как Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/payouts
```

```nginx
upstream payouts_backend {
    server 127.0.0.1:8000 fail_timeout=0;
    keepalive 32;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Редирект на HTTPS (после настройки SSL)
    # return 301 https://$server_name$request_uri;
    
    client_max_body_size 10M;
    
    # Логирование
    access_log /var/log/nginx/payouts-access.log;
    error_log /var/log/nginx/payouts-error.log;
    
    # Статические файлы
    location /static/ {
        alias /home/payouts/payouts_app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/payouts/payouts_app/media/;
        expires 7d;
    }
    
    # Проксирование запросов к Django
    location / {
        proxy_pass http://payouts_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**Активация конфигурации Nginx:**

```bash
sudo ln -s /etc/nginx/sites-available/payouts /etc/nginx/sites-enabled/
sudo nginx -t  # Проверка конфигурации
sudo systemctl restart nginx
```

#### Настройка SSL (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo systemctl restart nginx
```

### Мониторинг и обслуживание

#### Просмотр логов

```bash
# Логи Django/Gunicorn
tail -f /home/payouts/payouts_app/logs/gunicorn-error.log
tail -f /home/payouts/payouts_app/logs/django.log

# Логи Celery
tail -f /home/payouts/payouts_app/logs/celery-worker.log

# Логи Nginx
sudo tail -f /var/log/nginx/payouts-access.log
sudo tail -f /var/log/nginx/payouts-error.log

# Systemd логи
sudo journalctl -u payouts-web.service -f
sudo journalctl -u payouts-celery.service -f
```

#### Резервное копирование базы данных

```bash
# Создание бэкапа
sudo -u postgres pg_dump payouts_db > /backup/payouts_db_$(date +%Y%m%d_%H%M%S).sql

# Автоматическое резервное копирование (cron)
# Добавить в crontab:
0 2 * * * sudo -u postgres pg_dump payouts_db | gzip > /backup/payouts_db_$(date +\%Y\%m\%d).sql.gz
```

#### Обновление приложения

```bash
cd /home/payouts/payouts_app
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart payouts-web.service
sudo systemctl restart payouts-celery.service
```

### Рекомендации по безопасности

1. **Firewall**: Настроить UFW или firewalld для ограничения доступа
2. **SSL/TLS**: Обязательно использовать HTTPS в продакшне
3. **SECRET_KEY**: Генерировать уникальный ключ для каждого окружения
4. **База данных**: Использовать отдельного пользователя с минимальными правами
5. **Логи**: Настроить ротацию логов (logrotate)
6. **Мониторинг**: Интегрировать Sentry для отслеживания ошибок
7. **Backup**: Настроить автоматическое резервное копирование БД

## Дополнительная информация

- **Документация API**: http://localhost:8000/api/docs/ (Swagger)
- **Админ панель**: http://localhost:8000/admin/
- **Логи**: `logs/django.log`

