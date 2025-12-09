"""
Модели для приложения payouts.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class PayoutRequest(models.Model):
    """
    Модель заявки на выплату средств.
    
    Поля:
    - amount: сумма выплаты (должна быть положительной)
    - currency: валюта (ISO 4217 код)
    - recipient_details: реквизиты получателя (JSON)
    - status: статус заявки
    - description: опциональное описание
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    class Status(models.TextChoices):
        """Статусы заявки на выплату."""
        PENDING = 'PENDING', 'Ожидает обработки'
        PROCESSING = 'PROCESSING', 'В обработке'
        COMPLETED = 'COMPLETED', 'Завершена'
        FAILED = 'FAILED', 'Ошибка'
    
    id = models.AutoField(primary_key=True)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сумма выплаты',
        help_text='Сумма должна быть положительной'
    )
    currency = models.CharField(
        max_length=3,
        verbose_name='Валюта',
        help_text='ISO 4217 код валюты (USD, EUR, RUB и т.д.)'
    )
    recipient_details = models.JSONField(
        verbose_name='Реквизиты получателя',
        help_text='JSON объект с реквизитами получателя'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус заявки'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Опциональное описание или комментарий'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Заявка на выплату'
        verbose_name_plural = 'Заявки на выплату'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """Строковое представление объекта."""
        return f'Заявка #{self.id} - {self.amount} {self.currency} ({self.status})'

