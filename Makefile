.PHONY: help install migrate run worker test lint clean docker-up docker-down docker-build

help: ## Показать справку по командам
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -r requirements.txt

migrate: ## Выполнить миграции базы данных
	python manage.py migrate

makemigrations: ## Создать миграции
	python manage.py makemigrations

run: ## Запустить Django сервер разработки
	python manage.py runserver

worker: ## Запустить Celery worker
	celery -A config worker --loglevel=info

beat: ## Запустить Celery beat (планировщик задач)
	celery -A config beat --loglevel=info

test: ## Запустить тесты
	python manage.py test

test-coverage: ## Запустить тесты с покрытием кода
	pytest --cov=payouts --cov-report=html

lint: ## Проверить код линтерами
	black --check payouts config
	flake8 payouts config

format: ## Отформатировать код
	black payouts config

shell: ## Открыть Django shell
	python manage.py shell

createsuperuser: ## Создать суперпользователя
	python manage.py createsuperuser

collectstatic: ## Собрать статические файлы
	python manage.py collectstatic --noinput

# Docker команды
docker-up: ## Запустить все сервисы в Docker
	docker-compose up -d

docker-down: ## Остановить все сервисы Docker
	docker-compose down

docker-build: ## Собрать Docker образы
	docker-compose build

docker-logs: ## Показать логи Docker контейнеров
	docker-compose logs -f

docker-restart: ## Перезапустить Docker контейнеры
	docker-compose restart

# Команды для разработки
dev-setup: install migrate createsuperuser ## Полная настройка окружения разработки
	@echo "Окружение разработки настроено!"

clean: ## Очистить временные файлы
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

