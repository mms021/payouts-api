"""
Celery задачи для приложения payouts.
"""
import logging
import time
from celery import shared_task
from django.utils import timezone
from .models import PayoutRequest

logger = logging.getLogger('celery')


@shared_task(name='payouts.process_payout_request')
def process_payout_request(payout_id):
    """
    Асинхронная обработка заявки на выплату.
    
    Имитирует обработку заявки:
    1. Изменяет статус на PROCESSING
    2. Выполняет имитацию обработки (задержка, проверки)
    3. Изменяет статус на COMPLETED или FAILED в зависимости от результата
    
    Args:
        payout_id: идентификатор заявки на выплату
    
    Returns:
        str: сообщение о результате обработки
    """
    try:
        # Получение заявки из базы данных
        payout = PayoutRequest.objects.get(id=payout_id)
        logger.info(f'Начата обработка заявки #{payout_id}')
        
        # Изменение статуса на PROCESSING
        payout.status = PayoutRequest.Status.PROCESSING
        payout.save(update_fields=['status', 'updated_at'])
        logger.info(f'Статус заявки #{payout_id} изменен на PROCESSING')
        
        # Имитация обработки заявки (задержка 2-5 секунд)
        processing_time = 3
        logger.info(f'Имитация обработки заявки #{payout_id} (задержка {processing_time} сек)')
        time.sleep(processing_time)
        
        # Простая проверка валидности данных
        # В реальном проекте здесь были бы проверки баланса, реквизитов и т.д.
        is_valid = (
            payout.amount > 0 and
            payout.currency and
            payout.recipient_details and
            isinstance(payout.recipient_details, dict)
        )
        
        if is_valid:
            # Успешная обработка
            payout.status = PayoutRequest.Status.COMPLETED
            payout.save(update_fields=['status', 'updated_at'])
            logger.info(f'Заявка #{payout_id} успешно обработана. Статус изменен на COMPLETED')
            return f'Заявка #{payout_id} успешно обработана'
        else:
            # Ошибка обработки
            payout.status = PayoutRequest.Status.FAILED
            payout.save(update_fields=['status', 'updated_at'])
            logger.warning(f'Ошибка обработки заявки #{payout_id}. Статус изменен на FAILED')
            return f'Ошибка обработки заявки #{payout_id}: невалидные данные'
    
    except PayoutRequest.DoesNotExist:
        error_msg = f'Заявка #{payout_id} не найдена'
        logger.error(error_msg)
        return error_msg
    
    except Exception as e:
        # Обработка неожиданных ошибок
        error_msg = f'Неожиданная ошибка при обработке заявки #{payout_id}: {str(e)}'
        logger.error(error_msg, exc_info=True)
        
        # Попытка изменить статус на FAILED
        try:
            payout = PayoutRequest.objects.get(id=payout_id)
            payout.status = PayoutRequest.Status.FAILED
            payout.save(update_fields=['status', 'updated_at'])
        except Exception:
            pass
        
        return error_msg

