"""
Настройки для продакшн окружения.
"""
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Безопасность для продакшна
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Статические файлы через WhiteNoise (если используется)
# INSTALLED_APPS += ['whitenoise.middleware.WhiteNoiseMiddleware']

