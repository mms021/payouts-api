"""
Тесты для моделей приложения payouts.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from payouts.models import PayoutRequest


class PayoutRequestModelTest(TestCase):
    """Тесты для модели PayoutRequest."""
    
    def setUp(self):
        """Подготовка данных для тестов."""
        self.valid_data = {
            'amount': 1000.00,
            'currency': 'USD',
            'recipient_details': {
                'account': '1234567890',
                'bank': 'Test Bank',
                'name': 'John Doe'
            },
            'description': 'Test payout request'
        }
    
    def test_create_payout_request(self):
        """Тест создания заявки на выплату."""
        payout = PayoutRequest.objects.create(**self.valid_data)
        
        self.assertIsNotNone(payout.id)
        self.assertEqual(payout.amount, 1000.00)
        self.assertEqual(payout.currency, 'USD')
        self.assertEqual(payout.status, PayoutRequest.Status.PENDING)
        self.assertIsNotNone(payout.created_at)
        self.assertIsNotNone(payout.updated_at)
    
    def test_payout_request_str(self):
        """Тест строкового представления заявки."""
        payout = PayoutRequest.objects.create(**self.valid_data)
        # Проверяем, что строковое представление содержит основные элементы
        str_repr = str(payout)
        self.assertIn(f'Заявка #{payout.id}', str_repr)
        self.assertIn('USD', str_repr)
        self.assertIn('PENDING', str_repr)
    
    def test_default_status(self):
        """Тест статуса по умолчанию."""
        payout = PayoutRequest.objects.create(**self.valid_data)
        self.assertEqual(payout.status, PayoutRequest.Status.PENDING)
    
    def test_status_choices(self):
        """Тест доступных статусов."""
        payout = PayoutRequest.objects.create(**self.valid_data)
        
        # Проверка всех доступных статусов
        statuses = [choice[0] for choice in PayoutRequest.Status.choices]
        self.assertIn('PENDING', statuses)
        self.assertIn('PROCESSING', statuses)
        self.assertIn('COMPLETED', statuses)
        self.assertIn('FAILED', statuses)
    
    def test_ordering(self):
        """Тест сортировки заявок."""
        payout1 = PayoutRequest.objects.create(**self.valid_data)
        payout2 = PayoutRequest.objects.create(**self.valid_data)
        
        payouts = list(PayoutRequest.objects.all())
        # Должны быть отсортированы по дате создания (новые первые)
        self.assertEqual(payouts[0].id, payout2.id)
        self.assertEqual(payouts[1].id, payout1.id)
    
    def test_min_amount_validation(self):
        """Тест валидации минимальной суммы."""
        # Создание заявки с нулевой суммой должно вызвать ошибку
        invalid_data = self.valid_data.copy()
        invalid_data['amount'] = 0
        
        with self.assertRaises(ValidationError):
            payout = PayoutRequest(**invalid_data)
            payout.full_clean()

