from django.contrib import admin

from .models import Payment


class IsPaidListFilter(admin.SimpleListFilter):
    """
    Custom list filter which filters subscription by
    their status
    """
    title = 'Bezahlt'
    parameter_name = 'is_paid'

    def lookups(self, request, model_admin):
        """
        Filter options
        """
        return (
            ('paid', 'Bezahlt'),
            ('not_paid', 'Nicht bezahlt'),
        )

    def queryset(self, request, queryset):
        """
        Filter queryset based on set filter value.
        """
        if self.value() == 'paid':
            return queryset.filter(paid_at__isnull=False)

        if self.value() == 'not_paid':
            return queryset.filter(paid_at__isnull=True)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['period', 'amount', 'method', 'code',  'is_paid', 'paid_at']
    search_fields = ['code', 'amount', 'subscription__first_name', 'subscription__last_name', 'subscription__user__first_name', 'subscription__user__last_name']
    actions = ['confirm_payments']
    list_filter = [IsPaidListFilter, 'method', 'amount']

    def confirm_payments(self, request, queryset):
        for obj in queryset:
            obj.confirm()
    confirm_payments.short_description = 'Ausgewählte Zahlungen bestätigen'


admin.site.register(Payment, PaymentAdmin)
