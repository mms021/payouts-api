"""
Сериализаторы для приложения payouts.
"""
from rest_framework import serializers
from .models import PayoutRequest
from .validators import validate_currency, validate_recipient_details


class PayoutRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели PayoutRequest.
    
    Используется для создания и обновления заявок на выплату.
    Включает валидацию всех полей.
    """
    
    currency = serializers.CharField(
        max_length=3,
        validators=[validate_currency],
        help_text='ISO 4217 код валюты (USD, EUR, RUB и т.д.)'
    )
    recipient_details = serializers.JSONField(
        validators=[validate_recipient_details],
        help_text='JSON объект с реквизитами получателя'
    )
    
    class Meta:
        model = PayoutRequest
        fields = [
            'id',
            'amount',
            'currency',
            'recipient_details',
            'status',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        """
        Валидация суммы выплаты.
        
        Проверяет, что сумма положительна и больше нуля.
        
        Args:
            value: сумма выплаты
        
        Returns:
            Decimal: валидная сумма
        
        Raises:
            serializers.ValidationError: если сумма невалидна
        """
        if value <= 0:
            raise serializers.ValidationError('Сумма выплаты должна быть положительной')
        return value
    
    def validate_description(self, value):
        """
        Валидация описания.
        
        Проверяет длину описания (максимум 1000 символов).
        
        Args:
            value: описание заявки
        
        Returns:
            str: валидное описание
        
        Raises:
            serializers.ValidationError: если описание слишком длинное
        """
        if value and len(value) > 1000:
            raise serializers.ValidationError('Описание не должно превышать 1000 символов')
        return value


class PayoutRequestUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для частичного обновления заявки.
    
    Позволяет обновлять только статус и описание.
    """
    
    class Meta:
        model = PayoutRequest
        fields = ['status', 'description']
    
    def validate_status(self, value):
        """
        Валидация статуса при обновлении.
        
        Проверяет, что статус является допустимым значением.
        
        Args:
            value: новый статус
        
        Returns:
            str: валидный статус
        
        Raises:
            serializers.ValidationError: если статус невалиден
        """
        valid_statuses = [choice[0] for choice in PayoutRequest.Status.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f'Недопустимый статус. Допустимые значения: {", ".join(valid_statuses)}'
            )
        return value

