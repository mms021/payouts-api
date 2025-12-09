"""
Тесты для валидаторов приложения payouts.
"""
from django.test import TestCase
from rest_framework import serializers
from payouts.validators import validate_currency, validate_recipient_details


class CurrencyValidatorTest(TestCase):
    """Тесты для валидатора валюты."""
    
    def test_valid_currency(self):
        """Тест валидной валюты."""
        self.assertEqual(validate_currency('USD'), 'USD')
        self.assertEqual(validate_currency('EUR'), 'EUR')
        self.assertEqual(validate_currency('RUB'), 'RUB')
    
    def test_currency_uppercase(self):
        """Тест преобразования валюты в верхний регистр."""
        self.assertEqual(validate_currency('usd'), 'USD')
        self.assertEqual(validate_currency('eur'), 'EUR')
    
    def test_invalid_currency_length(self):
        """Тест невалидной длины кода валюты."""
        with self.assertRaises(serializers.ValidationError):
            validate_currency('US')
        with self.assertRaises(serializers.ValidationError):
            validate_currency('USDD')
    
    def test_invalid_currency_format(self):
        """Тест невалидного формата кода валюты."""
        with self.assertRaises(serializers.ValidationError):
            validate_currency('US1')
        with self.assertRaises(serializers.ValidationError):
            validate_currency('us-d')
    
    def test_unsupported_currency(self):
        """Тест неподдерживаемой валюты."""
        with self.assertRaises(serializers.ValidationError):
            validate_currency('XYZ')
    
    def test_empty_currency(self):
        """Тест пустой валюты."""
        with self.assertRaises(serializers.ValidationError):
            validate_currency('')


class RecipientDetailsValidatorTest(TestCase):
    """Тесты для валидатора реквизитов получателя."""
    
    def test_valid_recipient_details(self):
        """Тест валидных реквизитов."""
        valid_details = {
            'account': '1234567890',
            'bank': 'Test Bank',
            'name': 'John Doe'
        }
        self.assertEqual(validate_recipient_details(valid_details), valid_details)
    
    def test_recipient_details_with_account(self):
        """Тест реквизитов только с полем account."""
        details = {'account': '1234567890'}
        self.assertEqual(validate_recipient_details(details), details)
    
    def test_recipient_details_with_bank(self):
        """Тест реквизитов только с полем bank."""
        details = {'bank': 'Test Bank'}
        self.assertEqual(validate_recipient_details(details), details)
    
    def test_recipient_details_with_name(self):
        """Тест реквизитов только с полем name."""
        details = {'name': 'John Doe'}
        self.assertEqual(validate_recipient_details(details), details)
    
    def test_empty_recipient_details(self):
        """Тест пустых реквизитов."""
        with self.assertRaises(serializers.ValidationError):
            validate_recipient_details({})
    
    def test_invalid_recipient_details_type(self):
        """Тест невалидного типа реквизитов."""
        with self.assertRaises(serializers.ValidationError):
            validate_recipient_details('not a dict')
        with self.assertRaises(serializers.ValidationError):
            validate_recipient_details([])

