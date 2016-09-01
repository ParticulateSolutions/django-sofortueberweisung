from django.contrib import admin

from .models import SofortTransaction


class SofortTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'created_at', 'last_modified', 'status', 'status_reason')
    list_filter = ('status', 'status_reason')
    ordering = ('-created_at',)
    fields = ('transaction_id', 'created_at', 'last_modified', 'status', 'status_reason')

admin.site.register(SofortTransaction, SofortTransactionAdmin)
