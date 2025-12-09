"""
Кастомные валидаторы для приложения payouts.
"""
import re
from rest_framework import serializers

# ISO 4217 коды валют (основные)
VALID_CURRENCIES = {
    'USD', 'EUR', 'RUB', 'GBP', 'JPY', 'CNY', 'CHF', 'CAD', 'AUD', 'NZD',
    'BRL', 'INR', 'KRW', 'MXN', 'SGD', 'HKD', 'NOK', 'SEK', 'DKK', 'PLN',
    'TRY', 'ZAR', 'THB', 'MYR', 'IDR', 'PHP', 'CZK', 'HUF', 'ILS', 'CLP',
}


def validate_currency(value):
    """
    Валидация кода валюты.
    
    Проверяет, что код валюты соответствует ISO 4217 стандарту
    и находится в списке поддерживаемых валют.
    
    Args:
        value: код валюты (строка из 3 символов)
    
    Raises:
        serializers.ValidationError: если валюта невалидна
    """
    if not value:
        raise serializers.ValidationError('Валюта обязательна для заполнения')
    
    value = value.upper().strip()
    
    if len(value) != 3:
        raise serializers.ValidationError('Код валюты должен состоять из 3 символов')
    
    if not re.match(r'^[A-Z]{3}$', value):
        raise serializers.ValidationError('Код валюты должен содержать только заглавные латинские буквы')
    
    if value not in VALID_CURRENCIES:
        raise serializers.ValidationError(
            f'Валюта {value} не поддерживается. Поддерживаемые валюты: {", ".join(sorted(VALID_CURRENCIES))}'
        )
    
    return value


def validate_recipient_details(value):
    """
    Валидация реквизитов получателя.
    
    Проверяет, что реквизиты представлены в виде словаря (JSON объекта)
    и содержат необходимые поля.
    
    Args:
        value: реквизиты получателя (словарь)
    
    Raises:
        serializers.ValidationError: если реквизиты невалидны
    """
    if not isinstance(value, dict):
        raise serializers.ValidationError('Реквизиты получателя должны быть объектом JSON')
    
    if not value:
        raise serializers.ValidationError('Реквизиты получателя не могут быть пустыми')
    
    # Проверка наличия хотя бы одного обязательного поля
    required_fields = ['account', 'bank', 'name']
    has_required = any(field in value for field in required_fields)
    
    if not has_required:
        raise serializers.ValidationError(
            f'Реквизиты должны содержать хотя бы одно из полей: {", ".join(required_fields)}'
        )
    
    return value

