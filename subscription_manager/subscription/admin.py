from django.contrib import admin
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

from import_export import resources
from import_export.admin import ExportMixin

from .models import Period, Plan, Subscription
from .tasks import send_expiration_emails


class SubscriptionResource(resources.ModelResource):
    """
    Defines the data resource which can be exported.
    """
    class Meta:
        model = Subscription
        fields = ('first_name', 'last_name', 'address_line', 'additional_address_line', 'postcode', 'town')


class ActiveSubscriptionResource(SubscriptionResource):
    """
    Defines the data resource for active subscriptions which can be exported.
    """
    def export(self, queryset=None, *args, **kwargs):
        """
        Only export active subscriptions.
        """
        if queryset is None:
            queryset = Subscription.objects.filter(is_active=True)

        return super().export(queryset, *args, **kwargs)


class IsActiveListFilter(admin.SimpleListFilter):
    """
    Custom list filter which filters subscription by
    their status
    """
    title = 'Aktiv'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        """
        Filter options
        """
        return (
            ('active', 'Aktiv'),
            ('inactive', 'Inaktiv'),
        )

    def queryset(self, request, queryset):
        """
        Filter queryset based on set filter value.
        """
        if self.value() == 'active':
            queryset = queryset.filter(is_active=True)
        elif self.value() == 'inactive':
            queryset = queryset.filter(is_active=False)
        return queryset


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
            ('unpaid', 'Nicht bezahlt'),
        )

    def queryset(self, request, queryset):
        """
        Filter queryset based on set filter value.
        """
        if self.value() == 'paid':
            queryset = queryset.filter(is_paid=True)
        elif self.value() == 'unpaid':
            queryset = queryset.filter(is_paid=False)
        return queryset


class PeriodInline(admin.StackedInline):
    model = Period
    extra = 0
    readonly_fields = ['payment_link']

    def payment_link(self, period):
        """
        Returns a payment link if a payment exists.
        """
        if period.payment:
            url = reverse('admin:payment_payment_change', args=[period.payment.pk])
            return mark_safe('<a href="{}">{}</a>'.format(url, period.payment))

        return ''
    payment_link.short_description = 'Zahlung'


@admin.register(Subscription)
class SubscriptionAdmin(ExportMixin, admin.ModelAdmin):
    """
    Subscription model admin
    """
    list_display = [
        'account_name_field', 'address_name_field', 'plan', 'is_active_field', 'is_paid_field',
        'start_date_field', 'end_date_field', 'is_canceled_field'
    ]
    list_filter = [IsActiveListFilter, IsPaidListFilter, 'plan']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name', 'first_name', 'last_name', 'address_line',
        'additional_address_line', 'postcode', 'town', 'country'
    ]
    actions = ['send_renewal_notification']
    resource_class = SubscriptionResource
    inlines = [PeriodInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('user')

    def account_name_field(self, obj):
        return obj.user.full_name()
    account_name_field.short_description = 'Name (Account)'

    def address_name_field(self, obj):
        return obj.full_name()
    address_name_field.short_description = 'Name (Adresse)'

    def is_canceled_field(self, obj):
        return obj.is_canceled
    is_canceled_field.short_description = 'Gekündigt'
    is_canceled_field.admin_order_field = 'is_canceled'
    is_canceled_field.boolean = True

    def is_active_field(self, obj):
        return obj.is_active
    is_active_field.short_description = 'Ist aktiv'
    is_active_field.admin_order_field = 'is_active'
    is_active_field.boolean = True

    def is_paid_field(self, obj):
        return obj.is_paid
    is_paid_field.short_description = 'Ist bezahlt'
    is_paid_field.admin_order_field = 'is_paid'
    is_paid_field.boolean = True

    def start_date_field(self, obj):
        return obj.start_date
    start_date_field.short_description = 'Anfangsdatum'
    start_date_field.admin_order_field = 'start_date'

    def end_date_field(self, obj):
        return obj.end_date
    end_date_field.short_description = 'Enddatum'
    end_date_field.admin_order_field = 'end_date'

    def send_renewal_notification(self, request, queryset):
        send_expiration_emails(queryset=queryset)
    send_renewal_notification.short_description = 'Verlängerungserinnerung senden'


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """
    Plan model admin
    """
    list_display = ['name', 'price']
