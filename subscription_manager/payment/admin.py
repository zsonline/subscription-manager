# Django imports
from django.contrib import admin

# Application imports
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['period', 'code', 'amount', 'is_paid', 'paid_at']
    search_fields = ['period', 'code', 'amount']
    actions = ['confirm_payments']

    def confirm_payments(self, request, queryset):
        for obj in queryset:
            obj.confirm()
    confirm_payments.short_description = 'Ausgewählte Zahlungen bestätigen'


admin.site.register(Payment, PaymentAdmin)
