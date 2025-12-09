from django.contrib import admin
from .models import PayoutRequest


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    """Админ панель для модели PayoutRequest."""
    list_display = ('id', 'amount', 'currency', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('id', 'recipient_details', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

