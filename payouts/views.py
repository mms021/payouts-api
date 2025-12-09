"""
Представления (Views) для приложения payouts.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import PayoutRequest
from .serializers import PayoutRequestSerializer, PayoutRequestUpdateSerializer
from .tasks import process_payout_request

logger = logging.getLogger('payouts')


class PayoutRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления заявками на выплату.
    
    Предоставляет CRUD операции:
    - GET /api/payouts/ - список заявок
    - GET /api/payouts/{id}/ - получение заявки по ID
    - POST /api/payouts/ - создание новой заявки
    - PATCH /api/payouts/{id}/ - частичное обновление заявки
    - DELETE /api/payouts/{id}/ - удаление заявки
    """
    queryset = PayoutRequest.objects.all()
    permission_classes = [AllowAny]  # Для тестового проекта разрешаем всем
    
    def get_serializer_class(self):
        """
        Возвращает класс сериализатора в зависимости от действия.
        
        Returns:
            Serializer: класс сериализатора
        """
        if self.action in ['update', 'partial_update']:
            return PayoutRequestUpdateSerializer
        return PayoutRequestSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Создание новой заявки на выплату.
        
        После успешного создания запускает Celery задачу для обработки заявки.
        
        Args:
            request: HTTP запрос с данными заявки
        
        Returns:
            Response: ответ с данными созданной заявки и статусом 201
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Создание заявки
        payout_request = serializer.save()
        logger.info(f'Создана заявка #{payout_request.id} на сумму {payout_request.amount} {payout_request.currency}')
        
        # Запуск Celery задачи для обработки заявки
        try:
            process_payout_request.delay(payout_request.id)
            logger.info(f'Запущена Celery задача для обработки заявки #{payout_request.id}')
        except Exception as e:
            logger.error(f'Ошибка при запуске Celery задачи для заявки #{payout_request.id}: {e}')
            # Не прерываем создание заявки, даже если задача не запустилась
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        Полное обновление заявки.
        
        В данном проекте используется только для обновления статуса.
        
        Args:
            request: HTTP запрос с данными для обновления
        
        Returns:
            Response: ответ с обновленными данными заявки
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)
        logger.info(f'Обновлена заявка #{instance.id}: статус изменен на {instance.status}')
        
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление заявки (PATCH).
        
        Позволяет обновить только статус или описание.
        
        Args:
            request: HTTP запрос с данными для частичного обновления
        
        Returns:
            Response: ответ с обновленными данными заявки
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Удаление заявки.
        
        Args:
            request: HTTP запрос
        
        Returns:
            Response: ответ со статусом 204 (No Content)
        """
        instance = self.get_object()
        payout_id = instance.id
        self.perform_destroy(instance)
        logger.info(f'Удалена заявка #{payout_id}')
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def list(self, request, *args, **kwargs):
        """
        Получение списка заявок с пагинацией.
        
        Args:
            request: HTTP запрос
        
        Returns:
            Response: ответ со списком заявок
        """
        response = super().list(request, *args, **kwargs)
        logger.debug(f'Получен список заявок: {len(response.data.get("results", []))} записей')
        return response
    
    def retrieve(self, request, *args, **kwargs):
        """
        Получение заявки по ID.
        
        Args:
            request: HTTP запрос
        
        Returns:
            Response: ответ с данными заявки
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.debug(f'Получена заявка #{instance.id}')
        return Response(serializer.data)

