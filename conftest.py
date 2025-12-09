"""
Конфигурация pytest для проекта.
"""
import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    """Настройка базы данных для тестов."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }

