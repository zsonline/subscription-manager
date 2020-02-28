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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['account_name_field', 'address_name_field', 'amount', 'method', 'code',  'is_paid', 'paid_at']
    search_fields = [
        'amount', 'id', 'period__subscription__last_name', 'period__subscription__user__first_name',
        'period__subscription__user__last_name', 'period__subscription__user__first_name'
    ]
    actions = ['confirm_payments']
    list_filter = [IsPaidListFilter, 'method', 'amount']

    def account_name_field(self, obj):
        return obj.period.subscription.user.full_name()
    account_name_field.short_description = 'Name (Account)'

    def address_name_field(self, obj):
        return obj.period.subscription.full_name()
    address_name_field.short_description = 'Name (Adresse)'

    def confirm_payments(self, request, queryset):
        for obj in queryset:
            obj.confirm()
    confirm_payments.short_description = 'Ausgewählte Zahlungen bestätigen'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('period__subscription__user')
