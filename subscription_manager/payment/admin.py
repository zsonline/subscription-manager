# Django imports
from django.contrib import admin

# Application imports
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'is_paid', 'paid_at')

admin.site.register(Payment, PaymentAdmin)