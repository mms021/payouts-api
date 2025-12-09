from django.apps import AppConfig


class PayoutsConfig(AppConfig):
    """Конфигурация приложения payouts."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payouts'
    verbose_name = 'Заявки на выплату'

