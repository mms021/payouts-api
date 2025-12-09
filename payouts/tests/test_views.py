"""
Тесты для API представлений приложения payouts.
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from payouts.models import PayoutRequest


class PayoutRequestAPITest(APITestCase):
    """Тесты для API endpoints заявок на выплату."""
    
    def setUp(self):
        """Подготовка данных для тестов."""
        self.url_list = reverse('payout-list')
        self.valid_data = {
            'amount': '1000.00',
            'currency': 'USD',
            'recipient_details': {
                'account': '1234567890',
                'bank': 'Test Bank',
                'name': 'John Doe'
            },
            'description': 'Test payout request'
        }
    
    def test_create_payout_request(self):
        """Тест успешного создания заявки."""
        with patch('payouts.views.process_payout_request.delay') as mock_task:
            response = self.client.post(self.url_list, self.valid_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn('id', response.data)
            self.assertEqual(response.data['amount'], '1000.00')
            self.assertEqual(response.data['currency'], 'USD')
            self.assertEqual(response.data['status'], 'PENDING')
            
            # Проверка, что Celery задача была вызвана
            mock_task.assert_called_once()
            payout_id = response.data['id']
            mock_task.assert_called_with(payout_id)
    
    def test_create_payout_request_triggers_celery_task(self):
        """Тест проверки вызова Celery-задачи при создании."""
        with patch('payouts.views.process_payout_request.delay') as mock_task:
            response = self.client.post(self.url_list, self.valid_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # Проверка, что задача была вызвана ровно один раз
            self.assertEqual(mock_task.call_count, 1)
            # Проверка, что задача была вызвана с правильным ID заявки
            payout_id = response.data['id']
            mock_task.assert_called_with(payout_id)
    
    def test_get_payout_list(self):
        """Тест получения списка заявок."""
        # Создание тестовых заявок
        PayoutRequest.objects.create(
            amount=1000.00,
            currency='USD',
            recipient_details={'account': '123', 'bank': 'Bank', 'name': 'Name'}
        )
        PayoutRequest.objects.create(
            amount=2000.00,
            currency='EUR',
            recipient_details={'account': '456', 'bank': 'Bank', 'name': 'Name'}
        )
        
        response = self.client.get(self.url_list)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_payout_detail(self):
        """Тест получения заявки по ID."""
        payout = PayoutRequest.objects.create(
            amount=1000.00,
            currency='USD',
            recipient_details={'account': '123', 'bank': 'Bank', 'name': 'Name'}
        )
        
        url = reverse('payout-detail', kwargs={'pk': payout.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], payout.id)
        self.assertEqual(response.data['amount'], '1000.00')
    
    def test_update_payout_status(self):
        """Тест обновления статуса заявки."""
        payout = PayoutRequest.objects.create(
            amount=1000.00,
            currency='USD',
            recipient_details={'account': '123', 'bank': 'Bank', 'name': 'Name'}
        )
        
        url = reverse('payout-detail', kwargs={'pk': payout.id})
        update_data = {'status': 'PROCESSING'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payout.refresh_from_db()
        self.assertEqual(payout.status, 'PROCESSING')
    
    def test_delete_payout(self):
        """Тест удаления заявки."""
        payout = PayoutRequest.objects.create(
            amount=1000.00,
            currency='USD',
            recipient_details={'account': '123', 'bank': 'Bank', 'name': 'Name'}
        )
        
        url = reverse('payout-detail', kwargs={'pk': payout.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PayoutRequest.objects.filter(id=payout.id).exists())
    
    def test_create_payout_invalid_amount(self):
        """Тест создания заявки с невалидной суммой."""
        invalid_data = self.valid_data.copy()
        invalid_data['amount'] = '-100.00'
        
        response = self.client.post(self.url_list, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_payout_invalid_currency(self):
        """Тест создания заявки с невалидной валютой."""
        invalid_data = self.valid_data.copy()
        invalid_data['currency'] = 'XXX'
        
        response = self.client.post(self.url_list, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_payout_invalid_recipient_details(self):
        """Тест создания заявки с невалидными реквизитами."""
        invalid_data = self.valid_data.copy()
        invalid_data['recipient_details'] = {}
        
        response = self.client.post(self.url_list, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

