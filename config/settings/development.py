"""
Настройки для окружения разработки.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Дополнительные настройки для разработки
if DEBUG:
    INSTALLED_APPS += ['django_extensions'] if 'django_extensions' in INSTALLED_APPS else []

# CORS настройки для разработки (если нужно)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

